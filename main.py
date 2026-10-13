import requests

from parsers.romaji import hira_to_roma
from parsers.postalParser import get_links


def search(base_url, param = None):
    url = f"{base_url}"
    response = requests.get(url, params=param)

    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None



def main():
    links = []

    # with open("raws/postalcode.html") as file:
    #     links = get_links(file.read())
    #     pprint.pprint(links, width=200)

    postal_search = search("https://postaljp.com/")
    links = get_links(postal_search)

    filename = 'results/links.csv'
    links.to_csv(filename, index=False, header=['pref', 'romaji', 'muniCount', 'areaCount', 'postalCount', 'link'])


main()
