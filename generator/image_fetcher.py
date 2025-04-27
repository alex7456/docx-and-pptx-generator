import requests
import json
import urllib.parse
from bs4 import BeautifulSoup

TOPIC_TRANSLATIONS = {
    "горы": "mountains", "космос": "space", "море": "sea", "океан": "ocean",
    "животные": "animals", "человек": "human", "природа": "nature", "город": "city",
    "архитектура": "architecture", "история": "history", "техника": "technology",
    "наука": "science", "музыка": "music", "спорт": "sport", "еда": "food"
}

def fetch_image_urls_bing(query, count):
    search_term = TOPIC_TRANSLATIONS.get(query.lower(), query)
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(search_term)}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_tags = soup.find_all("a", class_="iusc")

    urls = []
    for tag in image_tags:
        try:
            m_json = json.loads(tag.get("m"))
            img_url = m_json["murl"]
            if img_url.endswith((".jpg", ".jpeg", ".png")):
                urls.append(img_url)
            if len(urls) >= count:
                break
        except:
            continue
    return urls
