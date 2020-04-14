import xml

import vcr

from service import get_soup, get_trade_lead_links, handler


@vcr.use_cassette()
def test_get_trade_lead_links():
    """Reads from the `test_get_trade_lead_links` cassette and processes the entries. Tests that
    multiple HTML pages get read correctly.

    """
    entries = list(get_trade_lead_links())
    assert len(entries) == 101
    assert entries[0] == {
        "atm_id": "SPC 3773",
        "agency": "Australian Taxation Office",
        "category": "80131500 - Lease and rental of property or building",
        "close_date_time": "2020-04-15T10:00:00+10:00",
        "publish_date": "Mon, 16 Mar 2020 13:00:00 GMT",
        "location": "ACT",
        "atm_type": "Expression of Interest",
        "multi_agency_access": "No",
        "panel_arrangement": "No",
        "multistage": "Yes",
        "multistage_criteria": "As defined in the Request documentation.",
        "description": "Colliers International, on behalf of the Australian Taxation Office ("
                       "ATO), invites potential suppliers to submit a submission for a "
                       "multi-stage procurement for the provision of leased office accommodation "
                       "for:  The location parameters within Canberra Net Lettable Area (NLA) "
                       "of\xa0 approximately 32,000m2 Lease term of ten (10) years with two (2) "
                       "by five (5) year options.",
        "other_instructions": "The Request documentation for this procurement opportunity can be "
                              "obtained from Colliers Tenderlink portal at "
                              "https://www.tenderlink.com/colliersinternational/. Addendum to the "
                              "Request documentation will also be made available via Tenderlink. "
                              "Tenderers are required to log in to Tenderlink and collect "
                              "addendum as notified.  The ATO will accept no responsibility if a "
                              "Tenderer fails to become aware of any addendum which would have "
                              "been apparent from a visit to the Tenderlink page for this "
                              "procurement activity.",
        "conditions_for_participation": "The Request documentation for this procurement activity "
                                        "contains Conditions of Participation and Minimum Content "
                                        "and Format Requirements. Tenderers are reminded that "
                                        "subject to clarification for unintentional errors or "
                                        "errors in form, Submissions that do not meet the "
                                        "Conditions of Participation and Minimum Content and "
                                        "Format Requirements will be excluded from further "
                                        "consideration.",
        "timeframe_for_delivery": "As defined in the Request documentation",
        "address_for_lodgement": "As defined in the Request documentation.",
        "tender_url": "https://www.tenders.gov.au/Atm/Show/4404e5d3-13ab-43ce-94bb-7e9c41947fe9",
        "uuid": "s://www.tenders.gov.au/Atm/Show/4404e5d3-13ab-43ce-94bb-7e9c41947fe9",
        "title": "Expression of Interest - Leased Office Accommodation - Canberra",
        "contact_officer": "Contact Details",
        "email": "WoAG.Leasing@colliers.com",
    }


@vcr.use_cassette()
def test_get_soup_returns_none_on_failure():
    nonsense_url = "http://google.com/nope-45404958-f3fa-4ed5-82b0-ee37043aed6f.html"
    assert get_soup(nonsense_url) is None


def test_handler_handles_parse_error(mocker):
    """Ensures any XML parsing issues from garbage input get ignored"""
    mocker.patch('service.get_trade_lead_links', side_effect=xml.etree.ElementTree.ParseError)
    assert handler(None, None) is False
