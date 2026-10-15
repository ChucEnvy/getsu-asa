import requests

from parsers.romaji import hira_to_roma
from parsers.postalParser import get_muni_links, get_pref_links


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
    sample_text = None
    filename = 'results/links.csv'

    with open("raws/postaljp_aichiken.html") as file:
        sample_text = file.read()
    
    # postal_search = search("https://postaljp.com/")

    # links = get_pref_links(sample_text)
    # links.to_csv(filename, index=False, header=['pref', 'prefR', 'link'])

    links = get_muni_links(sample_text)
    links.to_csv(filename, index=False, header=['muni', 'muniR', 'link'])



main()
