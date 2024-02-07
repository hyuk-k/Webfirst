import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

# 파일명을 정의합니다. 누적 데이터를 저장할 파일입니다.
accumulated_file_name = 'accumulated_crawling_results.csv'

# 누적 데이터 파일이 이미 존재하면 불러옵니다.
if os.path.exists(accumulated_file_name):
    accumulated_data = pd.read_csv(accumulated_file_name, encoding='utf-8-sig')
else:
    # 누적 데이터 파일이 존재하지 않을 때, 적절한 열을 가진 빈 데이터프레임을 생성합니다.
    accumulated_data = pd.DataFrame(columns=['구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수'])

# 각 제목을 구분과 데이터명으로 나누기 위한 함수
def split_title(title):
    parts = title.split(' - ')
    if len(parts) > 1:
        return parts[0].strip(), parts[1].strip()
    else:
        return title.strip(), ''

# 각 페이지에서 날짜별 다운로드 수를 크롤링하는 함수
def fetch_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 웹 페이지에서 제목을 추출하는 부분
    title_element = soup.find('div', class_='data_market_title')
    title = title_element.text.strip() if title_element else '제목을 찾을 수 없습니다'
    title = re.sub(r'^\d+\.\s+', '', title)  # 제목에서 숫자와 점을 제거

    # 'data_market_info' 클래스를 가진 ul 태그를 찾고, 그 안의 모든 li 태그를 찾습니다.
    data_info = soup.find('ul', class_='data_market_info').find_all('li')
    
    # 날짜별 다운로드 수를 추출하는 부분
    download_counts = {}

   # 현재 날짜와 시간 추출
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')  # '년-월-일 시:분:초' 형식으로 형식화합니다.

    # '다운로드' 횟수 추출
    for li in data_info:
        if '다운로드' in li.text:
            count = li.find('b', class_='text-bold').text.strip()
            download_counts[date_str] = count  # 현재 날짜와 시간을 사용하여 딕셔너리에 추가합니다.
            break

    return {
        'title': title,
        'download_counts': download_counts
    }

# URL 목록
urls = [
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=21",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=207",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=17",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=18",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=19",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=20",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=22",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=16",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=240",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=241",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=728",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=730",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=731",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=732",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=733",
    "https://bigdata-geo.kr/user/dataset/view.do?data_sn=729"
]

# 크롤링 결과 저장 리스트
crawling_results = []

# # 각 URL 크롤링
# for url in urls:
#     data = fetch_data(url)
#     title = data['title']
#     download_counts = data['download_counts']
#     category, data_name = split_title(title)
#     # 각 날짜별 다운로드 횟수와 함께 결과에 추가합니다.
#     for date, count in download_counts.items():
#         crawling_results.append((category, data_name, url, date, count))

# 각 URL 크롤링
for url in urls:
    data = fetch_data(url)
    title = data['title']
    download_counts = data['download_counts']
    category, data_name = split_title(title)
    
    # 날짜별로 데이터를 누적합니다.
    for date, count in download_counts.items():
        # 날짜와 카테고리, 데이터명을 기준으로 기존 데이터를 확인합니다.
        existing_data = accumulated_data[
            (accumulated_data['날짜'] == date) & 
            (accumulated_data['구분'] == category) & 
            (accumulated_data['데이터명'] == data_name)
        ]
        
        # 기존 데이터가 있다면, 다운로드 횟수를 업데이트합니다.
        if not existing_data.empty:
            accumulated_data.loc[existing_data.index, '다운로드 횟수'] = count
        else:
            # 새로운 데이터를 추가합니다.
            new_data = pd.DataFrame({
                '구분': [category],
                '데이터명': [data_name],
                '사이트 주소': [url],
                '날짜': [date],
                '다운로드 횟수': [count]
            })
            accumulated_data = pd.concat([accumulated_data, new_data], ignore_index=True)

# 누락된 값에 대한 처리 (NaN 값을 '-'로 변경)
accumulated_data.fillna('-', inplace=True)

# 데이터프레임 옵션 설정
pd.set_option('display.unicode.east_asian_width', True)

# 데이터프레임 생성
df_accumulated_data = pd.DataFrame(accumulated_data, columns=['구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수'])

# '연번' 칼럼 추가: 1부터 시작하며 각 행마다 1씩 증가
df_accumulated_data['연번'] = range(1, len(df_accumulated_data) + 1)

# '연번' 칼럼을 첫 번째 칼럼으로 이동
cols = df_accumulated_data.columns.tolist()
# '연번' 칼럼의 인덱스를 찾아 첫 번째 위치로 이동
cols = cols[-1:] + cols[:-1]
df_accumulated_data = df_accumulated_data[cols]

# 누적된 데이터프레임을 출력합니다.
print(df_accumulated_data)

# 데이터프레임을 CSV 파일로 저장합니다.
df_accumulated_data.to_csv(accumulated_file_name, index=False, encoding='utf-8-sig')

#####################################################################################
## MYSQL 적재
from sqlalchemy import create_engine
import pandas as pd

# 데이터베이스 연결 정보 설정
username = 'root'  # MySQL 사용자 이름
password = '0928'  # MySQL 비밀번호
host = 'localhost'          # MySQL 호스트
dbname = 'test01'      # 데이터베이스 이름
table_name = 'crwaling02'   # 데이터를 적재할 테이블 이름

# SQLAlchemy 엔진 생성
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{dbname}')

# # 데이터베이스에 적재할 DataFrame 컬럼 순서 조정
# df_accumulated_data = df_accumulated_data[['연번', '구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수']]

# DataFrame을 MySQL 테이블에 적재합니다. 
# if_exists='replace'를 사용하면 기존 테이블을 새로운 데이터로 대체합니다.
df_accumulated_data.to_sql(name=table_name, con=engine, if_exists='append', index=False)



################################################## 수정해볼까?

# import re
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from datetime import datetime

# # 각 제목을 구분과 데이터명으로 나누기 위한 함수
# def split_title(title):
#     parts = title.split(' - ')
#     if len(parts) > 1:
#         return parts[0].strip(), parts[1].strip()
#     else:
#         return title.strip(), ''

        
# current_date = datetime.now().strftime('%Y-%m-%d')


# # 각 페이지에서 날짜별 다운로드 수를 크롤링하는 함수
# def fetch_data(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # 웹 페이지에서 제목을 추출하는 부분
#     title_element = soup.find('div', class_='data_market_title')
#     title = title_element.text.strip() if title_element else '제목을 찾을 수 없습니다'
#     title = re.sub(r'^\d+\.\s+', '', title)  # 제목에서 숫자와 점을 제거

#     # 'data_market_info' 클래스를 가진 ul 태그를 찾고, 그 안의 모든 li 태그를 찾습니다.
#     data_info = soup.find('ul', class_='data_market_info').find_all('li')
    
#     # 날짜별 다운로드 수를 추출하는 부분
#     download_counts = {}
#     # '다운로드' 횟수를 추출합니다.
#     for li in data_info:
#         if '다운로드' in li.text:
#             # 다운로드 횟수가 포함된 태그를 찾아 텍스트를 추출합니다.
#             count = li.find('b', class_='text-bold').text.strip()
#             # 여기에서 날짜 데이터를 얻을 수 있는 코드를 추가합니다.
#             # 예시로, 날짜가 특정 태그에 있을 경우 그 태그에서 날짜를 추출합니다.
#             # 이 부분은 실제 페이지의 구조에 따라 달라집니다.
#             # date = li.find('span', class_='date-class-name').text.strip() # 실제 날짜 태그의 클래스명으로 교체 필요
#             # 만약 날짜가 li 태그 내에 다른 형태로 표시되면 그에 맞게 추출 로직을 작성해야 합니다.
#             # 아래는 단순한 예시입니다.
#             date = '2024-01-25'  # 실제 날짜 추출 로직으로 교체 필요
#             download_counts[date] = count
#             # 일반적으로 하나의 li 태그에 하나의 날짜 데이터만 있을 것이므로 break를 사용합니다.
#             break

#     return {
#         'title': title,
#         'download_counts': download_counts
#     }

# # URL 목록
# urls = [
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=21",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=207",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=17",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=18",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=19",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=20",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=22",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=16",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=240",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=241",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=728",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=730",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=731",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=732",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=733",
#     "https://bigdata-geo.kr/user/dataset/view.do?data_sn=729"
# ]

# # 크롤링 결과 저장 리스트
# crawling_results = []

# # 각 URL 크롤링
# for url in urls:
#     data = fetch_data(url)
#     title = data['title']
#     download_counts = data['download_counts']
#     category, data_name = split_title(title)
#     # 각 날짜별 다운로드 횟수와 함께 결과에 추가합니다.
#     for date, count in download_counts.items():
#         crawling_results.append((category, data_name, url, date, count))

# # 데이터프레임 생성
# df_crawling = pd.DataFrame(crawling_results, columns=['구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수'])

# # 날짜를 행으로, 구분과 데이터명을 멀티인덱스로 설정하고, 다운로드 횟수를 값으로 하는 피벗 테이블 생성
# df_pivot = df_crawling.pivot_table(index=['구분', '데이터명', '사이트 주소'], columns='날짜', values='다운로드 횟수', aggfunc='first')

# # 파일명을 정의합니다. 누적 데이터를 저장할 파일입니다.
# accumulated_file_name = 'accumulated_crawling_results.csv'

# # 누적 데이터 파일이 이미 존재하면 불러옵니다.
# if os.path.exists(accumulated_file_name):
#     df_accumulated = pd.read_csv(accumulated_file_name, encoding='utf-8-sig')
# else:
#     df_accumulated = pd.DataFrame(columns=['구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수'])

# # 새로운 데이터와 기존 데이터를 병합합니다.
# df_accumulated = pd.concat([df_accumulated, df_pivot]).drop_duplicates()

# # 누락된 값에 대한 처리 (NaN 값을 '-'로 변경)
# df_accumulated.fillna('-', inplace=True)

# # 누적된 데이터프레임을 출력합니다.
# print(df_accumulated)

# # 데이터프레임을 CSV 파일로 저장합니다.
# df_accumulated.to_csv(accumulated_file_name, index=False, encoding='utf-8-sig')


