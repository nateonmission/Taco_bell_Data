import os
import time
import random
from urllib.parse import urlparse
import json
from pathlib import Path
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs4


US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}


# BS4 Variables
BASE_URL = "https://locations.tacobell.com"
OUT_DIR = "downloaded_pages"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; learning-project; +https://example.com/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
MIN_DELAY = 1.0   # seconds
MAX_DELAY = 3.0

session = requests.Session()
session.headers.update(HEADERS)


def polite_sleep():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def scrape_cities_for_state(state_abbr: str) -> list[str]:
    url = f"{BASE_URL}/{state_abbr.lower()}.html"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = bs4(resp.text, "lxml")

    cities = []

    for a in soup.select("a.DirLinks"):
        city = a.get('href')
        if city:
            cities.append(city)
    polite_sleep()
    return cities


def get_cities():
    atlas = {}
    for st, state in US_STATES.items():
        city_list = scrape_cities_for_state(st)
        atlas[st] = city_list
    return atlas


def get_stores(city_url):
    url = f"{BASE_URL}/{city_url.lower()}.html"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = bs4(resp.text, "lxml")

    stores = []

    for h2 in soup.find_all("h2"):
        for store in h2.find_all("a", href=True):
            if store:
                # print(store.get('href'))
                stores.append(store.get('href').replace("..", ""))
    polite_sleep()
    return stores


def main():
    atlas =get_cities()
    city_stores = {}
    for state, cities in atlas.items():
        city_stores[state] = {}
        for city in cities:
            if city:
                city_stores[state][city] = get_stores(city)
            # print(city_stores[state][city])
    with open("taco_bell_locations.json", "w", encoding="utf-8") as f:
        json.dump(city_stores, f, indent=2, ensure_ascii=False)
        
    print(city_stores["AL"]["al/mobile"])


if __name__ == "__main__":
    main()