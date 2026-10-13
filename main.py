import requests
from bs4 import BeautifulSoup
import pandas as pd

from parsers.romaji import hira_to_roma


def todofuken_search():
    base_url = "https://uub.jp/ctv/search.cgi"
    params = {
        "L": "kanni",
        "Pa": "全国",
        "B": "最新",
        "P": "1",
        "C": "1",
        "T": "1",
        "V": "1",
        "U": "1",
        "K": "1",
        "Dn": "1",
        "Dp": "1",
        "Dg": "1",
        "Df": "1",
        "Rp": "1",
        "R": "stan",
        "A": "all",
        "M": "part"
    }

    response = requests.get(base_url, params=params)
    response.encoding = response.apparent_encoding

    return response.text


def parse_result(str):
    table_data = [] # Init empty set first

    soup = BeautifulSoup(str, "html.parser") # It will automatically use html.parser anyway
    print("Raw: ", len(str), "; Soup: ", len(soup))

    pref_boxes = soup.find_all("div", class_="table_box")
    print("Pref_boxes: ", len(pref_boxes))

    """
    Each table_box is a div, include the html table for todofuken in this format:
    	都道府県	政令市/郡	自治体名等	ふりがな
    Every prefecture will have "県" in it, with the exception of Hokkaido
    """
    for pref_box in pref_boxes:
        table = pref_box.find("table")
        if not table:
            continue

        headers = []
        
        rows = table.find_all('tr')
        if not rows:
            continue

        header_row = rows[0]
        headers = [header.text.strip() for header in header_row.find_all(['th', 'td'])]

        for row in rows[1:]:
            cols = row.find_all('td')

            if not cols:
                continue

            row_values = [col.text.strip() for col in cols]

            row_dict = dict(zip(headers, row_values))
            table_data.append(row_dict)

    return pd.DataFrame(table_data)

def main():
    with open("raws/todofuken.html") as file:
        parse_result(file.read())

    
    # print(todofuken_search())


main()


"""
    ON THE SECOND THOUGHTS:
    Since this is only the prefecture area, 
    it would be quite hard to pin point the area where the user would like to search,
    and the trash collection schedule will change as small as postal code level,
    it would be better to also have the postal code search.

    (I'm still thinking on the way to implement the postal code list stuff, since there
    is no exact list of postal code atm, at least not that I can find.
    Considering using this site: 
    https://postaljp.com/

    The data is structured quite well, and we can access the entire list of postal code
    of each municipalities using url like this: https://postaljp.com/aichiken/amashi/
    )

"""