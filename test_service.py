import xml

import vcr

from service import get_soup, get_trade_lead_links, handler


@vcr.use_cassette()
def test_get_trade_lead_links():
    """Reads from the `test_get_trade_lead_links` cassette and processes the entries. Tests that
    multiple HTML pages get read correctly.

    """
    entries = list(get_trade_lead_links())
    assert len(entries) == 102
    assert entries[0] == {
        "atm_id": "RFT 1-2020",
        "agency": "Australian Federal Police",
        "category": "43230000 - Software",
        "close_date_time": "2020-05-06T11:00:00+10:00",
        "publish_date": "Thu, 13 Feb 2020 13:00:00 GMT",
        "location": "Canberra",
        "atm_type": "Request for Tender",
        "multi_agency_access": "Yes",
        "multi_agency_access_type": "All Agencies",
        "panel_arrangement": "No",
        "multistage": "No",
        "description": "The AFP seeks responses from suitably qualified and experienced Tenderer"
                       "(s) for the provision of a software and support services solution that "
                       "will enable the AFP to maintain an Organisational Health Record for all AFP"
                       " Personnel.",
        "other_instructions": "An industry briefing will be held at 11am on Wednesday 26/2/20.",
        "conditions_for_participation": "The AFP will exclude a Tender from further consideration"
                                        " if it considers that, at the time of lodgement of the "
                                        "Tender, the Tenderer: (a)     does not exist as a legal "
                                        "entity at the time of lodgement of the Tender; (b)      is"
                                        " not solvent or financially viable; (c)      does not hold"
                                        " an Authorisation necessary for it to be able to perform "
                                        "the Services tendered for in accordance with applicable "
                                        "laws; or (d)     does not:    (i)       hold a Valid and "
                                        "Satisfactory Statement of Tax Record by the Closing Time; "
                                        "or    (ii)      have a receipt demonstrating that a State"
                                        "ment of Tax Record has been requested from the Australian "
                                        "Taxation Office by the Closing Time, and holds a Valid and"
                                        " Satisfactory Statement of Tax Record no later than 4 Busi"
                                        "ness Days from the Closing Time; and    (iii)     does not"
                                        " hold a Valid and Satisfactory Statement of Tax Record for"
                                        " any first tier subcontractor that it proposes, as part of"
                                        " its Tender, to engage to deliver the Services with an est"
                                        "imated value of over $4 million (GST inclusive).",
        "timeframe_for_delivery": "by September 2020",
        "estimated_value_aud": "From to",
        "address_for_lodgement": "Tenders must be lodged electronically via the AusTender, at "
        "https://www.tenders.gov.au before the Closing Time and in accordance with the Tender lodge"
        "ment procedures set out in this RFT and on AusTender.",
        "addenda_available": "View Addenda",
        "tender_url": "https://www.tenders.gov.au/Atm/Show/8d362bc7-2b95-4892-8b06-6e82f694788e",
        "uuid": "s://www.tenders.gov.au/Atm/Show/8d362bc7-2b95-4892-8b06-6e82f694788e",
        "title": "Provision of an Organisational Health Solution",
        "contact_officer": "Heath Galer",
        "email": "AFP-RFT@afp.gov.au"
    }


@vcr.use_cassette()
def test_get_soup_returns_none_on_failure():
    nonsense_url = "http://google.com/nope-45404958-f3fa-4ed5-82b0-ee37043aed6f.html"
    assert get_soup(nonsense_url) is None


def test_handler_handles_parse_error(mocker):
    """Ensures any XML parsing issues from garbage input get ignored"""
    mocker.patch('service.get_trade_lead_links', side_effect=xml.etree.ElementTree.ParseError)
    assert handler(None, None) is False
