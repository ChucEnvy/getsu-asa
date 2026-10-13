from bs4 import BeautifulSoup
import pandas as pd
import re
from parsers.romaji import hira_to_roma


class PostalLink:
    def __init__(self, pref, romaji, muniCount, areaCount, postalCount, link):
        self.pref = pref
        self.romaji = romaji
        self.muniCount = muniCount
        self.areaCount = areaCount
        self.postalCount = postalCount
        self.link = link

    def __repr__(self):
        # Pref, Romaji, Municipalities, Areas, Postal Codes, Link
        return f'{self.pref},{self.romaji},{self.muniCount},{self.areaCount},{self.postalCount},{self.link}'

def get_links(str):
    table_data = [] # Init empty set first

    soup = BeautifulSoup(str, "html.parser") # It will automatically use html.parser anyway
    print("Raw: ", len(str), "; Soup: ", len(soup))

    """
    Under section.listing-card#prefectures:
    -> div.section-head: 
        Count of prefectures, municipalities, and area (for checking afterwards)
        ##都道府県    ####市区町村    ######町域
    -> div.generator-grid:
        Each prefecture section is wrapped in a "a" tag, containing:
            - Href link to the next page
            - Prefecture name inside <strong> tag
            - HIRAGANA name inside <span> tag
            - Municipalities count  ###市区町村
            - Area count            ###町域
            - Postal code count     ###件
    """

    # Main content
    listing_card = soup.find("section", class_="listing-card", id="prefectures")

    # Header
    section_head = listing_card.find("div", class_="section-head")
    if not section_head:
        # Mission aborted, no data found
        print("No section_head found")
        return None
    
    pref_section = re.search(r'([\d,])+都道府県', section_head.text)
    pref_count = pref_section.group(0).replace(",", "").replace("都道府県", "")

    muni_section = re.search(r'([\d,])+市区町村', section_head.text)
    muni_count = muni_section.group(0).replace(",", "").replace("市区町村", "")

    area_section = re.search(r'([\d,])+町域', section_head.text)
    area_count = area_section.group(0).replace(",", "").replace("町域", "")

    # print(f"Prefectures: {pref_count}, Municipalities: {muni_count}, Areas: {area_count}")

    # Content
    generator_grid = listing_card.find("div", class_="generator-grid")
    if not generator_grid:
        # Mission aborted, no data found
        print("No generator_grid found")
        return None

    a_tags = generator_grid.find_all("a", class_="generator-card")
    for a_tag in a_tags:
        # print("A tag: ", a_tag)

        link = a_tag.get("href")
        pref = a_tag.find("strong").text.strip()
        romaji = hira_to_roma(a_tag.find("span", class_="generator-subtitle").text.strip())
        muniCount = int(a_tag.find("span", string=re.compile(r"市区町村")).text.replace(",", "").replace("市区町村", "").strip())
        areaCount = int(a_tag.find("span", string=re.compile(r"町域")).text.replace(",", "").replace("町域", "").strip())
        postalCount = int(a_tag.find("span", string=re.compile(r"件")).text.replace(",", "").replace("件", "").strip())

        table_data.append(PostalLink(pref, romaji, muniCount, areaCount, postalCount, link))

    table_frames = pd.DataFrame([vars(link) for link in table_data])
    print(f"Prefectures: {pref_count}, Municipalities: {muni_count}, Areas: {area_count}")
    print(f"Table Prefectures: {len(table_frames)}, Municipalities: {table_frames['muniCount'].sum()}, Areas: {table_frames['areaCount'].sum()}")
    
    if len(table_frames) != int(pref_count) or table_frames['muniCount'].sum() != int(muni_count) or table_frames['areaCount'].sum() != int(area_count):
        print("[WARN] Data mismatch found")
    else:
        print("[INFO] Data matches")

    return table_frames