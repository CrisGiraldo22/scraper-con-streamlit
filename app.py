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

def save_image(image_url, product_name):
    folder = "images"
    os.makedirs(folder, exist_ok=True)

    valid_filename = re.sub(r'[<>:"/\\|?*]','',product_name)
    valid_filename = valid_filename[:10]
    filepath =os.path.join(folder, valid_filename + '.jpg')

    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1

    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chuck in response.iter_content(1024):
                file.write(chuck)
        return filepath
    return None

def save_to_excel(data):
    df = pd.DataFrame(data)
    file_name = 'searches.xlsx'

    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(file_name, index=False)
    return  file_name

