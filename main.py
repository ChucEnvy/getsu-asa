import requests
from bs4 import BeautifulSoup
import pandas as pd


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

    table_data = []
    response = requests.get(base_url, params=params)
    response.encoding = response.apparent_encoding
    print(response)

    soup = BeautifulSoup(response.text, "html.parser") # It will automatically use html.parser anyway
    print(len(soup))

    pref_boxes = soup.find_all("div", class_="table_box")

    print(len(pref_boxes))

    # Each table_box is a div, include the html table for todofuken in this format:
    #	都道府県	政令市/郡	自治体名等	ふりがな
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
    print(todofuken_search())


main()