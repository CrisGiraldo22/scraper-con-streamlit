import os
import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit import header


def get_product_info(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'en-Us, en;q=0.9',
    }

    response = requests.get(url, headers=headers)
    soup =BeautifulSoup(response.text,'lxml')

    try:
        title = soup.find(id='productTitle').get_text(strip=True)
    except AttributeError:
        title = 'No title found'

    try:
        image_url = soup.find(id='landingImage')['src']
    except (AttributeError, TypeError):
        image_url = None

    try:
        price = soup.find('span',{'class':'a-offscreen'}) .get_text(strip=True)
    except (AttributeError, TypeError):
        price = 'No price found'

    return title, image_url, price 


