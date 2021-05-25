# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://towardsdatascience.com/a-tutorial-on-scraping-images-from-the-web-using-beautifulsoup-206a7633e948
# https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests, shutil, os, csv, re

import json # used for creating json database
import hashlib # used for creating unique ID from url adress by hashing

# Function to find out, how many pages are for given birck
# @var string/integer: brick number (e.g 3068)
# @return integer: number of pages
def get_pages(brick):
    req = Request('https://www.brickowl.com/search/catalog?query=' + str(brick), headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')

    # Get all items in the page
    div = soup.find('div', class_="pagination")
    li = div.findAll('li')

    last = li[len(li)-2]

    m = int(last.text)
    return(m)


# Create paths
# if not os.path.isdir('Folder1'):
#    os.makedirs('Folder1')

# Get current directory
# directory = os.getcwd()
# Define log entry
# def write_log_entry(name, location, source):
#     log=[]
#     log.append(name)
#     log.append(directory + location)
#     log.append(source)
#     log.append(timestamp())
#     csv_file=directory+'/log.csv'
#     fh=open(csv_file,'a',newline='')
#     writer=csv.writer(fh)
#     writer.writerow(log)
#     fh.close()

# Define timestamp
def timestamp():
    from datetime import datetime
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

# Get url
def get_html(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    return soup

# This function is for testing purposes only - it scrapes from locally stored html page
# @var string - filename
# @return BeatifulSoup object 
def get_test(file):
    with open(file) as f:
      soup = BeautifulSoup(f, features="lxml")
    return soup

# Get HTML for testing
#soup = get_html('https://www.brickowl.com/catalog/lego-tile-2-x-2-with-coastal-map-decoration-with-groove-3068-34888')
#html = str(soup)

# write test to file
#f = open("test.html", "w")
#f.write(html)
#f.close()

# get brick name
def get_name(soup):
    try: 
        name = soup.find('h1', id='page-title').contents[0]
        name = name.strip()
    except:
        name = ''
    return name

# get brick description
def get_description(soup):
    try:
        desc = soup.find('div', id='desc').contents[0]
        desc = desc.strip()
    except:
        desc = ''
    return desc

# get brick image
def get_image(soup, idx, brick):
    try: 
        block = soup.find('p', class_="product-image")
        image = block.find('img')
        src = image.attrs['src']

        # Take the last part of the name
        srclist = src.split(sep="/")
        picname = srclist[len(srclist) - 1]
        extension = picname.split(sep = ".")
        name = 'database/' + str(brick) + '/'+ str(idx) + '.' + extension[len(extension) - 1]
#         print(name)    
        # copy the image
        r = requests.get(src, stream=True)      #Get request on full_url
        if r.status_code == 200:                     #200 status code = OK
            file_name = name
            with open(file_name, 'wb') as f:        
                r.raw.decode_content = True        
                shutil.copyfileobj(r.raw, f)
        return True, name
    except:
        return False, ''

# get brick information from table
def handle_table(soup):
    table = soup.find('table', class_='item-right-table')
    mydict = {}
    
    # How many wishlists
    try:
        find = re.search(r"In (\d+) Wishlist", str(table))
        mydict['wishlists'] = int(find[1])
    except:
        pass
    
    # How many available
    try:
        href = table.find('a')
        span = href.findAll('span')
        for m in span:
            m.unwrap()
        
        mydict['available'] = int(href.contents[0])
    except:
        pass

    # Get the starting price
    try:
        price = table.find('span', class_='price').contents[0]
        find = re.search(r"(\d+.+)", str(price))
        mydict['price'] = float(find[1])
    except:
        pass

    # Get ID's
    try:
        # Find table
        table = soup.find('table', class_='item-right-table')

        # What year span
        try:
            ystart = table.findAll('span', class_='yearseg')        
            mydict['start'] = int(ystart[0].string.strip())
            mydict['end'] = int(ystart[2].string.strip())
        except:
            pass

        tr = table.findAll('tr')
        for rows in tr:
            data = rows.findAll('td')

            # Extract ids
            if len(data) == 2:                
                # clean span
                for d in data:
                    for m in d.findAll('span'):
                        m.unwrap()
                    
                    
                # id-name
                idtype = (str(data[0].string)).strip()
                
                #value
                idstr = str(data[1])
                idstr = re.sub(r"<td>|<\/td>|\s+", "", idstr)
                idvalue = idstr.split(sep=",")
                
                mydict[idtype] = idvalue

        return True, mydict
    except:
        return False, {}

# Get brick price-list
def get_prices(_soup):
    try:
        _table = _soup.find('table', 'ph-table')
        row = _table.find("td", string="Current").parent
        col = row.findAll("td")
        span = col[1].findAll("span")
    except:
        return False, {}

    i = 0
    table_data = {}
    while i < len(span):
        # We need to step further if it is a label or price... 
        try:
            while len(span[i].get('class')) > 0:
                i += 1
        except:
            pass
        try:
            key = span[i].text
            value = span[i+1].text
            value = value.replace('EUR ', '').strip()
            table_data[key.strip()] = value
            i += 2
        except:
            i += 2
            pass
    return True, table_data    

# Scrape lego brick information from given url
# @var string url of the brickowl brick
# @return dictionary brick data
def handle_lego(url, brick):
    # Query the url
    soup = get_html(url)
    
    # create a dictionary
    lego = dict()
#    lego[idx] = dict()
    
    # Collect the basic data
    result, legodict = handle_table(soup)
    
    # It is worthwhile to continue only if collecting was successful
    if result:
        # Collect the image information
        img_result, imagename = get_image(soup, hashlib.sha1(url.encode('utf-8')).hexdigest(), brick)
        if img_result:
            lego['image'] = imagename
        lego['name'] = get_name(soup)
        lego['description'] = get_description(soup)
        lego['url'] = url
        lego['data'] = legodict
        lego['saved'] = timestamp()    
    
    return lego

# Handles the folders
# @var string brick number 
def handle_folders(brick):
    folder = str(brick)
    #################################
    # create folder, if it does not exist
    if not os.path.isdir('database'):
        os.makedirs('database')
        
    if not os.path.isdir('database/' + folder):
        os.makedirs('database/' + folder)
    # read database from json
    database = 'database/' + folder + '/database.json'

    # if json file exists then read database from json
    if os.path.exists(database):
        f = open(database)
        lego = json.load(f)
        f.close()
    else:
        # else create empty dictionary
        lego = dict()
    return lego


# This is the main function
def scrape(brick):
    # Get number of pages
    last = get_pages(brick)
    i = 1
    database = 'database/' + str(brick) + '/database.json'

    lego = handle_folders(brick)

    while i < last:
        iterator(brick, i, lego)
#         mainurl = 'https://www.brickowl.com/search/catalog?query=' + str(brick) + '&page=' + str(i)
# 
#         # Get all items in the page
#         req = Request(mainurl, headers={'User-Agent': 'Mozilla/5.0'})
#         html_page = urlopen(req).read()
#         soup = BeautifulSoup(html_page, 'html.parser')
#         items = soup.findAll('li', class_="category-item")
# 
#         for item in items:
#             a = item.find('a', href=True)
#             src = 'https://www.brickowl.com' + a['href']   
# 
#             #url = 'https://www.brickowl.com/catalog/lego-sally-set-71024-15'
#             #soup = get_html(url)
# 
#     #        idx = str(uuid.uuid4())
# 
#             # Create unique id by hashing the url of the item
#             # idx = hash(src)
#             idx = hashlib.sha1(src.encode('utf-8')).hexdigest()
#             if idx not in lego:
#                 lego[idx] = handle_lego(src)

        i += 1

    # create a json file for database
    lego_json = json.dumps(lego)
    f = open(database, 'w')
    f.write(lego_json)
    f.close()

def iterator(brick, i, lego):
    mainurl = 'https://www.brickowl.com/search/catalog?query=' + str(brick) + '&page=' + str(i)

    # Get all items in the page
    req = Request(mainurl, headers={'User-Agent': 'Mozilla/5.0'})
    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')
    items = soup.findAll('li', class_="category-item")

    for item in items:
        a = item.find('a', href=True)
        src = 'https://www.brickowl.com' + a['href']
#         print(src)

        #url = 'https://www.brickowl.com/catalog/lego-sally-set-71024-15'
        #soup = get_html(url)

#        idx = str(uuid.uuid4())

        # Create unique id by hashing the url of the item
        # idx = hash(src)
        idx = hashlib.sha1(src.encode('utf-8')).hexdigest()
#         print(idx)
#         print(lego)
        if idx not in lego:
            lego[idx] = handle_lego(src, brick)

# print(os.getcwd())

#scrape(3069)