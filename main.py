import timeit

import requests

from crawlers.postalCode import search_postal_codes
from parsers.postalParser import get_muni_links, get_postal_codes, get_pref_links


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

    # with open("raws/postaljp_aichiken_amashi.html") as file:
    #     sample_text = file.read()
    
    # postal_search = search("https://postaljp.com/")

    # links = get_pref_links(sample_text)
    # links.to_csv(filename, index=False, header=['pref', 'prefR', 'link'])

    # links = get_postal_codes(sample_text)
    # links.to_csv(filename, index=False, header=['address', 'addressKana', 'addressRoma', 'postal_code'])
    
    print("Starting postal code search...")
    exec_time = timeit.default_timer()
    complete_postal_codes = search_postal_codes()
    exec_time = timeit.default_timer() - exec_time
    print(f"Postal code search completed in {exec_time:.3f} seconds.")

    if complete_postal_codes.size > 0:
        complete_postal_codes.to_csv('results/complete_postal_codes.csv', index=False, header=['prefecture', 'prefectureRoma', 'muni', 'muniRoma', 'address', 'addressKana', 'addressRoma', 'postal_code'])
        print("Complete postal codes saved to 'results/complete_postal_codes.csv'. Total records: ", len(complete_postal_codes))
    else:
        print("No postal codes found.")


main()
