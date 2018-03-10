# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import urllib
import json
from datetime import *
from db_provider import *
import response_fields as rf
import merger

RUB = u' руб'

TODAY = u'Сегодня'
YESTERDAY = u'Вчера'

BASE_URL = 'https://www.avito.ru'
MONTH_ARRAY = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня',
               u'июля', u'августа',
               u'сентября', u'октября', u'ноября', u'декабря']


def grab_page(url):
    r = requests.get(url)
    if r.status_code == 200:
        with open("content.html", 'wb') as f:
            f.write(r.content)
    return r.text


def get_geo_by_address(street_name):
    address = u'город Санкт-Петербург,' + street_name
    struct = {'format': 'json', 'geocode': address.encode('utf-8')}
    encoded_url = urllib.urlencode(struct)
    url = "https://geocode-maps.yandex.ru/1.x/?" + encoded_url
    r = requests.get(url)
    return r.text


def get_page_data(html):
    result = []
    soup = BeautifulSoup(html, 'lxml')
    ads = soup.find('div', class_='catalog-list').find_all('div', class_='item_table')
    for ad in ads:
        result.append(Apartment(parse_ad(ad)))
    return result


def parse_price(price):
    lst = price.split(RUB)
    try:
        if len(lst[1]) > 0:
            lst_fee = lst[1].split("\n\n")
            if len(lst_fee) > 0:
                fee_str = lst_fee[1][:-1]
                fee = int(fee_str)
    except:
        fee = 0

    try:
        price_rub_str = lst[0].replace(' ', '')
    except:
        price_rub_str = '0'
    return (int(price_rub_str), fee)


def parse_ad(ad):
    try:
        h3_title = ad.find('h3', class_='title')
        title = h3_title.text.strip()
        url = BASE_URL + h3_title.find('a').get('href')
    except:
        title = ''
        url = ''

    try:
        price = ad.find('div', class_='about').text.strip()
        price_rub, price_fee = parse_price(price)
    except:
        price_rub = 0
        price_fee = 0

    try:
        address_element = ad.find('p', class_='address')
        # result = re.match(ADDRESS_PATTERN, address_element)
        # print 'res', result.group(0), result.group(1)
        address_str = address_element.text.strip()
        metro_distance = address_element.find('span').text.strip()
        address_parts = address_str.split(metro_distance)
        address = address_parts[1].replace(",", "").strip()
        metro = address_parts[0]
    except:
        address = ''
        metro_distance = ''
        metro = ''

    try:
        time = time_str_to_datetime(ad.find('div', class_='c-2').text.strip())
    except:
        time = ''

    geocode = get_geo_by_address(address)
    pos = extract_geo_coords(geocode)

    data = {rf.TITLE: title,
            rf.URL: url,
            rf.PRICE: price_rub,
            rf.PRICE_FEE: price_fee,
            rf.ADDRESS: address,
            rf.METRO: metro,
            rf.METRO_DISTANCE: metro_distance,
            rf.DATE: time,
            rf.POS_L: float(pos[0]),
            rf.POS_W: float(pos[1])}
    return data


def time_str_to_datetime(time_str):
    today_lst = time_str.split(TODAY)
    now_dt = datetime.now()
    if len(today_lst) == 2:
        time_array = parse_time(today_lst[1].strip())
        return datetime(now_dt.year, now_dt.month, now_dt.day, time_array[0], time_array[1], 0, 0)

    yesterday_lst = time_str.split(YESTERDAY)
    if len(yesterday_lst) == 2:
        time_array = parse_time(yesterday_lst[1].strip())
        yesterday_time = datetime.today() - timedelta(days=1)
        return datetime(yesterday_time.year,
                        yesterday_time.month,
                        yesterday_time.day,
                        time_array[0], time_array[1], 0, 0)
    time_lst = time_str.split()
    day_str = int(time_lst[0])
    month_index = get_month_from_str(time_lst[1])
    time_array = parse_time(time_lst[2].strip())
    return datetime(now_dt.year,
                    month_index,
                    day_str,
                    time_array[0], time_array[1], 0, 0)


def get_month_from_str(month_str):
    for m in range(len(MONTH_ARRAY)):
        if MONTH_ARRAY[m] == month_str:
            return m + 1
    return None


# returns (H, M)
def parse_time(time_str):
    lst = time_str.split(':')
    return int(lst[0]), int(lst[1])


def open_html_from_cache():
    f = open('content.html', 'rb')
    buf = f.read()
    f.close()
    return buf


def extract_geo_coords(payload):
    data = json.loads(payload)
    response = data.get('response')
    geo_object_collection = response.get('GeoObjectCollection')
    feature_members = geo_object_collection.get('featureMember')
    for feature_member in feature_members:
        geo_object = feature_member.get('GeoObject')
        point = geo_object.get('Point')
        pos = point.get("pos").split(" ")
        return pos
    return ['', '']


if __name__ == '__main__':
    html = grab_page(
        'https://www.avito.ru/sankt-peterburg/kvartiry/sdam/na_dlitelnyy_srok?pmax=23000&pmin=0&metro=157-160-176-191-210&f=550_5702-5703')

    # html = open_html_from_cache()
    new_ads_list = get_page_data(html)

    db = DbService()
    # new_count = db.add_ads(ads_list)
    # print new_count
    cached_data_list = db.get_ads()

    new_items = merger.find_new_ads(new_ads_list, cached_data_list)
    if len(new_items) > 0:
        db.add_ads(new_items)

    print "new ads:"
    for ad in new_items:
        print '   ', ad.data

    print len(cached_data_list)
    db.close()
