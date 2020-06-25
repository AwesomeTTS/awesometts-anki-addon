#!/usr/bin/env python

"""
Retrieve Azure region list from web page
"""

import urllib
import urllib.request
from bs4 import BeautifulSoup

def main():
    url = 'https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech'
    
    response = urllib.request.urlopen(url)
    content = response.read()
    soup = BeautifulSoup(content, 'html.parser')

    tables = soup.find_all('table')
    region_table = tables[1]
    #print(region_table.prettify())
    rows = region_table.find('tbody').find_all('tr')
    for row in rows:
        # print(row.prettify())
        cells = row.find_all('td')
        geography = cells[0].string
        region = cells[1].string
        region_identifier = cells[2].string
        # print(region_identifier)

        print(f"('{region_identifier}', '{geography}, {region}'),")

    

if __name__ == '__main__':
    main()