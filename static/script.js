document.addEventListener('DOMContentLoaded', function () {
    function toggleDisplay(containerId) {
        const container = document.getElementById(containerId);
        if (container.style.display === 'none' || container.style.display === '') {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }

    const apiCheckButton = document.getElementById('apiCheckButton');
    if (apiCheckButton) {
        apiCheckButton.addEventListener('click', function() {
            fetchDataAndVisualize('/api-results', 'api-results-intro');
            toggleDisplay('api-results-intro');
        });
    }

    const crawlingCheckButton = document.getElementById('crawlingCheckButton');
    if (crawlingCheckButton) {
        crawlingCheckButton.addEventListener('click', function() {
            fetchDataAndVisualize('/crawling-results', 'crawling-results-intro');
            toggleDisplay('crawling-results-intro');
        });
    }

    const apiDetailsButton = document.getElementById('apiDetailsButton'); // 올바른 id로 수정
    if (apiDetailsButton) {
        apiDetailsButton.addEventListener('click', function() {
            fetchDetailedData('/api-results-detail', 'api-results-detail');
            // toggleDisplay('api-results-detail');
        });
    }

    const crawlingdetailsButton = document.getElementById('crawlingdetailsButton');
    if (crawlingdetailsButton) {
        crawlingdetailsButton.addEventListener('click', function() {
            fetchDetailedData('/crawling-results-detail', 'crawling-results-detail');
            // toggleDisplay('crawling-results-detail');
        });
    }

    function loadHomeContent() {
        const today = new Date().toISOString().slice(0, 10); // 오늘 날짜를 YYYY-MM-DD 형식으로 변환
        fetch(`/api-check-status?date=${today}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('서버로부터 데이터를 가져오는 데 실패했습니다.');
                }
                return response.json();
            })
            .then(data => {
                updateHomeTab(data); // 데이터를 기반으로 홈 탭 내용 업데이트
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('Home').innerHTML = '데이터를 불러오는 데 실패했습니다.';
            });
    }

    function updateHomeTab(data) {
        const homeTab = document.getElementById('Home');
        let content = '';
    
        data.forEach(item => {
            // 점검 결과에 따라 클래스 이름 결정 (예: 'status-ok', 'status-error')
            const statusClass = item.status === '정상' ? 'status-ok' : 'status-error';
            // 항목별로 내용 추가 (예시입니다. 실제 데이터 구조에 맞게 조정해야 합니다.)
            content += `<div class="${statusClass}">${item.checkName}: ${item.status}</div>`;
        });
    
        homeTab.innerHTML = content;
    }

    // 홈 탭에 현재 날짜 데이터 점검 결과 표시
    function displayTodaysCheckStatus() {
        const today = new Date().toISOString().slice(0, 10);
        // 서버로부터 현재 날짜의 데이터 점검 상태를 가져오기 위한 요청
        // 이 부분은 올바른 API 엔드포인트 URL로 수정해야 함
        fetch(`/correct-api-endpoint?date=${today}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`서버 오류: 상태 코드 ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const homeTabContent = document.getElementById('Home');
                // 데이터 점검 결과에 따라 내용 업데이트
                // 서버 응답 구조에 따라 data.status를 적절히 수정
                homeTabContent.innerHTML = `오늘의 데이터 점검 상태: ${data.status}`;
            })
            .catch(error => {
                console.error('Error fetching today\'s check status:', error);
                // 오류 처리 로직 추가, 예를 들어 사용자에게 오류 메시지를 표시
                const homeTabContent = document.getElementById('Home');
                homeTabContent.innerHTML = `데이터 점검 상태를 불러오는 데 실패했습니다.`;
            });
    }

    function fetchDataAndVisualize(apiEndpoint, resultContainerId) {
        fetch(apiEndpoint)
            .then(response => response.json())
            .then(data => {
                if (!Array.isArray(data) || data.length === 0) {
                    document.getElementById(resultContainerId).textContent = '데이터가 없습니다.';
                    return;
                }

                let processedData;
                let dataType;

                if (apiEndpoint.includes('api-results')) {
                    processedData = processApiResults(data);
                    dataType = 'api';
                } else if (apiEndpoint.includes('crawling-results')) {
                    processedData = processCrawlingResults(data);
                    dataType = 'crawling';
                }

                const htmlContent = createHtmlTable(processedData, dataType);
                document.getElementById(resultContainerId).innerHTML = htmlContent;
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                document.getElementById(resultContainerId).textContent = '데이터를 불러오는 데 실패했습니다.';
            });
    }

    function processApiResults(data) {
        let serviceNames = new Set();
        let dates = new Set();
    
        data.forEach(row => {
            serviceNames.add(row.service_name);
            dates.add(row.check_time.split(' ')[0]);
        });
    
        let results = Array.from(serviceNames).map(serviceName => {
            let resultRow = { '서비스명': serviceName };
            Array.from(dates).forEach(date => {
                let latestStatus = data.filter(row => row.service_name === serviceName && row.check_time.startsWith(date))
                                      .sort((a, b) => new Date(b.check_time) - new Date(a.check_time))[0];
                resultRow[date] = latestStatus ? latestStatus.status : '데이터 없음';
            });
            return resultRow;
        });
    
        return { 'dates': Array.from(dates).sort(), 'data': results };
    }
    
    function processCrawlingResults(data) {
        let categories = new Set();
        let dates = new Set();
    
        data.forEach(row => {
            categories.add(row['구분'] + ', ' + row['데이터명'] + ', ' + row['사이트 주소']);
            dates.add(row['날짜'].split(' ')[0]);
        });
    
        let results = Array.from(categories).map(category => {
            let resultRow = { '카테고리': category };
            Array.from(dates).forEach(date => {
                let maxDownloads = data.filter(row => 
                    (row['구분'] + ', ' + row['데이터명'] + ', ' + row['사이트 주소']) === category && 
                    row['날짜'].startsWith(date)
                ).reduce((max, currentRow) => Math.max(max, parseInt(currentRow['다운로드 횟수'])), 0);
                resultRow[date] = maxDownloads || '데이터 없음';
            });
            return resultRow;
        });
    
        return { 'dates': Array.from(dates).sort(), 'data': results };
    }
    
    function createHtmlTable(processedData, dataType) {
        let htmlContent = "<table border='1'>";
    
        // // 날짜 헤더 추가
        // htmlContent += "<tr><th>날짜</th>";
    
        if (dataType === 'api') {
            htmlContent += "<th>서비스명</th>"; // API 데이터의 경우 '서비스명' 헤더 추가
        } else if (dataType === 'crawling') {
            htmlContent += "<th>서비스명</th><th>데이터명</th><th>사이트 주소</th>"; // 크롤링 데이터의 경우 추가적인 헤더 추가
        }
    
        processedData.dates.forEach(date => {
            htmlContent += `<th>${date}</th>`;
        });
        htmlContent += "</tr>";
    
        // 데이터 행 추가
        processedData.data.forEach(row => {
            htmlContent += "<tr>";
    
            if (dataType === 'api') {
                htmlContent += `<td>${row['서비스명']}</td>`; // API 데이터의 경우 '서비스명' 컬럼만 추가
                processedData.dates.forEach(date => {
                    htmlContent += `<td>${row[date] || '데이터 없음'}</td>`;
                });
            } else if (dataType === 'crawling') {
                // 서비스명, 데이터명, 사이트 주소를 별도로 처리
                let categorySplit = row['카테고리'].split(', ');
                htmlContent += `<td>${categorySplit[0]}</td>`; // 서비스명
                htmlContent += `<td>${categorySplit[1]}</td>`; // 데이터명
                htmlContent += `<td>${categorySplit[2]}</td>`; // 사이트 주소
                // 나머지 날짜 데이터 추가
                processedData.dates.forEach(date => {
                    htmlContent += `<td>${row[date] || '데이터 없음'}</td>`;
                });
            }
    
            htmlContent += "</tr>";
        });
    
        htmlContent += "</table>";
        return htmlContent;
    }

    function fetchDetailedData(apiEndpoint, resultContainerId) {
        fetch(apiEndpoint)
            .then(response => response.json())
            .then(data => {
    
                const resultsContainer = document.getElementById(resultContainerId);
                let htmlContent = '<table border="1"><tr>';
    
                let headers;
                if (apiEndpoint.includes('api-results-detail')) {
                    // API 결과에 대한 열 헤더 정의
                    headers = ['연번', 'service_name', 'check_time', 'status'];
                } else if (apiEndpoint.includes('crawling-results-detail')) {
                    // 크롤링 데이터에 대한 열 헤더 정의
                    headers = ['연번', '구분', '데이터명', '사이트 주소', '날짜', '다운로드 횟수'];
                }
    
                headers.forEach(header => {
                    htmlContent += `<th>${header}</th>`;
                });
                htmlContent += '</tr>';
    
                // 테이블 데이터 채우기
                data.forEach((row, index) => {
                    htmlContent += '<tr>';
                    htmlContent += `<td>${index + 1}</td>`; // 연번 추가
    
                    headers.slice(1).forEach(header => { // 첫 번째 열은 연번이므로 제외
                        const cellValue = row[header] ? row[header] : '정보 없음';
                        htmlContent += `<td>${cellValue}</td>`;
                    });
    
                    htmlContent += '</tr>';
                });
    
                htmlContent += '</table>';
                resultsContainer.innerHTML = htmlContent;
            })
            .catch(error => {
                // 오류 로깅
                console.error('데이터 로드 실패. 오류:', error);
                document.getElementById(resultContainerId).textContent = '데이터를 불러오는 데 실패했습니다.';
            });
    }
    
    function openTab(evt, tabName) {
        var tabcontent = document.getElementsByClassName("tabcontent");
        var tablinks = document.getElementsByClassName("tablinks");

        for (var i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }

        for (var i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }

        var selectedTabContent = document.getElementById(tabName);
        if (selectedTabContent) {
            selectedTabContent.style.display = "block";
        }

        evt.currentTarget.className += " active";
    }

    // 이벤트 리스너를 적절한 탭 버튼에 추가
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById("defaultOpen").click();
    });
});