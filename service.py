# -*- coding: utf-8 -*-
"""Fetches trade leads links, scrapes data for each link from HTML page, builds a single JSON
document, and stores it in S3 """
import datetime as dt
import json
import logging
import re
import xml.etree.ElementTree as ET

import boto3
import requests
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from lxml import etree


KEY = "australia.json"
BUCKET = "trade-leads"
JSON = "application/json"

MAIN_CONTENT = "html body div.wrapper div.pushmenu-push main#mainContent"
MAIN_CONTENT_v2 = "html body div.wrapper div.pushmenu-push div.main "

CONTAINER_DIV_ROW = f"{MAIN_CONTENT} div.container div.row"
CONTAINER_DIV_ROW_v2 = f"{MAIN_CONTENT_v2} div.container div.row"
INNER_DIV_LIST_DESC = "div.col-sm-8 div.box.boxW.listInner div.list-desc"

CONTACT_ROW_SELECTOR = "div.col-sm-4 div.pc div.box.boxB.boxY1 div"
CONTACT_OFFICER_SELECTOR = "p.contact-heading + p"
EMAIL_SELECTOR = "p a.email"
PHONE_SELECTOR = "//p[span[label[contains(text(),'Phone')]]]"

RSS_ENDPOINT = "https://www.tenders.gov.au/public_data/rss/rss.xml"
INPUT_FORMAT = "%d-%b-%Y %I:%M %p (ACT Local Time) Show close time for other time zones"
OUTPUT_FORMAT = "%Y-%m-%dT%H:%M:%S+10:00"
S3_CLIENT = boto3.client("s3")


def handler(event, context):
    response = True
    try:
        entries = list(get_trade_lead_links())
        S3_CLIENT.put_object(
            Bucket=BUCKET, Key=KEY, Body=json.dumps(entries), ContentType=JSON
        )
        print(f"✅ Uploaded {KEY} file with {len(entries)} locations")
    except (ClientError, ET.ParseError) as e:
        logging.error(e)
        response = False
    return response


def get_trade_lead_links():
    print("Fetching RSS feed of trade leads...")
    response = requests.get(RSS_ENDPOINT)
    root = ET.fromstring(response.text.encode("utf-8"))
    items = root.findall("./channel/item")
    print(f"Found {len(items)} trade lead links")
    for item in items:
        trade_lead_item = {
            "link": item.find("link").text,
            "pubDate": item.find("pubDate").text,
        }
        entry = get_entry(trade_lead_item)
        if entry:
            yield entry


def get_entry(trade_lead_item):
    tender_url = trade_lead_item["link"]
    print(f"Fetching {tender_url}")
    soup = get_soup(tender_url)
    if soup:
        try:
            row = soup.select(CONTAINER_DIV_ROW)[0]
        except IndexError:
            row = soup.select(CONTAINER_DIV_ROW_v2)[0]
        main_fields = row.select(INNER_DIV_LIST_DESC)
        tuples = [list_item.text.strip().splitlines() for list_item in main_fields]
        kv_dict = {
            get_key(tuple[0]): get_value(tuple[1:])
            for tuple in tuples
            if len(tuple) > 1
        }
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
    contact_row = row.select(CONTACT_ROW_SELECTOR)[0]

    contact_officer_field = contact_row.select(CONTACT_OFFICER_SELECTOR)
    if len(contact_officer_field) > 0:
        contact["contact_officer"] = contact_officer_field[0].text

    email_field = contact_row.select(EMAIL_SELECTOR)
    if len(email_field) > 0:
        contact["email"] = email_field[0].text

    contact_row_etree = etree.HTML(str(contact_row))
    phone_field = contact_row_etree.xpath(PHONE_SELECTOR)
    if len(phone_field) > 0:
        all_phone_text = phone_field[0].xpath("string()").strip()
        phone = re.sub("Phone:", "", all_phone_text).strip()
        if phone_seems_reasonable(phone):
            contact["phone"] = phone

    return contact


def get_contact_info(p_entry):
    return "".join(p_entry.stripped_strings).split(":")


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
