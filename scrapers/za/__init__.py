from openstates.scrape import State
from .bills import ZABillScraper


class SouthAfrica(State):
    scrapers = {
        "bills": ZABillScraper,
    }
    legislative_sessions = [
        {
            "classification": "primary",
            "identifier": "2023",
            "name": "2023 Session",
            "start_date": "2023-01-01",
            "end_date": "2023-12-02",
            "active": True,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        return ["2023"]
