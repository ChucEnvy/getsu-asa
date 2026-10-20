# Auto scraper for postaljp.com

import requests
import pandas as pd
from parsers.postalParser import get_muni_links, get_postal_codes, get_pref_links

BASE_URL = "https://postaljp.com/"

class CompletePostalCode:
    def __init__(self, prefecture, prefectureRoma, muni, muniRoma, address, addressKana, addressRoma, postal_code):
        self.prefecture = prefecture
        self.prefectureRoma = prefectureRoma
        self.muni = muni
        self.muniRoma = muniRoma
        self.address = address
        self.addressKana = addressKana
        self.addressRoma = addressRoma
        self.postal_code = postal_code

def search_postal_codes():
    url = f"{BASE_URL}"

    # Step 1: Get the prefecture links
    pref_response = requests.get(url)

    if pref_response.status_code != 200:
        print(f"Error: {pref_response.status_code}")
        return None

    pref_response.encoding = pref_response.apparent_encoding

    pref_links = get_pref_links(pref_response.text)

    # Step 2: For each prefecture, get the municipality links
    complete_postal_codes = []
    for pref in pref_links.itertuples(index=False):
        print(f"Processing prefecture: {pref})")
        pref_url = f"{BASE_URL}{pref.link}"
        muni_response = requests.get(pref_url)

        if muni_response.status_code != 200:
            print(f"Error: {muni_response.status_code} for {pref_url}")
            continue

        muni_response.encoding = muni_response.apparent_encoding
        muni_links = get_muni_links(muni_response.text)

        # Step 3: For each municipality, get the postal codes
        for muni in muni_links.itertuples(index=False):
            muni_url = f"{BASE_URL}{muni.link}"
            postal_response = requests.get(muni_url)

            if postal_response.status_code != 200:
                print(f"Error: {postal_response.status_code} for {muni_url}")
                continue

            postal_response.encoding = postal_response.apparent_encoding
            postal_codes = get_postal_codes(postal_response.text)

            # Step 4: Combine all data into CompletePostalCode objects
            for code in postal_codes.itertuples(index=False):
                complete_postal_codes.append(
                    CompletePostalCode(
                        pref.pref,
                        pref.prefR,
                        muni.muni,
                        muni.muniR,
                        code.address,
                        code.addressKana,
                        code.addressRoma,
                        code.postal_code
                    )
                )

            # Quick log
            print(f"---> Processed {len(postal_codes)} postal codes for {muni.muni} in {pref.pref}")

        # break  # Remove this break to process all prefectures


    return pd.DataFrame([vars(code) for code in complete_postal_codes])
