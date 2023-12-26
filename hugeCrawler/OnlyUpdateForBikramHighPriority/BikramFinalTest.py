import os
import re
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
cookies=None
with open("state.json","r") as file:
    cookies={x['name']:x['value'] for x in json.loads(file.read())["cookies"]}

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Range': 'bytes=0-',
    'Referer': 'https://www.theyarehuge.com/',
    'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="119", "Google Chrome";v="119"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'video',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')  # Necessary for running in headless mode on Linux

# Retry mechanism for HTTP requests
def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Function to get MP4 link using Selenium with cookies
def get_mp4_link_with_selenium_and_cookies(url):
    user_agent = UserAgent().random
    headers = {'User-Agent': user_agent}

    for attempt in range(3):  # Retry up to 3 times
        try:
            # Set up WebDriver for Linux
            driver_path = '/usr/bin/chromedriver'  # Set the path to your chromedriver executable for Linux

            # Create a service object
            service = Service(driver_path)

            # Use the service object to create the WebDriver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            
            # Wait for the page to load (adjust the sleep duration if needed)
            time.sleep(10)

            # Extract the MP4 link
            video_element = driver.find_element("css selector", "video")
            mp4_link = video_element.get_attribute('src')

            # Remove the dynamic section after .mp4
            mp4_link = re.sub(r'\?.*', '', mp4_link)

            # Get cookies
            cookies = driver.get_cookies()

            # Close the WebDriver
            driver.quit()

            return mp4_link, cookies
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}: Error retrieving MP4 link for {url}: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying

    logger.error(f"All attempts failed. Skipping URL: {url}")
    return None, None

# Function to download a file with Free Download Manager
def download_with_fdm(url):
    try:
        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".strip("/")
        # Replace 'path_to_fdm' with the actual path to your Free Download Manager executable on Linux
        fdm_path = '/opt/freedownloadmanager/fdm'  # Set the path to your Free Download Manager executable on Linux

        # Format the command to add a new download in FDM
        command = f'"{fdm_path}" {url}'
        
        # Execute the command
        os.system(command)
        logger.info(f"Sent MP4 link to Free Download Manager: {url}")
    except Exception as e:
        logger.error(f"Error sending MP4 link to Free Download Manager: {e}")

def wait_based_on_content_size(content_length):
    if content_length < 100 * 1024 * 1024:  # Size less than 100MB (converted to bytes)
        time.sleep(30)
    elif 100 * 1024 * 1024 < content_length < 400 * 1024 * 1024:  # Size between 100MB and 400MB
        time.sleep(60)
    else:  # Size greater than 400MB
        time.sleep(120)
        
# Function to crawl a URL, extract MP4 link, and download with Free Download Manager
def crawl_and_download_with_fdm(url):
    mp4_link, _ = get_mp4_link_with_selenium_and_cookies(url)
    ContentLength=10 * 1024 * 1024
    try:
        response = requests.get(url,headers=headers,cookies=cookies,stream=True)
        ContentType = response.headers.get("Content-Type")
        if ContentType == "video/mp4":
            ContentLength = int(response.headers.get("Content-Length"))
    except Exception as e:
        print(f"[+] Error : {e}")
        
    if mp4_link:
        # Use Free Download Manager to download the file
        download_with_fdm(mp4_link)
        wait_based_on_content_size(ContentLength)


# Function to get the server-prescribed file name or immediate parent folder name
def get_server_prescribed_filename(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    filename = path_parts[-1] if path_parts[-1] else path_parts[-2]
    return filename

# Read URLs from list.txt
with open('list.txt', 'r') as file:
    urls = [line.strip() for line in file.readlines()]

# Crawl and download with Free Download Manager for each URL
for url in urls:
    crawl_and_download_with_fdm(url)
