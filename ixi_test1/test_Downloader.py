import requests
import json


# url = input("Enter url to download from ixiporn.cc : ")
url="https://cdn2.ixifile.xyz/1/Aunty%20ki%20Ghanti%20Ep%201.mp4"
output_file = "t2.mp4"

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Range': 'bytes=0-',
    'Referer': 'https://ixiporn.org/',
    'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="119", "Google Chrome";v="119"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'video',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
# {'Server': 'nginx', 'Date': 'Thu, 30 Nov 2023 03:34:53 GMT', 'Content-Type': 'video/mp4', 'Content-Length': '280947743', 'Last-Modified': 'Tue, 28 Nov 2023 15:45:58 GMT', 'Connection': 'keep-alive', 'ETag': '"65660b36-10beec1f"', 'X-Content-Type-Options': 'nosniff', 'X-XSS-Protection': '1; mode=block', 'X-Robots-Tag': 'none', 'Content-Security-Policy': "frame-ancestors 'self' cdn2.ixifile.xyz", 'Content-Range': 'bytes 0-280947742/280947743'}

response = requests.get(url,headers=headers,stream=True)
header = dict(response.headers)
print(header)
contentlength=response.headers.get('Content-Length')
if contentlength:
    total_size = int(contentlength)
    downloaded = 0
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                downloaded+=len(chunk)
                print(f"{downloaded}/{total_size}",end="\r",flush=True)
                f.write(chunk)