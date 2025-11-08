# ... existing code ...
@app.route('/')
def index():
# ... existing code ...
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
# ... existing code ...
        'error': f'처리 중 오류가 발생했습니다: {str(e)}'
    })


# --- 키워드 스캐너 라우트 추가 ---

@app.route('/scanner')
def scanner_index():
    """키워드 스캐너 - 스캔 결과 페이지"""
    # TODO: 실제 데이터 로직 추가 필요
    # 우선 빈 리스트로 템플릿을 렌더링합니다.
    return render_template('index_scan.html', results=[])

@app.route('/scanner/manage')
def scanner_manage():
    """키워드 스캐너 - 관리 페이지"""
    # TODO: 실제 데이터 로직 추가 필요
    # 우선 빈 리스트로 템플릿을 렌더링합니다.
    return render_template('manage.html', stats=[], blog_stats=[], blogs=[], keywords=[])

# --- ---------------------- ---


if __name__ == '__main__':
# ... existing code ...
