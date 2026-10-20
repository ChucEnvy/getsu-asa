from bs4 import BeautifulSoup
import pandas as pd
from parsers.romaji import kana_to_roma


class PrefPostalLink:
    def __init__(self, pref, prefR, link):
        self.pref = pref
        self.prefR = prefR
        self.link = link

    def __repr__(self):
        # Pref, Prefecture Reading, Link
        return f'{self.pref},{self.prefR},{self.link}'

def get_pref_links(str):
    table_data = [] # Init empty set first

    soup = BeautifulSoup(str, "html.parser") # It will automatically use html.parser anyway
    # print("Raw: ", len(str), "; Soup: ", len(soup))

    """
    Under section.listing-card#prefectures:
    -> div.section-head: 
        Count of prefectures, municipalities, and area (for checking afterwards)
        ##都道府県    ####市区町村    ######町域
    -> div.generator-grid:
        Each prefecture section is wrapped in a "a" tag, containing:
            - Href link to the next page
            - Prefecture name inside <strong> tag
            - KANA name inside <span> tag
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
        prefR = kana_to_roma(a_tag.find("span", class_="generator-subtitle").text.strip())

        table_data.append(PrefPostalLink(pref, prefR, link))

    return pd.DataFrame([vars(link) for link in table_data])



class MuniPostalLink:
    def __init__(self, muni, muniR, link):
        self.muni = muni
        self.muniR = muniR
        self.link = link

    def __repr__(self):
        # Municipality, Municipality Reading, Link
        return f'{self.muni},{self.muniR},{self.link}'


def get_muni_links(str):
    table_data = [] # Init empty set first

    soup = BeautifulSoup(str, "html.parser") # It will automatically use html.parser anyway
    # print("Raw: ", len(str), "; Soup: ", len(soup))

    """
    Under section.summary-grid:
    -> 4 article tags, each containing:
        - Municipalities count  ###市区町村
        - Area count            ###町域
        - Postal code count     ###件
        - Updated date          更新日

    Under table.listing-table:
    -> thead -> tr -> th: 
        Title of the table, containing:
        市区町村    読み方  町域数  郵便番号数  代表コード
    -> tbody -> tr -> td:
        Each row contains:
        - Municipality name, link to the next page
        - Municipality reading in kana
        - Area count
        - Postal code count
        - Representative code
    """

    # Get the listing-table section
    listing_table = soup.find("table", class_="listing-table")
    tbody = listing_table.find("tbody")
    rows = tbody.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        muni = cols[0].text.strip()
        link = cols[0].find("a").get("href")
        muniR = kana_to_roma(cols[1].text.strip())

        table_data.append(MuniPostalLink(muni, muniR, link))

    table_frames = pd.DataFrame([vars(link) for link in table_data])

    return table_frames


class PostalCode:
    def __init__(self, address, addressKana, addressRoma, postal_code):
        self.address = address
        self.addressKana = addressKana
        self.addressRoma = addressRoma
        self.postal_code = postal_code

    def __repr__(self):
        # Address, Address Reading, Postal Code
        return f'{self.address},{self.addressKana},{self.addressRoma},{self.postal_code}'

def get_postal_codes(str):
    table_data = [] # Init empty set first

    soup = BeautifulSoup(str, "html.parser") # It will automatically use html.parser anyway
    # print("Raw: ", len(str), "; Soup: ", len(soup))

    """
    There are 2 sections in the page with the same tag structure: section.listing-card -> div.table-wrap
    #1: The area list with area names and postal code EXAMPLE, we skip this
    #2: The postal code list with address and postal code, we parse this

    Under section.listing-card -> div.table-wrap -> table.listing-table:
    -> thead -> tr -> th: 
        Title of the table, containing:
        郵便番号    住所    読み方
    -> tbody -> tr -> td:
        Each row contains:
        - Postal code: ###-####
        - Address (kanji)
        - Address reading in kana
    """

    # Get the listing-table section
    listing_table = soup.find_all("table", class_="listing-table")
    tbody = listing_table[1].find("tbody")  # Select the second table (postal code list)
    rows = tbody.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        postal_code = int(cols[0].text.replace("-", "").strip())
        address = cols[1].text.strip()
        addressKana = cols[2].text.strip()
        addressRoma = kana_to_roma(addressKana)

        table_data.append(PostalCode(address, addressKana, addressRoma, postal_code))

    table_frames = pd.DataFrame([vars(code) for code in table_data])

    return table_frames