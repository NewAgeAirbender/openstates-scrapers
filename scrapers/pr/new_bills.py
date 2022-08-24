# import re
# import lxml.html
# import datetime
# import requests
# import pytz
# from openstates.scrape import Scraper, Bill, VoteEvent as Vote
from spatula import HtmlListPage, XPath


class SenadoBillList(HtmlListPage):
    selector = XPath("//a[contains(@href, '/Session/Bill/')]")
    next_page_selector = XPath("//a[@class='next']/@href")
