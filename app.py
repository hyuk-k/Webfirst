import pymysql
import pandas as pd
from flask import Flask, request, render_template, send_file, jsonify
from flask import jsonify

# Flask 애플리케이션 설정
app = Flask(__name__, static_folder='static')

def get_mysql_data(query):
    # MySQL 연결 설정
    connection = pymysql.connect(host='localhost', user='root', password='0928', db='test01', charset='utf8')
    
    try:
        # SQL 쿼리 실행
        df = pd.read_sql(query, connection)
        return df.to_dict(orient='records')
    finally:
        # 연결 종료
        connection.close()
 
@app.route('/')
def index():

    # 'intro' 페이지의 내용을 변수에 저장합니다.
    intro_content = {
        'title': '경기도자율주행센터',
        'description': '경기도자율주행센터는 최첨단 자율주행 기술 개발과 시험을 위한 허브입니다.',
        'vision': '안전하고 효율적인 교통 시스템을 통해 삶의 질을 향상시키는 것이 우리의 비전입니다.',
        'research': '우리 센터는 자율주행 기술의 연구 및 개발에 중점을 두고 있습니다.',
        'partnership': '우리는 다양한 산업 분야의 기업 및 연구 기관과 협력합니다.'
    }

    return render_template('index.html', intro=intro_content)

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/api-results')
def api_results():
    query = "SELECT * FROM api01"
    data = get_mysql_data(query)
    return jsonify(data)  # 데이터를 JSON 형식으로 반환

@app.route('/crawling-results')
def crawling_results():
    query = "SELECT * FROM crwaling02"
    data = get_mysql_data(query)
    return jsonify(data)  # 데이터를 JSON 형식으로 반환

@app.route('/api-results-detail')
def api_results_detail():
    query = "SELECT * FROM api01"
    data = get_mysql_data(query)
    return jsonify(data)

@app.route('/crawling-results-detail')
def crawling_results_detail():
    query = "SELECT * FROM crwaling02"
    data = get_mysql_data(query)
    return jsonify(data)

@app.route('/api-check-status')
def api_check_status():
    # 클라이언트로부터 날짜 매개변수 받기
    date = request.args.get('date')
    
    # 매개변수가 없는 경우 기본값 설정 (예: 오늘 날짜)
    if not date:
        date = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # 해당 날짜의 데이터 점검 결과를 조회하는 SQL 쿼리
    query = f"SELECT * FROM check_status WHERE check_date = '{date}'"
    data = get_mysql_data(query)
    
    # 데이터가 없는 경우 오류 메시지 반환
    if not data:
        return jsonify({'error': 'No data found for the specified date'}), 404
    
    return jsonify(data)  # 데이터를 JSON 형식으로 반환

if __name__ == '__main__':
    app.run(debug=True)
