# -*- coding: utf-8 -*-
"""Fetches trade leads links, scrapes data for each link from HTML page, builds a single JSON
document, and stores it in S3 """
import datetime as dt
import json
import re
import xml.etree.ElementTree as ET

import boto3
import requests
from bs4 import BeautifulSoup

KEY = "australia.json"
BUCKET = "trade-leads"
DIV_CONTACT_P = "div.col-sm-4 div.pc div.box.boxB.boxY1 div.contact p"
DIV_CONTACT_LONG_P = DIV_CONTACT_P.replace("contact", "contact-long")
INNER_DIV_LIST_DESC = "div.col-sm-8 div.box.boxW.listInner div.list-desc"
CONTAINER_DIV_ROW = "html body div div.pushmenu-push div.main div.container div.row"
RSS_ENDPOINT = "https://www.tenders.gov.au/public_data/rss/rss.xml"
INPUT_FORMAT = "%d-%b-%Y %I:%M %p (ACT Local Time) Show close time for other time zones"
OUTPUT_FORMAT = "%Y-%m-%dT%H:%M:%S+10:00"
LONG_CONTACT_NAME_INDEX = 0
REGULAR_CONTACT_NAME_INDEX = 1
S3_CLIENT = boto3.resource("s3")


def handler(event, context):
    entries = list(get_trade_lead_links())
    if entries:
        S3_CLIENT.Object(BUCKET, KEY).put(Body=json.dumps(entries), ContentType="application/json")
        return f"Uploaded {KEY} to {BUCKET} bucket with {len(entries)} trade leads"
    else:
        return f"No entries loaded from {RSS_ENDPOINT} so there is no JSON file to upload"


def get_trade_lead_links():
    print("Fetching RSS feed of trade leads...")
    response = requests.get(RSS_ENDPOINT)
    root = ET.fromstring(response.text.encode("utf-8"))
    items = root.findall("./channel/item")
    print(f"Found {len(items)} trade lead links")
    for item in items:
        trade_lead_item = {"link": item.find("link").text, "pubDate": item.find("pubDate").text}
        entry = get_entry(trade_lead_item)
        if entry:
            yield entry


def get_entry(trade_lead_item):
    tender_url = trade_lead_item["link"]
    print(f"Fetching {tender_url}")
    soup = get_soup(tender_url)
    if soup:
        row = soup.select(CONTAINER_DIV_ROW)[0]
        main_fields = row.select(INNER_DIV_LIST_DESC)
        tuples = [list_item.text.strip().splitlines() for list_item in main_fields]
        kv_dict = {get_key(tuple[0]): get_value(tuple[1:]) for tuple in tuples if len(tuple) > 1}
        entry = {k: v for k, v in kv_dict.items() if field_value_seems_reasonable(v)}
        uuid_index = tender_url.find("UUID=") + 5
        misc_fields = {
            "close_date_time": parse_close_date_time(entry["close_date_time"]),
            "tender_url": tender_url,
            "publish_date": trade_lead_item["pubDate"],
            "uuid": tender_url[uuid_index:],
            "title": row.select(".lead")[0].text,
        }
        entry.update(misc_fields)
        contact = get_contact(row)
        entry.update(contact)
        return entry


def parse_close_date_time(close_date_time):
    return dt.datetime.strptime(close_date_time, INPUT_FORMAT).strftime(OUTPUT_FORMAT)


def get_contact(row):
    contact = {}
    contact_fields, contact_name_index = parse_contact_formats(row)

    contact_officer = contact_fields[contact_name_index].text
    if contact_officer:
        contact["contact_officer"] = contact_officer

    remaining_fields_index = contact_name_index + 1
    phone_email_etc_list = [
        get_contact_info(p_entry) for p_entry in contact_fields[remaining_fields_index:]
    ]
    phone_email_etc_hash = {
        contact_tuple[0]: contact_tuple[1] for contact_tuple in phone_email_etc_list
    }
    phone = phone_email_etc_hash["P"]
    if phone_seems_reasonable(phone):
        contact["phone"] = phone

    email = phone_email_etc_hash["E"]
    if email:
        contact["email"] = email

    return contact


def get_contact_info(p_entry):
    return "".join(p_entry.stripped_strings).split(":")


def parse_contact_formats(row):
    contact_fields = row.select(DIV_CONTACT_P)
    contact_name_index = REGULAR_CONTACT_NAME_INDEX
    if len(contact_fields) == 0:
        contact_fields = row.select(DIV_CONTACT_LONG_P)
        contact_name_index = LONG_CONTACT_NAME_INDEX
    return contact_fields, contact_name_index


def phone_seems_reasonable(phone):
    return re.search("[1-9]", phone)


def field_value_seems_reasonable(value):
    return value and not (value == "Nil")


def get_key(key_string):
    return "_".join(re.sub("[^a-z ]", "", key_string.lower()).split())


def get_value(values):
    value = " ".join(values).strip()
    return value


def get_soup(link):
    response = requests.get(link, allow_redirects=False)
    if response.status_code != 200:
        print(f"Got status code {response.status_code} from response for link {link}")
        return None
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return soup
