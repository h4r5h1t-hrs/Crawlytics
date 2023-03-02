<h1 align="center"><a href="https://github.com/h4r5h1t-hrs/CertCheck.git">Crawlytics</a></h1>
<h4 align="center">A Python-based web crawling tool for data extraction and security analysis that supports various arguments for efficient crawling and outputs results in JSON format.</h4>

<p align="center">
<a href="https://twitter.com/h4r5h1t_hrs"><img src="https://img.shields.io/twitter/follow/h4r5h1t_hrs?style=social"></a>
<a href="https://github.com/h4r5h1t-hrs?tab=followers"><img src="https://img.shields.io/github/followers/h4r5h1t-hrs?style=social"></a>
<a href="https://github.com/h4r5h1t-hrs/webcopilot/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://github.com/h4r5h1t-hrs/webcopilot/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
<a href="#"><img src="https://img.shields.io/badge/Made%20with-python-1f425f.svg"></a>
<a href="#"><img src="https://madewithlove.org.in/badge.svg"></a>
</p>

<p align="center">
  <a href="#Requirements">Requirements</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a>
</p>

This is a python-based web crawling tool that allows users to crawl a website for the purpose of data extraction, security analysis or any other purpose.

# Requirements
- Python 3
- mechanicalsoup
- requests
- time
- threading
- math
- tldextract
- argparse
- typing
- rich

# Installation
1. Clone the repository from Github:
```bash
git clone https://github.com/h4r5h1t-hrs/Crawlytics
```
2. Navigate to the downloaded repository and install the required libraries:
```bash
cd Crawlytics
pip install -r requirements.txt
```
# Usage
To run the program, use the following command:
```bash
crawlytics.py --help
```
This will display the following output:
```bash
usage: crawlytics [-h] -u URL [-l URL_LIMIT]

Crawlytics is a python script which crawls the website and fetches all the URLs present on the website.

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Provide the URL to check
  -l URL_LIMIT, --url_limit URL_LIMIT
                        Provide URL limit to crawl (default: 1000)

Example: python3 crawlytics.py -u https://www.breachlock.com [-l 1000]
```
# Examples
Crawl a website, use the '-u' flag and provide the URL as an argument:
```bash
python crawlytics.py -u https://example.com
```

Crawl a website and limit the number of URLs to be fetched:
```bash
python crawlytics.py https://www.example.com -u 500
```
<table>
<td>
<b>Warning:</b> Developers assume no liability and are not responsible for any misuse or damage cause by this tool. So, please se with caution because you are responsible for your own actions.
</td>
</table>