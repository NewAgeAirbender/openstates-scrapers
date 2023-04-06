import logging
import attr
import json
import requests
from openstates.scrape import Scraper
from spatula import JsonPage, HtmlPage, URL

chamber_map = {"Council of Provinces": "upper", "Assembly": "lower"}


@attr.s(auto_attribs=True)
class PartialBill:
    title: str
    bill_num: str
    session: str
    date: str
    chamber: str


def graphql_query(data, link):
    return URL(
        link,
        timeout=30,
        method="POST",
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps(data),
        verify=False,
    )


def get_page_source(session, source_num, link):
    return graphql_query(
        {
            "query": '{"keyword":null,"committee":null,"year":"' + session + '"}',
            "bill_status": source_num,
        },
        link,
    )


class BillDetailPage(HtmlPage):
    example_source = "https://www.parliament.gov.za/bill/2308132"

    def process_page(self):
        b = self.input
        page = self.root
        print(b, page)


class BillList(JsonPage):
    def process_page(self):
        data = self.response.json().get("bills")
        for bill in data:
            title = bill["name"]
            bill_num = bill["bill_no_number"]
            session = bill["bill_no_year"]
            date = bill["introduced_date"]
            link_num = bill["id"]
            chamber = bill["status"]

            b = PartialBill(title, bill_num, session, date, chamber)
            link = f"https://www.parliament.gov.za/bill/{link_num}"
        yield BillDetailPage(b, link)


class Assembly(BillList):
    source = get_page_source("2023", 1, "https://www.parliament.gov.za/bills")


class Council(BillList):
    source = get_page_source("2023", 2, "https://www.parliament.gov.za/bills")


class Sent(BillList):
    source = get_page_source("2023", 6, "https://www.parliament.gov.za/bills-passed")


class Passed(BillList):
    source = get_page_source("2023", 7, "https://www.parliament.gov.za/bills-passed")


class ZABillScraper(Scraper):
    def scrape(self, session=None):
        self.raise_errors = False
        self.retry_attempts = 1
        self.retry_wait_seconds = 3
        requests.Session()
        requests.Session.cookies.set_cookie()

        # spatula's logging is better than scrapelib's
        logging.getLogger("scrapelib").setLevel(logging.WARNING)
        yield from Assembly.do_scrape()
