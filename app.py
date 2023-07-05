import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import requests
import streamlit as st
import time
import re
import base64

from py1337x import py1337x
# import pyratebay
torrents = py1337x(proxy='1337x.to', cache='py1337xCache', cacheTime=500)
# import libtorrent as lt
from requests.adapters import HTTPAdapter, Retry
# from bs4 import BeautifulSoup

############TPB########################

categories = {
	'audio': {
		'code':100,
		'subs':{
			'music':1,
			'audio books':2,
			'sound clips':3,
			'flac':4,
			'other':99
		}
	},
	'video': {
		'code':200,
		'subs':{
			'movies':1,
			'movies DVDR':2,
			'music videos':3,
			'movies clips':4,
			'tv shows':5,
			'handheld':6,
			'hd movies':7,
			'hd tv shows':8,
			'3d':9,
			'other':99
		}
	},
	'applications':{
		'code':300,
		'subs':{
			'windows':1,
			'mac':2,
			'unix':3,
			'handheld':4,
			'ios':5,
			'android':6,
			'other os':99
		}
	},
	'games':{
		'code':400,
		'subs':{
			'pc':1,
			'mac':2,
			'psx':3,
			'xbox360':4,
			'wii':5,
			'handheld':6,
			'ios':7,
			'android':8,
			'other':99
		}
	},
	'porn':{
		'code':500,
		'subs':{
			'movies':1,
			'movies dvdr':2,
			'pictures':3,
			'games':4,
			'hd movies':5,
			'movie clips':6,
			'other':99
		}
	},
	'other':{
		'code':600,
		'subs':{
			'ebooks':1,
			'comics':2,
			'pictures':3,
			'covers':4,
			'physibles':5,
			'other':99
		}
	}
}


URL = "https://apibay.org/"

class Torrent:

	def __init__(self, id, name, info_hash, le, se, num_files, size, username, added, status, category):
		self.id = id
		self.url = 'https://thepiratebay.org/description.php?id='+id
		self.name = name
		self.info_hash = info_hash
		self.leechers = int(le)
		self.seeders = int(se)
		self.num_files = num_files
		self.size = size
		self.username = username
		self.added = added
		self.status = status
		self.category = category
		self.description = None

	def get_description(self):
		if self.description == None:
			r = requests.get(URL+'t.php', params={'id':self.id})
			try:
				tor = r.json()
				self.description = tor['descr']
			except Exception as e:
				st.write('Error: ', e)

	def magnet(self):
		return f'magnet:?xt=urn:btih:{self.info_hash}&dn={self.name}'

	def __str__(self):
		return f'Name: {self.name}\nHash: {self.info_hash}\nURL: {self.url}'







class tpb:
	def search(keyword, cats=[]):
		params = {
			'q':keyword,
			'cat':[]
		}
		for cat in cats:
			if cat in categories:
				params['cat'].append(str(categories[cat]['code']))
		params['cat'] = ','.join(params['cat'])

		r = requests.get(URL+'q.php', params=params)

		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(tor['id'], tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None

		return torrents

	def get_torrent(torrent_id):
		r = requests.get(URL+'t.php', params={'id':torrent_id})

		try:
			tor = r.json()
		except Exception as e:
			st.write('Error: ', e)
			return None

		torrent = Torrent(str(tor['id']), tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
				tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
		torrent.description = tor['descr']
		return torrent

	def recent():
		r = requests.get(URL+'precompiled/data_top100_recent.json')
		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(tor['id'], tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None

		return torrents

	def top100(category=None, subc=None):
		if category is None:
			r = requests.get('https://apibay.org/precompiled/data_top100_all.json')
		else:
			if category not in categories:
				raise Exception(f"{category} is not a valid category!")
			cat_n = categories[category]['code']
			if subc is not None and subc not in categories[category]['subs']:
				raise Exception(f"{subc} is not a valid sub-category!")
			elif subc is not None:
				cat_n += categories[category]['subs'][subc]
			r = requests.get(URL+f'precompiled/data_top100_{cat_n}.json')
		torrents = []
		try:
			for tor in r.json():
				torrent = Torrent(str(tor['id']), tor['name'], tor['info_hash'], tor['leechers'], tor['seeders'],
						tor['num_files'], tor['size'], tor['username'], tor['added'], tor['status'], tor['category'])
				torrents.append(torrent)
		except Exception as e:
			st.write('Error: ', e)
			return None
		return torrents







#------------GET DOWNLOAD LINKS-------------
s = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))



api='257Z637RY5VU2XLAEWM2ICYXQHS6YG4C3I7PIGW6W6C7TMXSBBMQ'



df_torrents = pd.DataFrame({})
df_cached = pd.DataFrame({})
df_cloud = pd.DataFrame({})
df_files = pd.DataFrame({})
download_links = []
links = []
query = ''



def file_list(dic):
    if isinstance(dic, dict):
        files_in_source = (
            pd.DataFrame([item for sublist in [list(d.items()) for d in dic['rd']] for item in sublist], columns=['sno', 'dic'])
            .drop_duplicates(subset='sno', keep='first')
            .reset_index(drop=True)

        )
        df = pd.concat([files_in_source.apply(lambda row: row.dic['filename'], axis = 1)
                        ,files_in_source.apply(lambda row: row.dic['filesize'], axis = 1)], axis=1)
        return df.to_numpy()
    else:
        return []
    


def size(n):
    n=n/1000000000
    gb= "{:.2f}".format(n)
    mb= "{:.2f}".format(n*1000)
    if(n>=1):
        return f"{gb}GB"
    else:
        return f"{mb}MB"
    

#https://technoxyz.com/tamilrockers-proxy/
#https://www.1tamilmv.cafe/
def search_1337x(query, type_ ='All'):
    global df_torrents
    # get torrent list by search
    try:
        if(type_=='All'):
            results_dic = torrents.search(query)
        else:
            results_dic = torrents.search(query, category=type_)

        df = pd.DataFrame(results_dic['items'])
    except:
        st.write('site not accessible')
        return None


    # add info hash columns
    try:
        df['infoHash'] = 'NA'
        df['magnet'] = 'NA'
        for row in df.itertuples():
            try:
                torrent_info = torrents.info(link=row.link)
                df['infoHash'].iloc[row.Index] = torrent_info['infoHash']
                df['magnet'].iloc[row.Index] = torrent_info['magnetLink']
            except:
                pass
        df = df[df['infoHash'] != 'NA']

    except:
        st.write('info hash not added')
        return df[['name', 'seeders', 'leechers', 'size', 'time', 'uploader']]
    df_torrents = df[['name', 'seeders', 'leechers', 'size', 'time', 'uploader', 'infoHash', 'magnet']]

    return df_torrents[['name', 'seeders', 'leechers', 'size', 'time', 'uploader']]




def search_tpb(query):
    global df_torrents
    torrents = tpb.search(query)
    list_search_results=[]
    for torrent in torrents:
        list_search_results.append({'name':torrent.name, 'seeders': torrent.seeders, 'leechers': torrent.leechers, 'size':torrent.size, 'time': torrent.added, 'num_files': torrent.num_files, 'infoHash': torrent.info_hash, 'magnet': torrent.magnet()})

    df_torrents = pd.DataFrame(list_search_results)
    df_torrents['time'] = pd.to_numeric(df_torrents['time'], errors='coerce')
    df_torrents['time'] = pd.to_datetime(df_torrents['time'],unit='s')
    df_torrents['size']=df_torrents['size'].astype('int64').apply(size)

    return df_torrents[['name', 'seeders', 'leechers','size', 'time', 'num_files']]






def search_anime_tosho(title):
    global df_torrents
    title = title.replace(" ","+")
    url = f"https://animetosho.org/search?q={title}"
    page = s.get(url)

    #filter sources
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content")
    results_links = results.find_all("div", class_="home_list_entry")

    # make datafrmae of sources
    l=[]
    for results_link in results_links:
        title = results_link.find("div", class_="link").text
        magnet_url = results_link.find("a", href=True, string='Magnet')['href']
        info_hash = str(lt.parse_magnet_uri(magnet_url).info_hash)
        size = results_link.find("div", class_="size").text
        date = results_link.find("div", class_="date")['title'][20:]
        try:
            num_files = results_link.find("em").text.split(' ')[0][1:]
        except:
            num_files = '1'
        l.append((title, size, date, num_files, magnet_url, info_hash))

    df=pd.DataFrame(l)
    df.columns = ['name', 'size', 'time', 'number_of_files', 'magnet', 'infoHash']

    #refine source df
    df=(
        df
        .drop_duplicates(subset='infoHash', keep="first")
        .reset_index(drop=True)
    )
    df_torrents = df
    return df




def filter_cached():
    global df_cached
    df = df_torrents.copy()
    #check cached
    hash_list = '/'.join(df.loc[:,'infoHash'].to_list())
    url = f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_list}"
    response = requests.get(
        url
        ,headers={"Authorization": f"Bearer {api}"}
    )
    df['cache_info'] = df.apply(lambda row: file_list(response.json()[row.infoHash.lower()]), axis = 1)
    df['number_of_files'] = df.apply(lambda row: len(row.cache_info), axis = 1)
    df=df[df['number_of_files']>0].reset_index(drop=True)
    df_cached=df
    st.session_state['df_cached'] = df


    return df_cached[['name', 'size', 'time', 'number_of_files']]



def get_debrid_link(i):
    global df_cloud, df_files, links
    # check link in cloud
    try:
        st.write('Cloud scanning')
        response = requests.get(
            'https://api.real-debrid.com/rest/1.0/torrents'
            ,headers={"Authorization": f"Bearer {api}"}
        )
        df_cloud = pd.DataFrame(response.json())
        info_hash = df_cached.loc[i, 'infoHash'].lower()
        matching_indexes = df_cloud.index[df_cloud['hash'] == info_hash].to_list()
        if len(matching_indexes):
            
            id_ = df_cloud.loc[matching_indexes[0], 'id']
            url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{id_}"
            response = requests.get(
                url
                ,headers={"Authorization": f"Bearer {api}"}
            )
            links = response.json()['links']
            df_files = pd.DataFrame(response.json()['files']).drop(['id', 'selected'], axis =1).rename({'path':'filename'}, axis=1)
            df_files['size']=df_files['bytes'].apply(size)
            df_files.drop(['bytes'], axis=1, inplace=True)
            st.write('Found!')
            return df_files
        else:
            st.write('Pass')
    except:
        st.write('cloud checking failed')
        pass



    #add magnet to debrid
    try:
        magnet = df_cached.loc[i,'magnet']

        response = s.post(
            'https://api.real-debrid.com/rest/1.0/torrents/addMagnet'
            ,{"magnet" : magnet}
            ,headers={"Authorization": f"Bearer {api}"}
        )
        if not response.ok:
            st.write("error adding magnet, response not ok")
            return None
    except:
        st.write('error adding magnet --')
        return None

    #start magnet link
    try:
        id_ = response.json()['id']
        url = f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{id_}"
        response = requests.post(
            url
            ,{"files": "all"}
            ,headers={"Authorization": f"Bearer {api}"}
        )

        if not response.ok:
            st.write("error starting magnet")
            return None

    except:
        st.write('error starting magnet')
        return None


    #get cached magnet link
    try:
        url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{id_}"
        response = requests.get(
            url
            ,headers={"Authorization": f"Bearer {api}"}
        )
        links = response.json()['links']
        if response.ok:
            st.write('magnet added')
        else:
            st.write('error getting files')
            return None
    except:
        st.write('error getting files')
        return None

    df_files= pd.DataFrame(response.json()['files']).drop(['id', 'selected'], axis =1).rename({'path':'filename'}, axis=1)
    df_files['size']=df_files['bytes'].apply(size)
    df_files.drop(['bytes'], axis=1, inplace=True)
    return df_files




def unrestrict(i=[-1]):
    global download_links
    if isinstance(i, int):
        i_=[]
        i_.append(i)
        i=i_

    result = []
    download_links = []

    #get unrestricted link
    for j,link in enumerate(links):
        if j not in i and i!=[-1]:
            continue
        try:
            response = requests.post(
                'https://api.real-debrid.com/rest/1.0/unrestrict/link'
                ,{"link": link}
                ,headers={"Authorization": f"Bearer {api}"}
            )


            if not response.ok:
                st.write('error unrestricting')
                return None

            response = response.json()
            result.append((response['filename'],response['download']))
            download_links.append(response['download'])



        except:
            st.write('error unrestricting')
            return None
    download_links = result
    return result


def download_link(content, filename):
    href = f'<a href="data:application/octet-stream;base64,{base64.b64encode(content).decode()}" download="{filename}">download streamable</a>'
    return href

def vlc_playlist(title):
    s = '#EXTM3U\n'
    df = pd.DataFrame(download_links).sort_values(by=0).reset_index(drop=True)
    for index, row in df.iterrows():
        s=s+'#EXTINF:-1,'+ row[0]+'\n'+row[1]+'\n'
    s = s.encode()
    # Display the download link
    return s
    



def write_with_color(text, color):
    st.markdown(f"<p style='color:{color}'>{text}</p>", unsafe_allow_html=True)

def write_with_larger_font(text, font_size):
    st.markdown(f"<p style='font-size:{font_size}px'>{text}</p>", unsafe_allow_html=True)


def set_text_style(text, background_color, text_color):
    styled_text = f"<p style='background-color: {background_color}; color: {text_color};'>{text}</p>"
    st.markdown(styled_text, unsafe_allow_html=True)


def show_scrape_results(title):
    if st.session_state['selected_site'] == 'ThePirateBay':
        search_tpb(title)
    elif st.session_state['selected_site'] == '1337x':
        search_1337x(title)

    filter_cached()
    df_cached = st.session_state['df_cached']
    # st.session_state['df_cached'] = df_cached
    number_of_results = len(df_cached)

        
    st.write('---')
    
    for i in range(0, number_of_results):

        if f'container{i}' not in st.session_state:
            st.session_state[f'container{i}'] = None
        
        if f'container{i}_is_expanded' not in st.session_state:
            st.session_state[f'container{i}_is_expanded'] = False

        title_ = f"{df_cached.iloc[i].loc['name']} [{df_cached.iloc[i].loc['size']}]"
        st.session_state[f'container{i}'] = st.expander(title_, expanded=st.session_state[f'container{i}_is_expanded'])
        with st.session_state[f'container{i}']:
            if f"container{i}button" not in st.session_state:
                st.session_state[f"container{i}button"] = False
            st.session_state[f"container{i}button"] = st.button("link", key = f"container{i}button_")
            if st.session_state[f"container{i}button_"]:   
                get_debrid_link(i)
                debrid_result = unrestrict()
                link, streamable  = st.columns((3,2))
                with link:
                    for file in debrid_result:
                        name1 = file[0]
                        link = file[1]
                        link = f"[{name1}]({link})"
                        st.markdown(link, unsafe_allow_html=True)
                with streamable:
                    st.markdown(download_link(vlc_playlist(title), f'{title}.m3u'), unsafe_allow_html=True)
            # st.session_state[f'container{i}_is_expanded'] = False

    

##############################################################    
        
width = 200
height = 300
flag=0
title = ''
black_image = Image.new("RGB", (width, height), color="black")
df_tmdb_results = pd.DataFrame()
buttons =[]
buttons_for_scrape_results = []   
            

st.set_page_config(page_title="Debrid Scrap", layout="wide")




if 'submit_clicked' not in st.session_state:
    st.session_state['submit_clicked'] = False

if 'title' not in st.session_state:
    st.session_state['title'] = ' '


if 'scrape_button_click' not in st.session_state:
    st.session_state['scrape_button_click'] = False

if 'selected_scrape_result' not in st.session_state:
    st.session_state['selected_scrape_result'] = -1

if 'df_cached' not in st.session_state:
    st.session_state['df_cached'] = pd.DataFrame()

if 'selected_site' not in st.session_state:
    st.session_state['selected_site'] = 'ThePirateBay'


empty, selectbox  = st.columns((7,1))
with selectbox:
	st.session_state['selected_site'] = st.selectbox('Select Site', ['ThePirateBay', '1337x'])

query = st.text_input('Search..')
button_clicked = st.button('Submit')


if button_clicked:
    st.session_state['submit_clicked'] = True

if st.session_state['submit_clicked']:
    st.session_state['click_'] = False
    show_scrape_results(query)
    
    

if st.session_state.get('scrape_button_click', False):
    df_cached = st.session_state['df_cached']
    get_debrid_link(st.session_state['selected_scrape_result'])
    debrid_result = unrestrict()
    for file in debrid_result:
        name1 = file[0]
        link = file[1]
        link = f"[{name1}]({link})"
        st.markdown(link, unsafe_allow_html=True)
    st.session_state['scrape_button_click'] = False
        
        









