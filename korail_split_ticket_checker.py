# -*- coding: utf-8 -*-
import sys
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print 'BeautifulSoup4 and requests Required.'
    sys.exit()

FARE_URL = 'http://www.letskorail.com/ebizprd/EbizPrdTicketPr21111_i1.do'
ROUTE_URL = 'http://www.letskorail.com/ebizprd/EbizPrdTicketPr11131_i1.do'

DEFAULT_HEADERS = {"Referer": FARE_URL,
                   "Origin": "http://www.korail.com",
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) Apple" +
                                 "WebKit/537.36 (KHTML, like Gecko) Chrome/" +
                                 "32.0.1700.41 Safari/537.36"
                   }

DEFAULT_PAYLOADS = {"radJobId": "1",  # 조회 여정 종류 (직통)
                    "selGoTrain": "05",  # 열차타입 (전체)
                    "txtSeatAttCd_4": "15",  # 차실/좌석: 할인좌석종별 (기본)
                    "txtSeatAttCd_3": "00",  # 차실/좌석: 창/내측/1인좌석종별 (기본)
                    "txtSeatAttCd_2": "00",  # 차실/좌석: 좌석 방향 (기본)
                    "checkStnNm": "Y"  # 역 이름 검색 옵션 Y
                    }


def get_train_routes(date, train_number):
    # List to store route data
    stations = []

    # Request for train routes
    params = {'txtRunDt': date, 'txtTrnNo': '%05d' % int(train_number)}
    r = None
    try:
        r = requests.get(ROUTE_URL, params=params, headers=DEFAULT_HEADERS)
    except:
        print u'열차 정보를 가져오는데 실패했습니다.'

    # Get soup object
    if r:
        soup = BeautifulSoup(r.content, 'html')

        # To get train type
        train_type_data = soup.find("font")
        if train_type_data:
            train_type = train_type_data.text.strip()
            train_type_start = train_type.find('[') + 1
            train_type_end = train_type.find(']')
            train_type = train_type[train_type_start:train_type_end]
        else:
            return None, None

        # Looping for each stops
        route_results = soup.find_all("tr", {"bgcolor": "#FFFFFF"})
        for route in route_results:
            fragments = route.find_all('td')
            station = {}
            station['name'] = fragments[0].text.strip()
            station['arrival_time'] = fragments[1].text.strip()
            station['departure_time'] = fragments[2].text.strip()

            if not station.get('arrival_time') \
               or len(station.get('arrival_time')) < 5:
                station['arrival_time'] = station['departure_time']
            if not station.get('departure_time') \
               or len(station.get('departure_time')) < 5:
                station['departure_time'] = station['arrival_time']

            stations.append(station)

        return train_type, stations
    else:
        return None, None


def check_avail_route(departure, arrival, date, train_number):
    payloads = DEFAULT_PAYLOADS
    payloads['txtGoAbrdDt'] = date
    payloads['txtGoStart'] = departure['name'].encode('utf-8')
    payloads['txtGoEnd'] = arrival['name'].encode('utf-8')
    payloads['txtGoHour'] = departure['departure_time'].replace(':', '') + '00'

    # Request for checking availablity
    r = requests.post(FARE_URL, data=payloads, headers=DEFAULT_HEADERS)

    if r.status_code == requests.codes.ok:
        # Get soup object from response
        soup = BeautifulSoup(r.content, 'html')

        # Get result table
        result = soup.find("table", {"class": "tbl_h"})

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


def get_route(stations, date, train_number, departure, arrival):
    # Routes
    routes = []
    # Looping stations
    for idx in range(arrival, departure, -1):
        first_trip = False
        # To check whether direct route avail or not
        if idx == arrival:
            first_trip = check_avail_route(
                stations[departure], stations[idx], date, train_number)
            if first_trip:
                route = []
                route.append(stations[departure])
                route.append(stations[idx])
                routes.append(route)
                break
        else:
            first_trip = check_avail_route(stations[departure], stations[idx],
                                           date, train_number)
            if first_trip:
                # To check only two routes
                second_trip = check_avail_route(
                    stations[idx], stations[arrival], date, train_number)
                if second_trip:
                    route = []
                    route.append(stations[departure])
                    route.append(stations[idx])
                    route.append(stations[arrival])
                    routes.append(route)

    return routes


def main():
    date = raw_input('Input Date (YYYYmmdd): ')
    train_number = raw_input('Train No: ')

    print ''
    print u'해당 기차편을 검색 중입니다.'

    train_type, stations = get_train_routes(date, train_number)

    if train_type:
        print ''
        print train_type, train_number
        print ''

        print u'* 운행역 리스트 *'
        for i, station in enumerate(stations):
            print i, ':', station['name']

        print ''
        departure = int(raw_input(u'Departure : '))
        arrival = int(raw_input(u'Arrival: '))

        print ''
        print u'운행 가능 여정을 검색 중입니다.'

        results = get_route(stations, date, train_number, departure, arrival)

        print ''
        for idx, result in enumerate(results):
            print u'여정 %d ' % (idx+1),
            for trip in result:
                print '%s %s ' % (trip['name'], trip['departure_time']),
            print ''

        print u'\n --> 탑승가능: %s' % bool(results)
    else:
        print u'존재하지 않는 열차입니다.'


if __name__ == '__main__':
    main()
