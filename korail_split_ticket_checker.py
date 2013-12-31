# -*- coding: utf-8 -*-
import sys
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print 'BeautifulSoup4 and requests Required.'
    sys.exit()

FARE_URL = 'http://www.korail.com/servlets/pr.pr21100.sw_pr21111_i1Svt'
ROUTE_URL = 'http://www.korail.com/servlets/pr.pr11100.sw_pr11131_i1Svt'

DEFAULT_HEADERS = { "Referer" : FARE_URL,
                    "Origin" : "http://www.korail.com",
                    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.41 Safari/537.36"
                  }

DEFAULT_PAYLOADS = { "radJobId" : "1", # 조회 여정 종류 (직통)
                     "selGoTrain" : "05", # 열차타입 (전체)
                     "txtSeatAttCd_4" : "15", # 차실/좌석: 할인좌석종별 (기본)
                     "txtSeatAttCd_3" : "00", # 차실/좌석: 창/내측/1인좌석종별 (기본)
                     "txtSeatAttCd_2" : "00", # 차실/좌석: 좌석 방향 (기본)
                     "checkStnNm" : "Y" # 역 이름 검색 옵션 Y
                   }


def get_train_routes(date, train_number):
    # List to store route data
    stations = []

    # Request for train routes
    params = {'txtRunDt': date, 'txtTrnNo': '%05d' % int(train_number)}
    r = requests.get(ROUTE_URL, params=params, headers=DEFAULT_HEADERS)

    # Get soup object
    soup = BeautifulSoup(r.content, 'html')

    # To get train type
    train_type = soup.find("font", { "color" : "#003399" }).text.strip()
    train_type = train_type[train_type.find('[') + 1 : train_type.find(']')]

    # Looping for each stops
    route_results = soup.find_all("tr", { "bgcolor" : "#FFFFFF" })
    for route in route_results:
        fragments = route.find_all('td')
        station = {}
        station['name'] = fragments[0].text.strip()
        station['arrival_time'] = fragments[1].text.strip()
        station['departure_time'] = fragments[2].text.strip()
        
        if not station.get('arrival_time') or len(station.get('arrival_time')) < 5:
            station['arrival_time'] = station['departure_time']
        if not station.get('departure_time') or len(station.get('departure_time')) < 5:
            station['departure_time'] = station['arrival_time']

        stations.append(station)

    return train_type, stations


def check_avail_route(departure, arrival, date, train_number):
    payloads = DEFAULT_PAYLOADS
    payloads['txtGoAbrdDt'] = date
    payloads['txtGoStart'] = departure['name'].encode('euc-kr')
    payloads['txtGoEnd'] = arrival['name'].encode('euc-kr')
    payloads['txtGoHour'] = departure['departure_time'].replace(':', '') + '00'

    # Request for checking availablity
    r = requests.get(FARE_URL, params=payloads, headers=DEFAULT_HEADERS)

    if r.status_code == requests.codes.ok:
        # Get soup object from response
        soup = BeautifulSoup(r.content, 'html')

        # Get result table
        result = soup.find("table", { "class" : "list-view" })
        if result:
            # Get all train infos
            result_line = result.find_all('tr')
            for line in result_line:
                # Get each train
                fragments = line.find_all('td')
                if fragments:
                    result_train_number = fragments[1].text.strip()
                    # Train number validation
                    if result_train_number == train_number:
                        # To check whether train is on sale or not
                        if 'icon_apm_yes' in fragments[5].find('img')['src']:
                            return True
                        else:
                            return False
        else:
            return False
    else:
        r.raise_for_status()


def get_route(stations, date, train_number):
    # Looping stations
    for idx in range(1,len(stations)):
        first_trip = check_avail_route(stations[0], stations[-idx], date, train_number)
        if idx == 1 and first_trip:
            print '%s %s -> %s %s' % (stations[0]['name'], stations[0]['departure_time'], stations[-idx]['name'], stations[-idx]['departure_time'])
            return True
        elif first_trip:
            second_trip_idx = len(stations) - idx
            second_trip = check_avail_route(stations[second_trip_idx], stations[-1], date, train_number)
            if second_trip:
                print '%s %s -> %s %s' % (stations[0]['name'], stations[0]['departure_time'], stations[-idx]['name'], stations[-idx]['departure_time'])
                print '%s %s -> %s %s' % (stations[second_trip_idx]['name'], stations[second_trip_idx]['departure_time'], stations[-1]['name'], stations[-1]['departure_time'])
                return True

    return False


def main():
    date = raw_input('Input Date (YYYYmmdd): ')
    train_number = raw_input('Train No: ')

    train_type, stations = get_train_routes(date, train_number)
    print ''
    print train_type, train_number
    result = get_route(stations, date, train_number)

    print u' --> 탑승가능: %s' % result


if __name__ == '__main__':
    main()