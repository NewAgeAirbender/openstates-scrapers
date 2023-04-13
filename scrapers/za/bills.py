import logging
import json
import requests
from openstates.scrape import Bill, Scraper
from spatula import JsonListPage, HtmlPage, URL

chamber_map = {"National Council of Provinces": "upper", "National Assembly": "lower"}


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
    input_type = Bill
    example_input = Bill(
        "B7",
        "2023",
        "[title]",
        chamber="lower",
        classification="bill",
    )
    example_source = "https://www.parliament.gov.za/bill/2308132"

    def get_source_from_input(self):
        return URL(self.input.sources[0]["url"], verify=False, timeout=30)

    def process_page(self):
        b = self.input
        page = self.root

        abstract = (
            page.xpath('//*[@id="content"]/div[1]/text()')[0]
            .replace("\r\n", "")
            .strip()
        )
        b.add_abstract(abstract, note="summary")

        versions = page.xpath('//*[@id="versions"]/table/tbody/tr')
        for version in versions:
            name = version.xpath("td[2]/a/button/text()")[0]
            link = version.xpath("td[2]/a/@href")[0]
            date = version.xpath("td[3]/text()")[0]
            b.add_version_link(name, link, media_type="application/pdf", date=date)

        sponsor = page.xpath('//*[@id="versions"]/p/text()')[0].strip()
        b.add_sponsorship(
            sponsor,
            classification="primary",
            entity_type="person",
            primary=True,
        )
        return b


class BillList(JsonListPage):
    def process_item(self, item):
        for bill in self.data["bills"]:
            title = bill["name"]
            bill_id = bill["bill_no_number"]
            session = bill["bill_no_year"]
            link_num = bill["id"]

            b = Bill(
                bill_id,
                session,
                title,
                chamber="lower" if bill["bill_status"][1] == "A" else "upper",
                classification="bill",
            )
            link = f"https://www.parliament.gov.za/bill/{link_num}"
            b.add_source(link, note="homepage")
            yield BillDetailPage(b)


class Assembly(BillList):
    # def get_source_from_input(self):
    #     return get_page_source('2023', 1, 'https://www.parliament.gov.za/bills')
    source = get_page_source("2023", 1, "https://www.parliament.gov.za/bills")


class Council(BillList):
    source = get_page_source("2023", 2, "https://www.parliament.gov.za/bills")


class Sent(BillList):
    source = get_page_source("2023", 6, "https://www.parliament.gov.za/bills-passed")


class Passed(BillList):
    source = get_page_source("2023", 7, "https://www.parliament.gov.za/bills-passed")


class ZABillScraper(Scraper):
    def scrape(self):
        self.raise_errors = False
        self.retry_attempts = 1
        self.retry_wait_seconds = 3
        requests.Session()
        requests.Session.cookies.set_cookie()

        # spatula's logging is better than scrapelib's
        logging.getLogger("scrapelib").setLevel(logging.WARNING)
        bill_list = Assembly()
        yield from bill_list.do_scrape()
