# importing libraries
import warnings

warnings.filterwarnings('ignore')
import re
import pandas as pd
import warnings
from stemming.porter2 import stem

warnings.filterwarnings('ignore')
from os.path import exists
import pymongo
import json

stop = []

def stopwords(path):
    global stop
    with open(path, 'r') as f_s:
        for x in f_s:
            stop.append(x.strip())

    return stop


def preprocess_lyric(text):
    p_words = []
    tokenization = re.sub('\W', ' ', text.lower()).split()

    for word in tokenization:
        # if word not in stop:
        if stem(word).strip() != "":
            p_words.append(stem(word).strip())
    return p_words


def preprocess(text):
    p_words = []
    tokenization = re.sub('\W', ' ', text.lower()).split()

    for word in tokenization:
        # if word not in stop:
        if stem(word).strip() != "":
            p_words.append(stem(word).strip())
    return p_words


def preprocess_normal(text):
    p_words = []
    tokenization = re.sub('\W', ' ', text.lower()).split()

    for word in tokenization:
        if word not in stop:
            if stem(word).strip() != "":
                p_words.append(stem(word).strip())
    return p_words


def generate_inverted_index(file_map):
    pos_index = {}
    for key in file_map:
        wordlist = file_map[key]
        for pos, word in enumerate(wordlist):
            if word in pos_index:
                if key in pos_index[word][1]:
                    pos_index[word][1][key].append(pos)
                else:
                    pos_index[word][1][key] = [pos]
            else:
                pos_index[word] = []
                pos_index[word].append(1)
                pos_index[word].append({})
                pos_index[word][1][key] = [pos]

    for term in pos_index:
        for i in pos_index[term]:
            pos_index[term][0] = len(pos_index[term][1])

    return pos_index


def get_lyric_filemap():
    myclient = pymongo.MongoClient(
        "mongodb://34.121.79.26:27017/autoReconnect=true&socketTimeoutMS=360000&connectTimeoutMS=360000")
    db = myclient["trackInfo"]
    tracks = db.tracks.find()
    file_map = {}
    num = 0
    for track in tracks:
        if track['lyrics'] is not None:
            file_map[track['track_spotify_idx']] = preprocess_lyric(track['lyrics'])
            print(num)
            num = num + 1
            x = db.tracks.update_one({'_id': track['_id']},
                                     {'$set':
                                          {'lyric_filemap_length': len(preprocess_lyric(track['lyrics']))}
                                      })

    with open('search/'+'lyric_filemap.json', 'w') as fpl:
        json.dump(file_map, fpl)
    return file_map


def get_title_filemap():
    myclient = pymongo.MongoClient(
        "mongodb://34.121.79.26:27017/autoReconnect=true&socketTimeoutMS=360000&connectTimeoutMS=360000")
    db = myclient["trackInfo"]
    tracks = db.tracks.find()
    file_map = {}
    for track in tracks:
        file_map[track['track_spotify_idx']] = preprocess_normal(track['track_name'])
        x = db.tracks.update_one({'_id': track['_id']},
                                 {'$set':
                                      {'title_filemap_length': len(preprocess_normal(track['track_name']))}
                                  })
    with open('search/'+'title_filemap.json', 'w') as fpt:
        json.dump(file_map, fpt)

    return file_map


def get_artist_filemap():
    myclient = pymongo.MongoClient(
        "mongodb://34.121.79.26:27017/autoReconnect=true&socketTimeoutMS=360000&connectTimeoutMS=360000")
    db = myclient["trackInfo"]

    artists = db.artists.find()
    file_map = {}
    for artist in artists:
        file_map[artist['artist_spotify_idx']] = preprocess_normal(artist['artist_name'])
        x = db.artists.update_one({'_id': artist['_id']},
                                  {'$set':
                                       {'artist_filemap_length': len(preprocess_normal(artist['artist_name']))}
                                   })
    with open('search/'+'artist_filemap.json', 'w') as fpa:
        json.dump(file_map, fpa)
    return file_map


def get_album_filemap():
    myclient = pymongo.MongoClient(
        "mongodb://34.121.79.26:27017/autoReconnect=true&socketTimeoutMS=360000&connectTimeoutMS=360000")
    db = myclient["trackInfo"]

    albums = db.albums.find()
    file_map = {}
    for album in albums:
        file_map[album['album_spotify_idx']] = preprocess_normal(album['album_name'])
        x = db.albums.update_one({'_id': album['_id']},
                                 {'$set':
                                      {'album_filemap_length': len(preprocess_normal(album['album_name']))}
                                  })
    with open('search/'+'album_filemap.json', 'w') as fpb:
        json.dump(file_map, fpb)
    return file_map

def read_whole_index_from_json(search_type):
    file_path = 'search/'+search_type+'ii.json'
    with open(file_path, 'r') as fp7:
        iindex = json.load(fp7)

    return iindex

def update_inverted_index(search_trpe):
    file = 'search/'+"newfilemap.json"
    file_exists = exists(file)
    if file_exists:
        with open('search/'+'newfilemap.json', 'r') as fp1:
            filemap = json.load(fp1)
    #output_index_into_mongodb(lyricii, "lyric")

    pos_index = read_whole_index_from_json(search_trpe)

    new_pos_index = {}
    for key in filemap:
        wordlist = filemap[key]
        for pos, word in enumerate(wordlist):
            if word in pos_index:
                new_pos_index[word] = pos_index[word]
                if key in new_pos_index[word][1]:
                    new_pos_index[word][1][key].append(pos)
                else:
                    new_pos_index[word][1][key] = [pos]
            else:
                pos_index[word] = []
                pos_index[word].append(1)
                pos_index[word].append({})
                pos_index[word][1][key] = [pos]

    with open('search/'+search_trpe+'ii.json', 'w') as fp:
        json.dump(pos_index, fp)

    return pos_index


class invertedindex:
    Instance = None

    def __init__(self):
        self.lyricii = {}
        self.albumii = {}
        self.titleii = {}
        self.artistii = {}
        self.lyric_filemap = {}
        self.album_filemap = {}
        self.title_filemap = {}
        self.artist_filemap = {}
        #self.data = pd.DataFrame() 
        # self.initialise()
        self.initialise()

    @staticmethod
    def instance():
        if invertedindex.Instance == None:
            invertedindex.Instance = invertedindex()
        return invertedindex.Instance

    def read_index_from_json(self):
        search_type = ['artist', 'album', 'title', 'lyric']
        lst = []
        for s in search_type:
            file_path = 'search/'+s + 'ii.json'
            with open(file_path, 'r') as fp7:
                iindex = json.load(fp7)
            lst.append(iindex)
        return lst

    def read_filemap_key_from_json(self):
        search_type = ['artist', 'album', 'title', 'lyric']
        lst = []
        for s in search_type:
            with open('search/'+s + '_filemap.json', 'r') as fp4:
                filemap = json.load(fp4)
            fmp = list(filemap.keys())
            lst.append(fmp)

        return lst

    def get_title_inverted_index(self):
        return self.titleii

    def get_lyric_inverted_index(self):
        return self.lyricii

    def get_artist_inverted_index(self):
        return self.artistii

    def get_album_inverted_index(self):
        return self.albumii

    def get_title_filemap(self):
        return self.title_filemap

    def get_lyric_filemap(self):
        return self.lyric_filemap

    def get_artist_filemap(self):
        return self.artist_filemap

    def get_album_filemap(self):
        return self.album_filemap
    
    #def get_recommender_data(self):
        #return self.data

    def initialise(self):
        stop = stopwords("search/englishST.txt")

        file1 = "search/lyric_filemap.json"
        file_exists1 = exists(file1)
        file2 = "search/title_filemap.json"
        file_exists2 = exists(file2)
        file3 = "search/album_filemap.json"
        file_exists3 = exists(file3)
        file4 = "search/artist_filemap.json"
        file_exists4 = exists(file4)
        if file_exists1 and file_exists2 and file_exists3 and file_exists4:
            self.artist_filemap, self.album_filemap, self.title_filemap, self.lyric_filemap = self.read_filemap_key_from_json()

        else:
            self.lyric_filemap = get_lyric_filemap()
            self.title_filemap = get_title_filemap()
            self.album_filemap = get_album_filemap()
            self.artist_filemap = get_artist_filemap()

        file5 = "search/lyricii.json"
        file_exists5 = exists(file5)
        file6 = "search/titleii.json"
        file_exists6 = exists(file6)
        file7 = "search/artistii.json"
        file_exists7 = exists(file7)
        file8 = "search/albumii.json"
        file_exists8 = exists(file8)
        if file_exists5 and file_exists6 and file_exists7 and file_exists8:
            self.artistii, self.albumii, self.titleii, self.lyricii = self.read_index_from_json()
        else:
            self.lyricii = generate_inverted_index(self.lyric_filemap)
            with open('search/lyricii.json', 'w') as fp5:
                json.dump(self.lyricii, fp5)
            # output_index_into_mongodb(lyricii, "lyric")

            self.titleii = generate_inverted_index(self.title_filemap)
            with open('search/titleii.json', 'w') as fp6:
                json.dump(self.titleii, fp6)
            # output_index_into_mongodb(titleii, "title")

            self.artistii = generate_inverted_index(self.artist_filemap)
            with open('search/artistii.json', 'w') as fp7:
                json.dump(self.artistii, fp7)
            # output_index_into_mongodb(artistii, "artist")

            self.albumii = generate_inverted_index(self.album_filemap)
            with open('search/albumii.json', 'w') as fp8:
                json.dump(self.albumii, fp8)
            # output_index_into_mongodb(albumii, "album")
        recommend_file = 'search/recommender_tracks.csv'
        file_exists_r = exists(recommend_file)
        print("done")
        '''
        if file_exists_r:
            self.data = pd.read_csv("search/recommender_tracks.csv")
            self.data.drop(['Unnamed: 0'], axis=1, inplace=True)
                # data = data.reset_index()
        else:
            self.data = pd.read_csv('search/tracks.csv')

            self.data.drop_duplicates(inplace=True)
                # print(data.columns)
                # data = data.reset_index()
                # data.drop(['index'],axis=1,inplace =True)
            self.data.drop(['album.album_name',
                           'album.album_release_day', 'album.album_release_month',
                           'album.album_release_year', 'album.album_spotify_idx', 'album.artists'], axis=1,
                          inplace=True)
            self.data = data.fillna(0)
            self.data["explicit"] = self.data["explicit"].astype(int)
            self.data.to_csv("recommender_tracks.csv")
        print("done")
        '''

