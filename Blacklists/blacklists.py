import requests
import csv
import io
from bs4 import BeautifulSoup
import os

# First blacklist: https://urlhaus.abuse.ch
def check_blacklist1(url): 
    try:
        response = requests.get('https://urlhaus.abuse.ch/downloads/csv_online/')
        # Raises an HTTPError if the HTTP request was unsuccessful
        response.raise_for_status()
        csv_data = csv.reader(io.StringIO(response.text))
        next(csv_data, None)
        for row in csv_data:
            if len(row) > 2 and url == row[2]:
                return 1
        return -1 
    except Exception as e:
        return e

# Second blacklist: https://db.aa419.org/fakebankslist.php
def check_blacklist2(url):
    # API endpoint and headers
    api_endpoint = "https://api.aa419.org/fakesites"
    # Get the key stored in an environment variable
    api_key = os.environ.get('blacklists2_key')
    if not api_key:
        raise Exception("API key not found")
    headers = {'Auth-API-Id': api_key}
    # Maximum umber of results to fetch per page
    page_size = 500
    # Starting page number
    page_number = 0
    # Number of pages to check
    max_pages = 10
    try:
        # Loop through the pages until the maximum number is reached
        while page_number < max_pages:
            params = {'fields': 'Url', 'pgsize': page_size, 'pgno': page_number}
            response = requests.get(api_endpoint, headers=headers, params=params)
            response.raise_for_status()
            # Parse the JSON response
            data = response.json()
            for site in data:
                if url == site.get('Url'):
                    return 1  # URL is blacklisted
            if len(data) < page_size:
                break
            page_number += 1
        return -1
    except Exception as e:
        return e

# Third blacklist: https://phishstats.info/
def check_blacklist3(url):
    # API endpoint
    api_endpoint = "https://phishstats.info:2096/api/phishing"
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
        data = response.json()
        for record in data:
            if url == record['url']:
                return 1
        return -1
    except Exception as e:
        return e

# Fourth blacklist: https://github.com/mitchellkrogza/Phishing.Database/blob/master/phishing-links-ACTIVE-today.txt
def check_blacklist4(url):
    try:
        # URL of the raw content of the file
        blacklist = 'https://github.com/mitchellkrogza/Phishing.Database/raw/master/phishing-links-ACTIVE-today.txt'
        response = requests.get(blacklist)
        response.raise_for_status()
        urls = response.content.decode('utf-8').splitlines()
        for u in urls:
            if url == u:
                return 1
        return -1
    except Exception as e:
        return e

def check_blacklists(url):
    url = url.replace(' ', '').replace('\t', '')
    if url.endswith('/'):
        url = url[:-1]
    protocol, rest = url.split('://', 1)
    if rest.startswith('www.'):
        # Remove 'www.'
        url2 = f'{protocol}://{rest[4:]}'
    else:
        # Add 'www.'
        url2 = f'{protocol}://www.{rest}'
    # If one of them gives an error, ignore it
    blacklist_functions = [check_blacklist1, check_blacklist2, check_blacklist3, check_blacklist4]
    for func in blacklist_functions:
        try:
            if func(url) == 1 or func(url2) == 1:
                return 'P'
        except Exception as e:
            return e
    return 'L'
