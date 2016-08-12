# -*- coding: utf-8 -*-
import requests
import json
import re
import boto3
import xml.etree.ElementTree as ET
import datetime as dt
from bs4 import BeautifulSoup

DIV_CONTACT_P = 'div.col-sm-4 div.pc div.box.boxB.boxY1 div.contact p'
DIV_CONTACT_LONG_P = DIV_CONTACT_P.replace('contact', 'contact-long')
INNER_DIV_LIST_DESC = 'div.col-sm-8 div.box.boxW.listInner div.list-desc'
CONTAINER_DIV_ROW = 'html body div div.pushmenu-push div.main div.container div.row'
RSS_ENDPOINT = "https://www.tenders.gov.au/public_data/rss/rss.xml"
CLOSE_DATE_TIME_FORMAT = "%d-%b-%Y %I:%M %p (ACT Local Time) Show close time for other time zones"
LONG_CONTACT_NAME_INDEX = 0
REGULAR_CONTACT_NAME_INDEX = 1

s3 = boto3.resource('s3')


def handler(event, context):
    items = get_items()
    entries = [get_entry(item) for item in items]
    if len(entries) > 0:
        s3.Object('trade-leads', 'australia.json').put(Body=json.dumps(entries), ContentType='application/json')
        return "Uploaded australia.json file with %i trade leads" % len(entries)
    else:
        return "No entries loaded from %s so there is no JSON file to upload" % RSS_ENDPOINT


def get_entry(item):
    tender_url = item['link']
    print "Fetching %s" % tender_url
    soup = get_soup(tender_url)
    row = soup.select(CONTAINER_DIV_ROW)[0]
    contact = get_contact(row)
    main_fields = row.select(INNER_DIV_LIST_DESC)
    tuples = [list_item.text.strip().splitlines() for list_item in main_fields]
    two_tuples = [[get_key(tuple[0]), get_value(tuple[1:])] for tuple in tuples if len(tuple) > 1]
    dict = {tuple[0]: tuple[1] for tuple in two_tuples if field_value_seems_reasonable(tuple[1])}
    dict['close_date_time'] = parse_close_date_time(dict['close_date_time'])
    entry = {"tender_url": tender_url,
             "publish_date": item['pubDate'],
             "uuid": tender_url[tender_url.find('UUID=') + 5:],
             "title": row.select('.lead')[0].text}
    dict.update(entry)
    dict.update(contact)
    return dict


def parse_close_date_time(close_date_time):
    return dt.datetime.strptime(close_date_time, CLOSE_DATE_TIME_FORMAT).strftime("%Y-%m-%dT%H:%M:%S+10:00")


def get_contact(row):
    contact = {}
    contact_fields, contact_name_index = parse_contact_formats(row)

    contact_officer = contact_fields[contact_name_index].text
    if contact_officer: contact['contact_officer'] = contact_officer

    remaining_fields_index = contact_name_index + 1
    phone_email_etc_list = [p_entry.text.split(':') for p_entry in contact_fields[remaining_fields_index:]]
    phone_email_etc_hash = {contact_tuple[0]: contact_tuple[1].strip() for contact_tuple in phone_email_etc_list}

    phone = phone_email_etc_hash['P']
    if phone_seems_reasonable(phone): contact['phone'] = phone

    email = phone_email_etc_hash['E']
    if email: contact['email'] = email

    return contact


def parse_contact_formats(row):
    contact_fields = row.select(DIV_CONTACT_P)
    contact_name_index = REGULAR_CONTACT_NAME_INDEX
    if len(contact_fields) == 0:
        contact_fields = row.select(DIV_CONTACT_LONG_P)
        contact_name_index = LONG_CONTACT_NAME_INDEX
    return contact_fields, contact_name_index


def phone_seems_reasonable(phone):
    return re.search('[1-9]', phone)


def field_value_seems_reasonable(value):
    return value and not (value == 'Nil')


def get_key(key_string):
    return '_'.join(re.sub('[^a-z ]', '', key_string.lower()).split())


def get_value(values):
    value = ' '.join(values).strip()
    return value


def get_items():
    print "Fetching RSS feed of items..."
    response = requests.get(RSS_ENDPOINT)
    root = ET.fromstring(response.text.encode('utf-8'))
    items = root.findall('./channel/item')
    item_list = [{"link": item.find('link').text, "pubDate": item.find('pubDate').text} for item in items]
    print "Found %i items" % len(item_list)
    return item_list


def get_soup(link):
    response = requests.get(link)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return soup
