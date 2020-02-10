import vcr

from service import get_trade_lead_links, get_soup


@vcr.use_cassette()
def test_get_trade_lead_links():
    """Reads from the `test_get_trade_lead_links` cassette and processes the entries. Tests that
    multiple HTML pages get read correctly.

    """
    entries = list(get_trade_lead_links())
    assert len(entries) == 126
    assert entries[0] == {
        "atm_id": "165A-2019-20",
        "agency": "Bureau of Meteorology",
        "category": "78100000 - Mail and cargo transport",
        "close_date_time": "2020-02-11T12:00:00+10:00",
        "publish_date": "Mon, 13 Jan 2020 13:00:00 GMT",
        "location": "QLD",
        "atm_type": "Request for Tender",
        "multi_agency_access": "No",
        "panel_arrangement": "Yes",
        "multistage": "No",
        "description": "Provision of shipping services to Willis Island",
        "conditions_for_participation": "is not a joint Tenderer.",
        "timeframe_for_delivery": "As required over a period of five years commencing May 2020.",
        "address_for_lodgement": "www.tenders.gov.au",
        "tender_url": "https://www.tenders.gov.au/Atm/Show/45404958-f3fa-4ed5-82b0-ee37043aed6f",
        "uuid": "s://www.tenders.gov.au/Atm/Show/45404958-f3fa-4ed5-82b0-ee37043aed6f",
        "title": "Deed of Standing Offer for Shipping Services to Willis Island",
        "contact_officer": "Ray Martin",
        "email": "tenders@bom.gov.au",
    }


@vcr.use_cassette()
def test_get_soup_returns_none_on_failure():
    assert get_soup("http://google.com/nope-45404958-f3fa-4ed5-82b0-ee37043aed6f.html") is None
