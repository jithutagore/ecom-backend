from bs4 import BeautifulSoup
import urllib.parse
import requests
import re
import pymysql

def google_search(query):
    try:
        formatted_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={formatted_query}&tbm=shop"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for 4XX or 5XX status codes
        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

def html_parser(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    sh_dgr_contents = soup.find_all(class_="sh-dgr__content")
    
    for sh_dgr_content in sh_dgr_contents:
        product_title = sh_dgr_content.find(class_="tAxDx").get_text()
        original_price = sh_dgr_content.find(class_="a8Pemb OFFNJ").get_text()
        
        additional_info_element = sh_dgr_content.find(class_="vEjMR")
        additional_info = additional_info_element.get_text() if additional_info_element else None
        
        url_anchor = sh_dgr_content.find('a', class_='xCpuod')
        product_url = "https://www.google.com" + url_anchor['href'] if url_anchor else None
        
        img_tag = sh_dgr_content.find('img')
        img_id = img_tag.get('id') if img_tag else None
        if img_id:
            script_tag = soup.find('script', string=re.compile(f"var _i\s*=\s*'({img_id})'"))
            if script_tag:
                u_pattern = r"var _u\s*=\s*'([^']*)';"
                match = re.search(u_pattern, script_tag.string)
                if match:
                    img_url = urllib.parse.unquote(match.group(1).replace("\\x3d", "=").replace("\\x26", "&"))
                else:
                    img_url = None
            else:
                img_url = None
        else:
            img_url = None
        
        result = {
            "product_title": product_title,
            "original_price": original_price,
            "additional_info": additional_info,
            "product_url": product_url,
            "img_url": img_url
        }
        results.append(result)
    
    return results




def google_search_morzilla(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def comparer(html_content):
    data = []
    soup = BeautifulSoup(html_content, "html.parser")
    buying_options_div = soup.find("div", class_="sh-pov__grid")
    img_url=""
    for img_tag in soup.find_all("img"):
        src = img_tag.get('src')
        if src and src.startswith("https://encrypted"):
            img_url=src
            break 
    description = [li.span.text.strip() for li in soup.find_all('li', class_='KgL16d')]
    if len(description)==0:
        description = [soup.find('span', class_='sh-ds__trunc-txt').text.strip()]
    title = soup.find('span', class_='BvQan').text.strip()

    if buying_options_div:
        for row in buying_options_div.find_all("tr", class_="sh-osd__offer-row"):
            seller_name = row.find("td", class_="SH30Lb").text.strip().replace('Opens in a new window', '') 
            item_price = row.find("span", class_="g9WBQb").text.strip().replace('\u20b9', '')  # Remove currency symbol
            for anchor_tag in row.find_all("a", href=True):
                href = anchor_tag["href"]
                href1 = urllib.parse.unquote(href.replace("/url?q=", "").replace("\\x3d", "=").replace("\\x26", "&"))
                data.append({
                    "Seller": seller_name,
                    "Item Price": item_price,
                    "Href": href1
                })
    else:
        print("Buying options div not found in the HTML content.")
    return {
        "img_url": img_url,
        "description": description,
        "title": title,
        "price_comparison": data
    }