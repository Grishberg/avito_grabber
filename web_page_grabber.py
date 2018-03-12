# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import urllib
import json
from datetime import *
from db_provider import *
import response_fields as rf
import merger

URL = 'https://www.avito.ru/sankt-peterburg/kvartiry/sdam/na_dlitelnyy_srok?pmax=23000&pmin=0'

DEBUG = False
URL_WITH_PAGE = '/sankt-peterburg/kvartiry/sdam/na_dlitelnyy_srok?p='
URL_AFTER_PAGE = '&amp;pmax=23000&amp;pmin=0'
RUB = u' руб'

TODAY = u'Сегодня'
YESTERDAY = u'Вчера'

BASE_URL = 'https://www.avito.ru'
MONTH_ARRAY = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня',
               u'июля', u'августа',
               u'сентября', u'октября', u'ноября', u'декабря']


def grab_page_from_web(page_index=1):
    url = URL + "&p=" + str(page_index)
    r = requests.get(url)
    if r.status_code == 200 and DEBUG:
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


def parse_page(soup, min_date):
    result = []
    ads = soup.find('div', class_='catalog-list').find_all('div', class_='item_table')
    for ad in ads:
        parsed_data = Apartment(parse_ad(ad))
        if parsed_data.data[rf.DATE] >= min_date:
            result.append(parsed_data)
    return result


def find_pages_count(soup):
    div_with_pages = soup.find("div", "pagination-pages")
    pages = div_with_pages.find_all('a', 'pagination-page')
    last_page_href = pages[-1].get('href')
    total_pages = int(last_page_href.split("p=")[1].split('&')[0])
    return total_pages


def parse_ad(ad):
    photo = ''
    try:
        raw_style = ad.find('div', class_='large-picture').get('style')
        lst = raw_style.split('url(//')
        if len(lst) == 2:
            photo = lst[1][:-1]
    except:
        photo = ''
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

    data = {rf.TITLE: title,
            rf.URL: url,
            rf.PHOTO: photo,
            rf.PRICE: price_rub,
            rf.PRICE_FEE: price_fee,
            rf.ADDRESS: address,
            rf.METRO: metro,
            rf.METRO_DISTANCE: metro_distance,
            rf.DATE: time}
    return data


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


def extract_geo_location(payload):
    data = json.loads(payload)
    response = data.get('response')
    geo_object_collection = response.get('GeoObjectCollection')
    feature_members = geo_object_collection.get('featureMember')
    for feature_member in feature_members:
        geo_object = feature_member.get('GeoObject')
        point = geo_object.get('Point')
        pos = point.get("pos").split(" ")
        return pos
    return ['0', '0']


def populate_items_with_geo_location(new_items):
    for new_item in new_items:
        ad = new_item.data
        address = ad[rf.ADDRESS]
        if address == '':
            ad[rf.POS_L] = None
            ad[rf.POS_W] = None
            continue
        geocode = get_geo_by_address(address)
        pos = extract_geo_location(geocode)
        try:
            ad[rf.POS_L] = float(pos[0])
            ad[rf.POS_W] = float(pos[1])
        except Exception as e:
            ad[rf.POS_L] = None
            ad[rf.POS_W] = None
            print e


def check_new_ads():
    ids = []
    html = grab_page_from_web()

    soup = BeautifulSoup(html, 'lxml')
    total_pages_count = find_pages_count(soup)

    db = DbService()
    min_date = datetime.today() - timedelta(days=10)
    min_date_for_web = datetime.today() - timedelta(days=5)
    cached_data_list = db.get_ads(min_date)

    for page_index in range(total_pages_count):
        if page_index > 0:
            html = grab_page_from_web(page_index + 1)
            soup = BeautifulSoup(html, 'lxml')
        new_ads_list = parse_page(soup, min_date_for_web)

        new_items = merger.find_new_ads(new_ads_list, cached_data_list)
        populate_items_with_geo_location(new_items)

        ids = db.add_ads(new_items)
        for id in ids:
            ids.append(id)

    db.close()
    return ids


if __name__ == '__main__':
    html = grab_page_from_web()

    soup = BeautifulSoup(html, 'lxml')
    total_pages_count = find_pages_count(soup)
    print 'total pages count:', total_pages_count

    db = DbService()
    min_date = datetime.today() - timedelta(days=6)
    min_date_for_web = datetime.today() - timedelta(days=5)
    cached_data_list = db.get_ads(min_date)
    print 'cached data list:', len(cached_data_list)

    for page_index in range(total_pages_count):
        print 'current index:', page_index
        if page_index > 0:
            html = grab_page_from_web(page_index + 1)
            soup = BeautifulSoup(html, 'lxml')
        new_ads_list = parse_page(soup, min_date_for_web)

        if len(new_ads_list) == 0:
            print 'no new data'
            break

        new_items = merger.find_new_ads(new_ads_list, cached_data_list)
        print 'new items count:', len(new_items)
        populate_items_with_geo_location(new_items)

        for ad in new_items:
            print "    new ads:", ad.data

        ids = db.add_ads(new_items)
        print 'added count:', len(ids)

    db.close()
    print 'done.'
