import re
from urllib.parse import urlparse, urljoin
import tldextract
import requests
import ssl
import time
import OpenSSL
import socket
from datetime import datetime, timedelta
import whois
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pickle
import sys
phishing_model_path = os.path.join(os.path.dirname(__file__), '..', 'RandomForest')
sys.path.append(phishing_model_path)
from randomForest import bagging_predict
import json

#1
def url_has_ip(url):
    ip_pattern = r'https?://(\d{1,3}\.){3}\d{1,3}/'
    ip_pattern_hex = r'https?://(0x[0-9A-Fa-f]{1,2}\.|[0-9]{1,3}\.){3}(0x[0-9A-Fa-f]{1,2}|[0-9]{1,3})/'
    ip = re.match(ip_pattern, url)
    ip_hex = re.match(ip_pattern_hex, url)
    if ip or ip_hex:
        return 1
    else:
        return -1

#2
def has_long_url(url):
    if len(url) < 54:
        return -1
    elif len(url) >= 54 and len(url) <= 75:
        return 0
    else:
        return 1

#3
def has_shortening_service(url):
    shortening_services = ['t.ly', 'bit.ly', 'is.gd', 'v.gd', 'ow.ly', '3.ly', 'tinyurl.com', 'clicky.me', 'bl.ink', 'buff.ly', 'rebrandly.com', 't2m.io', 'cutt.ly', 'shorturl.at', 'urlzs.com', 'linksplit.io', 'short.io', 'kutt.io', 'switchy.io', 'gg.gg', 'urlr.me', 'name.com', 'han.gl', 'bitly.kr', 'hoy.kr', 'vo.la', 'oe.cd', 'lstu.fr', 'linkhuddle.com', 'kutt.it', 'lstu.fr', 'yourls.org', 'polr.org', 'shlink.io', 'pygmy.co', 'dub.sh', 'u.li2niu.com', 'goo.gl', 'me2.do', 's2r.co', 'cutit.org', 'soo.gd', 'tiny.cc', 'shorte.st', 'sniply.io', 'hopp.co', 'adf.ly', 'bit.do', 'mcaf.ee', 'su.pr']
    domain = urlparse(url).netloc
    if domain in shortening_services:
        return 1
    return -1

#4
def has_at_symbol(url):
    if '@' in url:
        return 1
    else:
        return -1

#5
def has_double_slash(url):
    pattern = '//'
    matches = re.findall(pattern, url)
    if len(matches) > 1:
        return 1
    else:
        return -1

#6
def has_dash(url):
    if '-' in url:
        return 1
    else:
        return -1

#7
def has_subdomain(url):
    ccTLD = ['.ac', '.ad', '.ae', '.af', '.ag', '.ai', '.al', '.am', '.ao', '.aq', '.ar', '.as', '.at', '.au', '.aw', '.ax', '.az', '.ba', '.bb', '.bd', '.be', '.bf', '.bg', '.bh', '.bi', '.bj', '.bl', '.bm', '.bn', '.bo', '.bq', '.br', '.bs', '.bt', '.bv', '.bw', '.by', '.bz', '.ca', '.cc', '.cd', '.cf', '.cg', '.ch', '.ci', '.ck', '.cl', '.cm', '.cn', '.co', '.cr', '.cu', '.cv', '.cw', '.cx', '.cy', '.cz', '.de', '.dj', '.dk', '.dm', '.do', '.dz', '.ec', '.ee', '.eg', '.eh', '.er', '.es', '.et', '.eu', '.fi', '.fj', '.fk', '.fm', '.fo', '.fr', '.ga', '.gb', '.gd', '.ge', '.gf', '.gg', '.gh', '.gi', '.gl', '.gm', '.gn', '.gp', '.gq', '.gr', '.gs', '.gt', '.gu', '.gw', '.gy', '.hk', '.hm', '.hn', '.hr', '.ht', '.hu', '.id', '.ie', '.il', '.im', '.in', '.io', '.iq', '.ir', '.is', '.it', '.je', '.jm', '.jo', '.jp', '.ke', '.kg', '.kh', '.ki', '.km', '.kn', '.kp', '.kr', '.kw', '.ky', '.kz', '.la', '.lb', '.lc', '.li', '.lk', '.lr', '.ls', '.lt', '.lu', '.lv', '.ly', '.ma', '.mc', '.md', '.me', '.mf', '.mg', '.mh', '.mk', '.ml', '.mm', '.mn', '.mo', '.mp', '.mq', '.mr', '.ms', '.mt', '.mu', '.mv', '.mw', '.mx', '.my', '.mz', '.na', '.nc', '.ne', '.nf', '.ng', '.ni', '.nl', '.no', '.np', '.nr', '.nu', '.nz', '.om', '.pa', '.pe', '.pf', '.pg', '.ph', '.pk', '.pl', '.pm', '.pn', '.pr', '.ps', '.pt', '.pw', '.py', '.qa', '.re', '.ro', '.rs', '.ru', '.rw', '.sa', '.sb', '.sc', '.sd', '.se', '.sg', '.sh', '.si', '.sj', '.sk', '.sl', '.sm', '.sn', '.so', '.sr', '.ss', '.st', '.sv', '.sx', '.sy', '.sz', '.tc', '.td', '.tf', '.tg', '.th', '.tj', '.tk', '.tl', '.tm', '.tn', '.to', '.tr', '.tt', '.tv', '.tw', '.tz', '.ua', '.ug', '.um', '.us', '.uy', '.uz', '.va', '.vc', '.ve', '.vg', '.vi', '.vn', '.vu', '.wf', '.ws', '.ye', '.yt', '.za', '.zm', '.zw']
    dot_count = url.count('.')
    page_domain = urlparse(url).netloc
    if page_domain[-3:] in ccTLD:
        dot_count -= 1
    if re.search(r'https?://www\.', url):
        dot_count -= 1
    if dot_count > 2:
        return 1
    elif dot_count > 1:
        return 0
    else:
        return -1

#8
def has_https(url):
    trusted_issuers = ['GeoTrust', 'Cloudflare', 'GoDaddy', 'Network Solutions', 'Thawte', 'Comodo', 'DigiCert', 'VeriSign', 'IdenTrust', 'Entrust', 'Sectigo', 'GlobalSign', 'GTS', 'AlphaSSL', 'Entrust', 'SSL.com', 'RapidSSL', 'Symantec']
    try:
        if url.startswith('http://'):
            return 1
        # Extract the hostname from the URL
        hostname = url.split('//')[-1].split('/')[0]
        # Establish a secure context
        context = ssl.create_default_context()
        # Create a connection to the host on port 443 (SSL port)
        with socket.create_connection((hostname, 443)) as sock:
            # Wrap the socket to add SSL support
            with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
                cert = ssl_sock.getpeercert(binary_form=True)
        # Load the certificate using OpenSSL
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
        # Extract the issuer's common name and the issued date
        issuer = x509.get_issuer().CN
        issued_date = datetime.strptime(x509.get_notBefore().decode('ascii'), '%Y%m%d%H%M%SZ')
        expiry_date = datetime.strptime(x509.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
        # Check if the issuer is trusted
        is_issuer_trusted = any(trusted_issuer in issuer for trusted_issuer in trusted_issuers)
        cert_age = expiry_date - issued_date
        is_cert_old_enough = cert_age.days >= 83
        if url.startswith('https://') and is_issuer_trusted and is_cert_old_enough:
            return -1
        elif url.startswith('https://') and not is_issuer_trusted:
            return 0
        else:
            return 1
    except Exception as e:
        # Display the results even in the unlikely case of a function failing
        return 0

#9
def domain_length(url):
    try:
        # Retrieve domain information
        domain_info = whois.whois(url)
        if domain_info.expiration_date is None:
            return 1
        # Handle case where multiple expiration dates are present
        if isinstance(domain_info.expiration_date, list):
            expiration_date = domain_info.expiration_date[0]
        else:
            expiration_date = domain_info.expiration_date
        if (expiration_date - datetime.now()).days < 60:
            return 1
        else:
            return -1
    except Exception as e:
        return 0

#10
def has_favicon(url, driver):
    try:
        # Find favicon elements in the page's HTML
        favicons = driver.find_elements(By.XPATH, "//link[@rel='icon' or @rel='shortcut icon' or @rel='apple-touch-icon'] | //meta[@name='msapplication-TileImage' or @name='msapplication-config']")
        # Check if there are no favicons found
        if not favicons:
            return -1
        for favicon in favicons:
            href = favicon.get_attribute('href')
            # Convert relative URLs to absolute URLs
            href_full = urljoin(url, href)
            if href_full:
                # Extract the domain from the page URL
                extracted = tldextract.extract(url)
                page_domain = "{}.{}".format(extracted.domain, extracted.suffix)
                # Extract the domain from the favicon URL
                extracted = tldextract.extract(href_full)
                favicon_domain = "{}.{}".format(extracted.domain, extracted.suffix)
                if favicon_domain != page_domain:
                    return 1
        return -1
    except Exception as e:
        return 0

#11
def check_port(url):
    # Dictionary of common ports and their preferred status
    common_ports = {21: 'Close', 22: 'Close', 23: 'Close', 80: 'Open', 443: 'Open', 445: 'Close', 1433: 'Close', 1521: 'Close', 3306: 'Close', 3389: 'Close'}
    # Parse the URL to extract the hostname
    hostname = urlparse(url).hostname
    # Function to check if a port is open
    def is_port_open(host, port):
        # Create a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            # connect_ex returns 0 if the connection is successul
            return s.connect_ex((host, port)) == 0
    # Check each port and determine legitimacy
    for port, status in common_ports.items():
        if is_port_open(hostname, port):
            actual_status = 'Open'
        else:
            actual_status = 'Close'
        if actual_status != status:
            return 1
    return -1

#12
def has_token(url):
    page_domain = urlparse(url).netloc
    if 'http' in page_domain:
        return 1
    else:
        return -1

#13
def has_request_url(url, driver):
    try:
        # Extract the domain from the page URL
        extracted = tldextract.extract(url)
        web_domain = "{}.{}".format(extracted.domain, extracted.suffix)
        # List of all possible tags and their attributes to check
        tag_attribute_pairs = [
            ("//img", "src"),
            ("//script", "src"),
            ("//link[@rel='stylesheet']", "href"),
            ("//video", "src"),
            ("//audio", "src"),
            ("//iframe", "src"),
            ("//object", "data"),
            ("//embed", "src"),
            ("//a[@href]", "href")
        ]
        total_resources = 0
        linked_ins = 0
        # Process each tag-attribute pair
        for tag, attribute in tag_attribute_pairs:
            elements = driver.find_elements(By.XPATH, tag)
            for elem in elements:
                resource_url = elem.get_attribute(attribute)
                if resource_url:
                    # Convert relative URLs to absolute URLs
                    resource_url_full = urljoin(url, resource_url)
                    # Extract the domain of the current resource
                    extracted = tldextract.extract(resource_url_full)
                    resource_domain = "{}.{}".format(extracted.domain, extracted.suffix)   
                    total_resources += 1
                    if web_domain == resource_domain:
                        linked_ins += 1
        # No resources found
        if total_resources == 0:
            return -1
        linked_out = total_resources - linked_ins
        avg = linked_out / total_resources
        if avg < 0.22:
            return -1
        elif 0.22 <= avg < 0.61:
            return 0
        else:
            return 1
    except Exception as e:
        return 0

#14
def url_anchor(url, driver):
    try:
        # Find all anchor tags with href attribute (i.e., all hyperlinks)
        anchors = driver.find_elements(By.XPATH, "//a[@href]")
        if not anchors:
            return -1
        # Extract the domain from the page URL
        extracted = tldextract.extract(url)
        web_domain = "{}.{}".format(extracted.domain, extracted.suffix)
        # Count the total number of hyperlinks
        no_anchor = len(anchors)
        linked_ins = 0
        # Process each hyperlink
        for anch in anchors:
            href = anch.get_attribute('href')
            if href.startswith('#') or href.startswith('javascript:void(0)'):
                linked_ins += 1
            # Convert relative URLs to absolute URLs
            href_full = urljoin(url, href)
            # Extract the domain of the current hyperlink
            extracted = tldextract.extract(href_full)
            anchor_domain = "{}.{}".format(extracted.domain, extracted.suffix)
            if web_domain == anchor_domain:
                linked_ins += 1
        linked_out = no_anchor - linked_ins
        avg = linked_out / no_anchor
        if avg < 0.31:
            return -1
        elif 0.31 <= avg < 0.67:
            return 0
        else:
            return 1
    except Exception as e:
        return 0

#15
def has_links_in_tags(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        # Extract the domain from the page URL
        extracted = tldextract.extract(url)
        web_domain = "{}.{}".format(extracted.domain, extracted.suffix)
        # Find all Meta, Script, and Link tags
        tags = soup.find_all(['meta', 'script', 'link'])
        # Count the number of tags linked to the same domain
        same_domain_count = 0
        for tag in tags:
            href = tag.get('href') or tag.get('src') or tag.get('content')
            if href:
                # Convert relative URLs to absolute URLs
                href_full = urljoin(url, href)
                # Extract the domain of the current hyperlink
                extracted = tldextract.extract(href_full)
                tag_domain = "{}.{}".format(extracted.domain, extracted.suffix)
                if tag_domain == '' or tag_domain == web_domain:
                    same_domain_count += 1
        other_domain = len(tags) - same_domain_count
        if len(tags) > 0:
            avg = other_domain / len(tags)
        else:
            return -1
        if avg < 0.31:
            return -1
        elif 0.31 <= avg <= 0.67:
            return 0
        else:
            return 1
    except Exception as e:
        return 0

#16
def sfh(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        # Extract the domain of the main webpage
        extracted = tldextract.extract(url)
        web_domain = "{}.{}".format(extracted.domain, extracted.suffix)
        # Find all form tags
        form_tags = soup.find_all('form')
        for form in form_tags:
            # Retrieve the value of action
            action = form.get('action', '').strip()
            # Check if SFH is empty or about:blank
            if not action or action == 'about:blank':
                return 1
            # If SFH contains a domain, check if it's different from the webpage's domain
            if action.startswith('http'):
                # Extract the domain of the current action
                extracted = tldextract.extract(action)
                action_domain = "{}.{}".format(extracted.domain, extracted.suffix)
                if action_domain != web_domain:
                    return 0
        return -1
    except Exception as e:
        return 0

#17
def email(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        # Search for href attributes containing 'mailto:'
        mailto_links = soup.find_all(href=lambda href: href and 'mailto:' in href)
        if 'mail(' in sourcecode:
            return 1
        if mailto_links:
            return 1
        else:
            return -1
    except Exception as e:
        return 0

#18
def has_abnormal_url(url):
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        # Check if domain is in the WHOIS database
        if domain_info.domain_name:
            if domain.lower() in url.lower():
                return -1
            else:
                return 1
        else:
            return 1
    except Exception as e:
        return 0

#19
def forwarding(url):
    try:
        # Sends a GET request to the URL and follows any redirects
        response = requests.get(url, allow_redirects=True)
        number_of_redirects = len(response.history)
        if number_of_redirects <= 1:
            return -1
        elif 1 < number_of_redirects < 4:
            return 0
        else:
            return 1
    except Exception as e:
        return 0

#20
def mouseover(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        onmouseover_elements = soup.find_all(onmouseover=True)
        # Check if any onmouseover attribute contains code that changes the status bar
        for element in onmouseover_elements:
            if 'window.status' in element.get('onmouseover') or "window.statusText" in element.get('onmouseover'):
                return 1
        return -1
    except Exception as e:
        return 0

#21
def has_disabled_right_click(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        script_tags = soup.find_all('script')
        # Check if any script tag contains code that disables right click
        for script in script_tags:
            if script.text and ('event.button == 2' in script.text or 'oncontextmenu' in script.text):
                return 1
        return -1
    except Exception as e:
        return 0

#22
def popup(url, driver):
    try:
        popups = driver.find_elements(By.XPATH, "//*[contains(@class, 'popup') or @role='dialog' or contains(@class, 'modal')]")
        # Check for text fields within popups
        for popup in popups:
            if popup.find_elements(By.XPATH, ".//input[@type='text']"):
                return 1
        return -1
    except Exception as e:
        return 0

#23
def has_iframe(url, driver):
    try:
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        iframes = soup.find_all('iframe')
        if iframes:
            return 1
        else:
            return -1
    except Exception as e:
        return 0

#24
def age_of_domain(url):
    try:
        domain_info = whois.whois(url)
        creation_date = domain_info.creation_date
        # Ensure that the creation date is in a consistent format
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        six_months = datetime.now() - timedelta(days=180)
        if creation_date and creation_date < six_months:
            return -1 
        else:
            return 1 
    except Exception as e:
        return 0

#25
def has_DNS_record(url):
    try:
        domain_info = whois.whois(url)
        # Check if 'name_servers' section exists
        if hasattr(domain_info, 'name_servers'):
            dns_records = domain_info.name_servers  
        else:
            return 1
        if dns_records:
            return -1
        else:
            return 1
    except Exception as e:
        return 0

#26
def google_index(url):
    try:
        # Get the key and custom search engine id stored in environment variables
        api_key = os.environ.get('google_api_key')
        cse_id = os.environ.get('google_api_cse')
        if not api_key:
            raise Exception("API key not found")
        if not cse_id:
            raise Exception("CSE id not found")    
        # Make the request
        response = requests.get(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q=site:{url}")
        # Raises an HTTPError if the HTTP request was unsuccessful
        response.raise_for_status()
        # Check for successful response
        search_results = json.loads(response.text)
        # Check if there are any search results
        if 'items' in search_results and len(search_results['items']) > 0:
            return -1
        else:
            return 1
    except Exception as e:
        return 0

def get_driver(url):
    driver = None
    try:
        # Configure Selenium WebDriver
        options = Options()
        # Run in headless mode
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        # Determine the current working directory and set path for the Chrome driver
        current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_path = os.path.join(current_directory, 'chromedriver')
        service = Service(executable_path=driver_path)
        # Initialize the Chrome WebDriver with the specified options
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Set a 10 seconds timeout and wait for page to load completely
        timeout = 10
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        return driver
    except Exception as e:
        return e

def attributes(url):
    url = url.replace(' ', '').replace('\t', '')
    # Get the Chrome WebDriver
    driver = get_driver(url)
    attributes = [url_has_ip(url), has_long_url(url), has_shortening_service(url), has_at_symbol(url), has_double_slash(url), has_dash(url), has_subdomain(url), has_https(url), domain_length(url), has_favicon(url, driver), check_port(url), has_token(url), has_request_url(url, driver), url_anchor(url, driver), has_links_in_tags(url, driver), sfh(url, driver), email(url, driver), has_abnormal_url(url), forwarding(url), mouseover(url, driver), has_disabled_right_click(url, driver), popup(url, driver), has_iframe(url, driver), age_of_domain(url), has_DNS_record(url), google_index(url)]
    if driver is not None:
        driver.quit()
    return attributes
    
def make_prediction(forest, test_data):
    return bagging_predict(forest, test_data)

def random_forest(url):
    row = attributes(url)
    model_path = os.path.join(os.path.dirname(__file__), '..', 'RandomForest', 'random_forest_model.pkl')
    # Load the model
    with open(model_path, 'rb') as file:
        forest = pickle.load(file)
    prediction = make_prediction(forest, row)
    return prediction
