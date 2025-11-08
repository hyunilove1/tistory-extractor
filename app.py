#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 블로그 인기글 추출 웹 애플리케이션
"""

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

class TistoryPopularPostsExtractor:
    def __init__(self, blog_url):
        self.blog_url = blog_url.rstrip('/')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def validate_url(self):
        """URL이 유효한 티스토리 주소인지 확인"""
        parsed = urlparse(self.blog_url)
        if 'tistory.com' not in parsed.netloc:
            raise ValueError("유효한 티스토리 블로그 주소가 아닙니다.")
        return True
    
    def fetch_page(self):
        """블로그 페이지 가져오기"""
        try:
            response = requests.get(self.blog_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"페이지 가져오기 실패: {str(e)}")
    
    def extract_popular_posts(self, html):
        """인기글 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        popular_posts = []
        
        # 티스토리 인기글 섹션 찾기
        popular_sections = []
        popular_sections.extend(soup.find_all(class_=re.compile('popular', re.I)))
        popular_sections.extend(soup.find_all(id=re.compile('popular', re.I)))
        
        # "인기글", "인기 글" 텍스트를 포함한 헤더 찾기
        for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'span']):
            if header.get_text() and re.search(r'인기\s*글', header.get_text()):
                parent = header.find_parent(['div', 'section', 'aside'])
                if parent:
                    popular_sections.append(parent)
        
        # 인기글 링크 추출
        seen_urls = set()
        for section in popular_sections:
            links = section.find_all('a', href=True)
            for link in links:
                url = link.get('href', '')
                title = link.get_text(strip=True)
                
                # 상대 URL을 절대 URL로 변환
                if url and not url.startswith('http'):
                    url = urljoin(self.blog_url, url)
                
                # 유효한 포스트 링크만 추가
                if url and title and url not in seen_urls and '/m/' not in url:
                    if re.search(r'/\d+', url) or 'entry' in url:
                        popular_posts.append({
                            'title': title,
                            'url': url
                        })
                        seen_urls.add(url)
        
        # 명시적인 인기글이 없는 경우
        if not popular_posts:
            all_links = soup.find_all('a', href=re.compile(r'/\d+'))
            for link in all_links[:20]:
                url = link.get('href', '')
                title = link.get_text(strip=True)
                
                if url and not url.startswith('http'):
                    url = urljoin(self.blog_url, url)
                
                if url and title and url not in seen_urls and len(title) > 5:
                    popular_posts.append({
                        'title': title,
                        'url': url
                    })
                    seen_urls.add(url)
        
        return popular_posts
    
    def get_popular_posts(self):
        """인기글 가져오기"""
        self.validate_url()
        html = self.fetch_page()
        popular_posts = self.extract_popular_posts(html)
        return popular_posts


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    """인기글 추출 API"""
    try:
        data = request.get_json()
        blog_urls_input = data.get('blog_urls', '').strip()
        
        if not blog_urls_input:
            return jsonify({
                'success': False,
                'error': '블로그 주소를 입력해주세요.'
            })
        
        # 여러 줄로 입력된 URL을 분리
        blog_urls = [url.strip() for url in blog_urls_input.split('\n') if url.strip()]
        
        if not blog_urls:
            return jsonify({
                'success': False,
                'error': '유효한 블로그 주소를 입력해주세요.'
            })
        
        results = []
        
        # 각 블로그별로 인기글 추출
        for blog_url in blog_urls:
            # http:// 또는 https://가 없으면 추가
            if not blog_url.startswith('http'):
                blog_url = 'https://' + blog_url
            
            try:
                # 인기글 추출
                extractor = TistoryPopularPostsExtractor(blog_url)
                popular_posts = extractor.get_popular_posts()
                
                results.append({
                    'success': True,
                    'blog_url': blog_url,
                    'posts': popular_posts,
                    'count': len(popular_posts)
                })
            
            except ValueError as e:
                results.append({
                    'success': False,
                    'blog_url': blog_url,
                    'error': str(e),
                    'posts': [],
                    'count': 0
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'blog_url': blog_url,
                    'error': f'오류가 발생했습니다: {str(e)}',
                    'posts': [],
                    'count': 0
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_blogs': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        })


if __name__ == '__main__':
    print("=" * 60)
    print("티스토리 블로그 인기글 추출 웹 애플리케이션")
    print("=" * 60)
    print("\n브라우저에서 http://localhost:5000 으로 접속하세요.\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
