# travel_scraper.py
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def search_hotel_links(destination, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"hotels in {destination} site:booking.com", max_results=max_results))
        return [r['href'] for r in results if 'booking.com' in r['href']]
    except Exception as e:
        return []

def scrape_hotel_details(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.title.text.strip() if soup.title else "No title"
        snippet = soup.find('meta', {'name': 'description'})
        desc = snippet['content'].strip() if snippet else "No description available"

        return {
            "name": title,
            "description": desc,
            "url": url
        }
    except Exception as e:
        return {"name": "Error", "description": str(e), "url": url}

def scrape_hotels(destination, check_in, check_out):
    links = search_hotel_links(destination)
    hotels = [scrape_hotel_details(link) for link in links]
    return hotels
