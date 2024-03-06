import vt
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

def download_file(url):
    try:
        # Set the download directory to a 'Downloads' folder in the current script's directory
        current_directory = os.path.dirname(os.path.abspath(__file__))
        download_path = os.path.join(current_directory, 'Downloads')
        # Create the Downloads directory if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        # Set Chrome options for headless mode and download directory
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('prefs', {'download.default_directory': download_path})
        # Initialize a Selenium WebDriver using webdriver-manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # Navigate to the URL
        driver.get(url)
        # Wait for the download to complete
        time.sleep(8)
        # Check the download directory for files
        downloaded_files = os.listdir(download_path)
        if len(downloaded_files) > 1:
            # Return the path of the downloaded file
            if downloaded_files[1] == '.ipynb_checkpoints':
                return download_path + '/' + downloaded_files[0]
            else:
                return download_path + '/' + downloaded_files[1]
        else:
            # No files were downloaded
            return 'L'
    except Exception as e:
        return e
    finally:
        # Close the browser
        driver.quit()

def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        return e

def analyse_file(api_key, file_path):
    try:
        with vt.Client(api_key) as client:
            # Open the file and send it for analysis
            with open(file_path, "rb") as file:
                analysis = client.scan_file(file)
            # Poll until the analysis is completed
            while True:
                analysis = client.get_object(f"/analyses/{analysis.id}")
                if analysis.status == 'completed':
                    break
                # Wait for a seconds before polling again
                time.sleep(1)
            # Check if the analysis object has the attribute 'stats'
            if hasattr(analysis, 'stats'):
                stats = analysis.stats
                malicious_detections = stats.get('malicious', 0)
                if malicious_detections >= 4:
                    return 'P'
                else:
                    return 'L'
            else:
                return 'L'
    except Exception as e:
        return e

def virustotal(url):
    # Create a new event loop
    loop = asyncio.new_event_loop()
    # Set the newly created loop as the current event loop, ensuring the asynchronous code has a compatible event loop and will behave as expected
    asyncio.set_event_loop(loop)
    downloaded_file = download_file(url)
    if downloaded_file == 'L':
        return 'L'
    else:
        # Get the key stored in an environment variable
        api_key = os.environ.get('virustotal_key')
        if not api_key:
            raise Exception("API key not found")
        result = analyse_file(api_key, downloaded_file)
        delete_file(downloaded_file)
        if result == 'P':
            return 'P'
        elif result == 'L':
            return 'D'
    # Close the loop at the end of the function
    loop.close()
