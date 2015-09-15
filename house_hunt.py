from oauth2client.client import SignedJwtAssertionCredentials
from bs4 import BeautifulSoup
from urlparse import urlparse
import json
import requests
import datetime
import ConfigParser
import gspread
import sys
import os


def get_expose_ids(worksheet):
    values_list = worksheet.col_values(1)
    if 'expose' in values_list:
        values_list.remove('expose')

    existing = {}
    for value in values_list:
        existing[value] = None

    return existing


def asciiLower(mystring):
    return mystring.encode('ascii', 'ignore').rstrip().lower()


def parseHeader(header):
    title = header.find("span", {"class": "title"})
    titletext = asciiLower(title.find("span", {"class": "link"}).contents[0])
    titletext = titletext.replace(",", ".")
    contents = title.contents
    c = contents[1]
    exposeid = None
    if 'href' in c.attrs:
        exposeid = c.attrs['href']

    return titletext, exposeid.split("/")[-1]


def parseInfo(info):
    try:
        area = -1
        price = -1
        rooms = -1

        contents = info.contents
        if len(contents) > 1:
            price = asciiLower(contents[1].dd.text).strip()
            price = price.replace(",", ".")
        if len(contents) > 3:
            area = asciiLower(contents[3].dd.text).strip()
            area = area.replace(",", ".")
        if len(contents) > 5:
            rooms = asciiLower(contents[5].dd.text).strip()
            rooms = rooms.replace(",", ".")
    except Exception as e:
        pass
    finally:
        return price, area, rooms


def parse_item(item):
    offer_dict = {}
    res = item.find("div", {"class": "resultlist_entry_data"})
    header = res.find("div", {"class": "header"})
    info = res.find("div",
                    {"class": "resultlist_criteria resultlist_gt_2_criteria"})
    title, expose_id = parseHeader(header)
    offer_dict['title'] = title
    offer_dict['expose'] = expose_id

    price, area, rooms = parseInfo(info)
    offer_dict['price'] = price
    offer_dict['m2'] = area
    offer_dict['rooms'] = rooms

    return offer_dict


def get_complete_url(original_url, expose_id):
    parsed = urlparse(original_url)
    return '/'.join([parsed.netloc, str(expose_id)])


def parse_url(url, existing={}):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    items = soup.findAll("li", {"data-item": "result"})
    format = '%Y-%m-%d %H:%M %p'
    time_now = datetime.datetime.today().strftime(format)

    new_offers = []
    for item in items:
        offer_dict = parse_item(item)
        expose_id = offer_dict['expose']
        if expose_id in existing:
            continue
        else:
            offer_dict['link'] = get_complete_url(url, expose_id)
            offer_dict['comments'] = "NEW OFFER"
            offer_dict['added_on'] = time_now
            new_offers.append(offer_dict)

    return new_offers


def setup_auth(key_location):
    json_key = json.load(open(key_location))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                json_key['private_key'], scope)
    gc = gspread.authorize(credentials)
    return gc


def parse_area(url, worksheet_name, area_name, sheet, existing):
    print 'Parsing area ', area_name
    worksheet = sheet.worksheet(worksheet_name)
    this_area_existing = get_expose_ids(worksheet)
    print 'Total Existing in this area', len(this_area_existing)
    new_row_num = len(this_area_existing) + 2
    headers = worksheet.row_values(1)
    existing.update(this_area_existing)
    print 'total existing overall ', len(existing)
    new_offers = parse_url(url, existing)
    print 'New offers in %s = %d' % (area_name, len(new_offers))

    for offers in new_offers:
        offer_id = offers['expose']
        print offers['link']
        existing[offer_id] = None
        row_data = []
        for ele in headers:
            row_data.append(offers[ele])
        updateRowCells(row_data, new_row_num, worksheet)
        new_row_num += 1

    return existing


def updateRowCells(row_data, row_index, sheet):
    for col_index, col_value in enumerate(row_data):
        sheet.update_cell(row_index, col_index + 1, col_value)


def help_usage():
    print 'python', __file__, 'config.ini'
    os._exit(1)


def main():
    if len(sys.argv) < 2:
        print 'Please specify config file'
        help_usage()

    config_location = sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.read(config_location)
    key_location = config.get("AUTH", "key_location")
    google_sheet_id = config.get("AUTH", "google_sheet_id")

    gc = setup_auth(key_location)
    google_worksheet = gc.open_by_key(google_sheet_id)

    active_regions = config.get("REGIONS", "active")
    active_region_list = active_regions.split(",")

    existing = {}
    for region in active_region_list:
        if not config.has_section(region):
            print 'Cannot parse region %s as section does not exists in config' % region
        else:
            url = config.get(region, "url")
            worksheet_name = config.get(region, "worksheet")
            existing.update(parse_area(url, worksheet_name, region,
                                       google_worksheet, existing))


if __name__ == '__main__':
    main()
