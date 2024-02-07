import requests
import pymysql
import datetime

# 데이터베이스 연결 정보
username = 'root'
password = '0928'
host = 'localhost'
dbname = 'test01'
table_name = 'api01'

# MySQL에 데이터 삽입하는 함수
def insert_data_to_mysql(data, connection):
    with connection.cursor() as cursor:
        sql = f"INSERT INTO {table_name} (service_name, status, check_time) VALUES (%s, %s, %s)"
        cursor.execute(sql, data)

    connection.commit()

# API 요청 및 결과 처리 함수
def getRequest(serviceName, url, params):
    try:
        response = requests.get(url, params=params, timeout=100)
        check_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 'numOfRows' in response.text:
            result = (serviceName, '정상', check_time)
        else:
            result = (serviceName, '오류 - 점검 필요', check_time)
        
        # MySQL 데이터베이스에 결과 삽입
        connection = pymysql.connect(host=host, user=username, password=password, db=dbname, charset='utf8')
        insert_data_to_mysql(result, connection)
        connection.close()

        return f"{serviceName}: 결과 처리 및 적재 완료"

    except Exception as e:
        return f"{serviceName}: 오류 - {str(e)}"

# 각 서비스 API 점검 및 결과 저장 함수
def getService():
    # 서비스 이름, URL, 파라미터 등을 정의
    global results
    results = ""
    d = datetime.datetime.now()
    results += f"{d.year}년 {d.month}월 {d.day}일 {d.hour}시 {d.minute}분 {d.second}초  공공데이터 포털 Open API 점검사항\n"
    results += "=====================================================================\n"


    # 각 서비스 요청 후 결과 문자열에 추가
    serviceNames = [
        '판교제로시티 CCTV 데이터 2D 바운딩박스 조회',
        '판교제로시티 CCTV 데이터 2D 세그멘테이션 조회',
        '판교제로시티 CCTV 데이터 제로셔틀 경로추적 조회',
        '제로셔틀 차량 센서데이터(라이다)조회',
        '데이터취득차량 센서 데이터 조회',
        '제로셔틀차량 GPS-INS 데이터 정보 조회',
        '제로셔틀차량 객체 위치인식정보 조회',
        '제로셔틀 차량제어정보 조회',
        '제로셔틀 차량상태정보 조회',
        '도로노면 감시정보 조회',
        '보행자 Care 검지 내역 조회',
        '자율주행차기본안전메시지 조회',
        '판교제로시티 내 시설물 등에 대한 기준정보 조회',
        '경기도자율주행센터 CCTV 영상 이벤트 데이터'
    ]

    urls = [
        'http://apis.data.go.kr/C100006/zerocity/getCctvList/event/2DBoundingBox',
        'http://apis.data.go.kr/C100006/zerocity/getCctvList/event/2DSegmentation',
        'http://apis.data.go.kr/C100006/zerocity/getCctvList/zeroShuttle',
        'http://apis.data.go.kr/C100006/zerocity/getSensorList/zeroShuttle',
        'http://apis.data.go.kr/C100006/zerocity/getSensorList/dataAcquisitionVehicle',
        'http://apis.data.go.kr/C100006/zerocity/getGpsInsList',
        'http://apis.data.go.kr/C100006/zerocity/getObstacleList',
        'http://apis.data.go.kr/C100006/zerocity/getVcuControlList',
        'http://apis.data.go.kr/C100006/zerocity/getVcuStatusList',
        'http://apis.data.go.kr/C100006/zerocity/getIotRoadList',
        'http://apis.data.go.kr/C100006/zerocity/getIotPdstrnList',
        'http://apis.data.go.kr/C100006/zerocity/getV2XMessageList',
        'http://apis.data.go.kr/C100006/zerocity/getMetaDataList/cctv',
        'http://apis.data.go.kr/C100006/SearchCctvEventService/getCECctveventList'
    ]

    params_list = [
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '10', 'pageNo' : '1', 'eventType' : '06', 'startDt' : '2021-07-03', 'endDt' : '2021-07-31' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'sgmtType' : '01', 'startDt' : '2021-09-01', 'endDt' : '2021-09-02' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2021-06-23', 'endDt' : '2021-07-01' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'lidarLoc' : '02', 'startDt' : '2021-09-02', 'endDt' : '2021-09-03' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'lidarLoc' : '01', 'camLoc' : '01', 'startDt' : '2021-09-01', 'endDt' : '2021-09-02' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2021-11-11', 'endDt' : '2021-11-12' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2021-11-11', 'endDt' : '2021-11-30' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2021-11-11', 'endDt' : '2021-11-13' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2021-11-11', 'endDt' : '2021-11-13' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2019-09-07', 'endDt' : '2019-09-10' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'startDt' : '2020-05-02', 'endDt' : '2020-05-02' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '500', 'startDt' : '2021-07-27', 'endDt' : '2021-07-30' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'numOfRows' : '2', 'pageNo' : '1', 'eqmtId' : '', 'eqmtType' : '' },
        {'serviceKey' : '6jWk39DhwuYKHuTVldVl0c5Sncjc8ceKbYLq4xytc/mntrUhL9wLzF1B37sNsmieFEkLqLAeCQUvs3sKTrHWDw==', 'type' : '', 'eventDvsn' : '', 'dayNightCd' : '', 'skySttsDvsnCd' : '', 'eventDt' : ' ' }
    ]
   
    for i in range(len(serviceNames)):
        result = getRequest(serviceNames[i], urls[i], params_list[i])
        print(result)

# 서비스 점검 실행
getService()
