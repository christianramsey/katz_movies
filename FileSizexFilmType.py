
# coding: utf-8

# In[ ]:

from bs4 import BeautifulSoup
import re
from time import sleep
import requests
import re

import numpy as np
import pandas as pd
import xlsxwriter



# In[2]:

# first we will get as many links as we can say 50*25
urllist = ['https://kat.cr/movies/']
for x in range(400):
    name = "https://kat.cr/movies/" + str(x+1) + "/"
    urllist.append(name)


# In[3]:

# #mainSearchTable
# table
# tbody
# tr (not tr.firstr) -> (if even or odd YES, if neither not)


# In[4]:


def convert_to_mb(size, measure):
    """
    standardising size, I know this isn't super accurate, perhaps 1024 is better. 
    takes size and measure where size is int and measure tells us the unit type.
    """
    c_size = 0
    if measure == 'KB':
        c_size = .99
    elif measure == 'MB':
        c_size = size
    elif measure == 'GB':
        c_size = (size*1000)
    return c_size

def get_features(torrent):
    """
        torrent = soup
        get features uses beautifulsoup to find each relevant feature 
        within the html document.
    """
    
    
    # # here are the "selectors" for each feature/attribute 
    # name : $('a.cellMainLink')
    # size : $('td.nobr.center')
    # comments: .icommentjs
    # torrent_movies_torrents12504043
    # $('#torrent_movies_torrents12504043 td.center')
    # 1. size
    # 2.files
    # 3. age
    # 4. seed
    # 5. leech
    #name
    name_link= torrent.find("a", {"class":"cellMainLink"})
    name = name_link.contents[0]

    #size
    size_td= torrent.find("td", {"class":"nobr center"})
    size =  float(size_td.contents[0])
    measure = size_td.contents[1].contents[0]

    #comments to make it more robust one should 
#         add try/except statements around each selector to make sure it
#         finds it. For my needs I only found that comments would need to be verified. 
#         But... just like the tags themselves, they could change or go missing with a simple 
#         template update or an incomplete torrent upload. 
        
    mkblka = torrent.find("a", {"class":"icommentjs"})
    if (mkblka is None):
        comments = 0
    else:
        comments = mkblka.contents[0]
    
    #I want to use the numerical part of the elements id as an index (assuming it really is an index of some sort)
    css_id = str(torrent['id'])
    m = re.search('(\d+)', css_id)
    cid = int(m.group(0))

    meta = torrent.find_all("td", {"class":"center"})
    files = meta[1].contents[0]
    age = meta[2]['title'] #timestamp
    seeders = meta[3].contents[0]
    leechers = meta[4].contents[0]
    features = {cid: {'seeders': seeders, 'leechers': leechers, 'files': files, 'age': age, 'comments': int(comments), 'size': convert_to_mb(size, measure),  'name': name}}
    return features


# In[5]:

# Setting up a blank dataframe, since I couldn't figure out how to assign it, 
# could have set it up using idx is 0 to set the first and then concat the rest
blank = {0: {'seeders': 0, 'leechers': 0, 'files': 0, 'age': "age", 'comments': 0, 'size':0,  'name': "name"}}
torrent_df = pd.DataFrame.from_dict(blank, orient="index")


for idx, url in enumerate(urllist):
    r = requests.get(url) 
    if r.status_code == 200:
            bsObj = BeautifulSoup(r.text, "lxml")             
            trs = bsObj.findAll("tr", {"id" : re.compile('torrent_movies_torrents.*')})
            for torrent in trs:
                features = get_features(torrent)
                print(features)
                adpdp = pd.DataFrame.from_dict(features, orient="index")
                torrent_df = pd.concat([torrent_df, adpdp] )
            
            # waiting 5 seconds between url calls
            sleep(5)               


# In[7]:

writer = pd.ExcelWriter('/Users/christianramsey/PycharmProjects/Katz/FileSizexFilmType.xlsx', engine='xlsxwriter')
torrent_df.to_excel(writer, sheet_name='Sheet1')
torrent_df


# In[ ]:



