import os
import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit import header, title
from streamlit.testing.v1.element_tree import Title


def get_product_info(url):
    headers = {
        'Host': 'www.amazon.com',
        'User-Agent': '...',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com'
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

def get_search_results(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'en-Us, en;q=0.9',
        }
    url = f"https://www.amazon.com/s?k={query}"
    response =requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    product_links = []
    for link in soup.find_all('a',{'class':'a-link-normal s-line-clamp-2'}, href=True):
        product_links.append('https://www.amazon.com' + link['href'])

    return product_links

#Streamlit App
st.title("Amazon scraper product")

search_query = st.text_input("Enter your search on Amazon:")

if search_query:
    st.write(f"Results for: {search_query}")
    product_urls = get_search_results(search_query)

    if product_urls:
        all_data = []
        for url in product_urls[:10]:
            title, image_url, price = get_product_info(url)

            if title != 'The title was not found':
                data = {
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Title': title,
                    'Price': price,
                    'Image url': image_url,
                    'Product url':url
                }
                all_data.append(data)

                if image_url:
                    save_image(image_url, title)
        if all_data:
            df = pd.DataFrame(all_data)
            st.write("### Product information")
            st.dataframe(df.style.set_properties(**{'text-align':'left'}).set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'left')]}]
            ))

            file_name = save_to_excel(all_data)
            st.success(f"Data saved in {file_name}")
        else:
            st.error("No valid products found.")
    else:
        st.error("No results were found for your search.")


