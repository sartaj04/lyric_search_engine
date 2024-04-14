# importing libraries
import math
import re
import warnings
from itertools import combinations
import json
import numpy as np
from pymongo import MongoClient
from stemming.porter2 import stem
import itertools
from search.inverted_index import invertedindex
# import interact_mongo
from os.path import exists
import numpy as np
import pandas as pd
import warnings
import pymongo
# import spotipy
# import os
# from spotipy.oauth2 import SpotifyClientCredentials
# from collections import defaultdict
warnings.filterwarnings('ignore')
import joblib
# from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from collections import defaultdict
from scipy.spatial.distance import cdist

warnings.filterwarnings('ignore')

clientlocal = MongoClient('mongodb://35.225.194.2:27017/')
client = MongoClient('mongodb://localhost:27017/')

class lyricsearchengine:
    def __init__(self, index_obj):
        index = index_obj
        # print(index.lyricii)

        self.stop = []
        # self.pos_index = {}
        self.spotify_ids = []
        # self.filemap = {}
        self.lyricii = index.get_lyric_inverted_index()
        self.albumii = index.get_album_inverted_index()
        self.titleii = index.get_title_inverted_index()
        self.artistii = index.get_artist_inverted_index()
        self.lyric_filemap = index.get_lyric_filemap()
        self.album_filemap = index.get_album_filemap()
        self.title_filemap = index.get_title_filemap()
        self.artist_filemap = index.get_artist_filemap()



    def preprocess_lyric(self, text):
        p_words = []
        tokenization = re.sub('\W', ' ', text.lower()).split()

        for word in tokenization:
            # if word not in stop:
            if stem(word).strip() != "":
                p_words.append(stem(word).strip())
        return p_words


    def preprocess_normal(self, text):
        p_words = []
        tokenization = re.sub('\W', ' ', text.lower()).split()

        for word in tokenization:
            if word not in self.stop:
                if stem(word).strip() != "":
                    p_words.append(stem(word).strip())
        return p_words


    def stopwords(self, path):
        # global stop
        with open(path, 'r') as f_s:
            for x in f_s:
                self.stop.append(x.strip())

        return self.stop

    def read_index_from_json(self, search_type, query):
        # if search_type ==
        # file_path = search_type+'ii.json'
        # with open(file_path, 'r') as fp7:
        #     iindex = json.load(fp7)
        ii = {}
        real_query = []
        if search_type == 'artist':
            query = self.preprocess_normal(query)
            iindex = self.artistii
        elif search_type == 'album':
            query = self.preprocess_normal(query)
            iindex = self.albumii
        elif search_type == 'title':
            query = self.preprocess_normal(query)
            iindex = self.titleii
        else:
            query = self.preprocess_lyric(query)
            iindex = self.lyricii

        for term in query:
            if term in iindex.keys():
                ii[term] = iindex[term]
                real_query.append(term)

        realquery_string = " ".join(real_query)

        return ii, realquery_string

    def read_filemap_key_from_json(self, search_type):
        filemap = []
        # with open(search_type + '_filemap.json', 'r') as fp4:
        #     artist_filemap = json.load(fp4)
        if search_type == 'artist':
            filemap1 = self.artist_filemap
        elif search_type == 'album':

            filemap1 = self.album_filemap
        elif search_type == 'title':

            filemap1 = self.title_filemap
        else:

            filemap1 = self.lyric_filemap
        for key in filemap1:
            filemap.append(key)

        return filemap

    def read_related_info_from_mongodb(self, spotify_id, search_type):
        myclient = MongoClient("mongodb://34.121.79.26:27017/autoReconnect=true&socketTimeoutMS=360000&connectTimeoutMS=360000")
        mydb = myclient["trackInfo"]
        mycol = mydb["tracks"]
        data = mycol.find_one({"track_spotify_idx": spotify_id})
        search_id = []
        if search_type == 'artist':
            for result in data['artists']:
                search_id.append(result['artist_spotify_idx'])
        elif search_type == 'album':
            search_id.append(data['album']['album_spotify_idx'])
        elif search_type == 'track_name':
            search_id.append(spotify_id)

        return search_id


    def bm25(self, query,search_type):
        terms = self.preprocess_normal(query)
        score = {}
        filemap = self.read_filemap_from_db(search_type,self.spotify_ids)

        l = 0
        for sid1 in self.spotify_ids:
            l += filemap[sid1]
        l_ = l / len(self.spotify_ids)

        for sid in self.spotify_ids:
            weight = 0
            ld = filemap[sid]
            k = 1.5
            for term in terms:
                if sid in self.pos_index[term][1]:
                    dl = self.pos_index[term]
                    tf_td = len(dl[1][sid])
                    dft = len(self.pos_index[term][1])
                    # wtd1 = ((1 + math.log10(tf_td)) * math.log10(len(song_names) / dft))

                    wtd2 = (tf_td / ((k * (ld / l_)) + tf_td + 0.5)) * math.log10(
                        (len(self.spotify_ids) - dft + 0.5) / (dft + 0.5))
                    weight = weight + wtd2
            score[str(sid)] = weight

        score = sorted(score.items(), key=lambda x: -x[1])
        result_list = []

        for i, (k, v) in enumerate(score):
            if i in range(0, 10):
                result_list.append(str(k) + ',' + ('%.4f' % v))

        return result_list


    def compute_tf(self, song_lyrics: list) -> dict:
        tf = {}
        for word in song_lyrics:
            tf[word] = tf.get(word, 0) + 1
        return tf


    # ranked
    def tfidf(self, query,spotify_ids,pos_index):
        terms = query.split()
        score = {}
        for sid in spotify_ids:
            weight = 0
            for term in terms:
                if sid in pos_index[term][1]:
                    dl = pos_index[term]
                    tf_td = len(dl[1][sid])
                    dft = len(pos_index[term][1])
                    wtd = ((1 + math.log10(tf_td)) * math.log10(len(spotify_ids) / dft))
                    weight = weight + wtd
            score[str(sid)] = weight

        score = sorted(score.items(), key=lambda x: -x[1])

        result_list = []

        for i, (k, v) in enumerate(score):
            if i in range(0, 300):
                result_list.append(str(k) + '|' + ('%.4f' % v))

        return result_list

    #tfidf cosine
    def build_vocabulary(self, pos_index):
        return sorted(list(pos_index.keys()))


    def build_tf_vector(self, query, vocabulary):
        tf_vector = [0] * len(vocabulary)

        for term in query:
            if term in vocabulary:
                index = vocabulary.index(term)
                tf_vector[index] += 1

        return tf_vector


    def build_tfidf_vector(self, tf_vector, idf_vector):
        return [tf * idf for tf, idf in zip(tf_vector, idf_vector)]


    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0

        similarity = dot_product / (norm_vec1 * norm_vec2)
        return similarity

    def read_index_from_mongodb(self, search_type, query):
        myclient = pymongo.MongoClient("mongodb://34.121.79.26:27017/")
        mydb = myclient["indices"]
        if (search_type == "lyric"):
            mycol = mydb["lyricIndex"]
            query = self.preprocess_lyric(query)
        elif (search_type == "title"):
            mycol = mydb["titleIndex"]
            query = self.preprocess_normal(query)
        elif (search_type == "artist"):
            mycol = mydb["artistIndex"]
            query = self.preprocess_normal(query)
        elif (search_type == "album"):
            mycol = mydb["albumIndex"]
            query = self.preprocess_normal(query)

        ii = {}
        real_query = []

        for term in query:
            myquery = {"index_name": term}
            x = mycol.find_one(myquery)
            i = 0
            inner_dict = {}
            if x is not None:
                for song in x["index_ids"]:
                    inner_dict[song] = x["index_location"][i]
                    i = i + 1
                ii[x["index_name"]] = [x["index_times"], inner_dict]
                real_query.append(x["index_name"])

        realquery_string = " ".join(real_query)

        return ii, realquery_string

    def tfidf_cosine_similarity(self, query,spotify_ids,pos_index):
        query = self.preprocess_lyric(query)
        vocabulary = self.build_vocabulary(pos_index)

        # Calculate the IDF vector for the vocabulary
        idf_vector = []
        for term in vocabulary:
            idf = math.log(len(spotify_ids) / int(pos_index[term][0]))
            idf_vector.append(idf)

        # Build the query TF vector and calculate the query TF-IDF vector
        query_tf_vector = self.build_tf_vector(query, vocabulary)
        query_tfidf_vector = self.build_tfidf_vector(query_tf_vector, idf_vector)

        # Initialize the similarities dictionary
        similarities = {}

        for sid in spotify_ids:
            # Build the song TF vector using the entire vocabulary
            song_terms = {}
            for term, (_, song_dict) in pos_index.items():
                if sid in song_dict:
                    song_terms[term] = song_dict[sid]

            song_tf_vector = self.build_tf_vector(song_terms, vocabulary)
            song_tfidf_vector = self.build_tfidf_vector(song_tf_vector, idf_vector)

            # Calculate cosine similarity between query TF-IDF vector and song TF-IDF vector
            similarity = self.cosine_similarity(query_tfidf_vector, song_tfidf_vector)

            # Store the similarity in the similarities dictionary
            similarities[sid] = similarity

        return similarities

    def sort_similarities(self, similarities):

        sorted_data = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        top_n_results = sorted_data[:10]
        return [f"{key},{value}" for key, value in top_n_results]

    def phrase_search(self, query, pos_index):
        tokens = query.split()
        num_tokens = len(tokens)
        if num_tokens == 1:
            # If the query consists of a single token, return the postings list for that token
            term = tokens[0]
            return {0: pos_index[term][1]} if term in pos_index else []

        resultlist = {i: [] for i in range(num_tokens)}
        lengthresult = 0
        z = 0
        da = [perm.split() for perm in self.generate_permutations(tokens)]

        while (lengthresult < 20) & (z < len(da)):

            # If the query consists of multiple tokens, perform phrase search
            positions = {}
            for i, token in enumerate(da[z]):
                if i == 0:
                    # For the first token, initialize the positions with the postings list for the token
                    positions = pos_index[token][1]
                else:
                    # For subsequent tokens, keep only the positions that are adjacent to the previous token
                    new_pos = {}
                    for candidate in pos_index[token][1]:
                        if candidate in positions:
                            for pospos in positions[candidate]:
                                for pos in pos_index[token][1][candidate]:
                                    distance = pos - pospos
                                    if distance == 1:
                                        new_pos[candidate] = pos_index[token][1][candidate]
                                        break
                    positions = new_pos

            if positions:
                index = num_tokens - len(da[z])
                resultlist[index].extend(positions.keys())
                resultlist[index] = list(set(resultlist[index]))

            lengthresult = sum(len(lst) for lst in resultlist.values())
            z += 1

        return resultlist



    def generate_permutations(self, tokens):
        num_tokens = len(tokens)
        permutations = []

        for length in range(num_tokens, 0, -1):
            for combination in combinations(tokens, length):
                permutations.append(' '.join(combination))

        # Remove duplicates and sort according to length
        sorted_permutations = sorted(list(set(permutations)), key=lambda x: (len(x), x), reverse=True)

        return sorted_permutations

    def lyric_search(self, query, spotify_id, pos_index):

        tfidf_results = self.tfidf(query, spotify_id, pos_index)
        phrase_search_results = self.phrase_search(query, pos_index)
        tfidf_scores = [result.split('|') for result in tfidf_results]
        tfidf_dict = {song: float(score) for song, score in tfidf_scores}

        token_length = len(self.preprocess_lyric(query))
        phrase_percentage = {}
        for num_tokens, song_list in phrase_search_results.items():
            for song in song_list:
                current_score = phrase_percentage.get(song, 0)
                if num_tokens >= current_score:
                    phrase_percentage[song] = ((token_length - num_tokens) / token_length) * 100

        final_scores = {}
        for song in set(tfidf_dict.keys()) | set(phrase_percentage.keys()):
            tfidf_score = tfidf_dict.get(song, 0)
            phrase_score = phrase_percentage.get(song, 0)
            # final_scores[song] = (weight_tfidf * tfidf_score) + (weight_phrase * phrase_score)
            final_scores[song] = tfidf_score * (2 + phrase_score)
            # final_scores[song] = tfidf_score * (1 + phrase_score)

        ranked_songs = dict(sorted(final_scores.items(), key=lambda x: x[1], reverse=True))
        ranked_songs = dict(itertools.islice(ranked_songs.items(), 40))

        # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        # mydb = myclient["trackInfo"]
        # mycol = mydb["tracks"]
        # result = {}
        # for key in ranked_songs:
        #     myquery = {'track_spotify_idx': key}
        #     x = mycol.find_one(myquery)
        #     result[x['track_name']] = ranked_songs[key]
        # top_songs = [song for song, score in ranked_songs[:20]]

        # print(ranked_songs)

        return ranked_songs


    def normalize(self, scores):
        min_score = min(scores.values())
        max_score = max(scores.values())

        if max_score == min_score:
            return {song: 0.5 for song in scores.keys()}

        return {song: (score - min_score) / (max_score - min_score) for song, score in scores.items()}


    def tfidf_ot(self, query,spotify_ids, pos_index):
        terms = query.split()
        score = {}
        for sid in spotify_ids:

            weight = 0
            for term in terms:
                if sid in pos_index[term][1]:
                    dl = pos_index[term]
                    tf_td = len(dl[1][sid])
                    dft = len(pos_index[term][1])
                    wtd = ((1 + math.log10(tf_td)) * math.log10(len(spotify_ids) / dft))
                    weight = weight + wtd
            score[str(sid)] = weight

        score = sorted(score.items(), key=lambda x: -x[1])

        result_list = {}

        for i, (k, v) in enumerate(score):
            if i in range(0, 40):
                result_list[k] = float('%.4f' % v)

        return result_list

    def long_query_handling(self, query, pos_index):
        query = query.split()
        freq_list = []
        for i, word in enumerate(query):
            freq_list.append((word, pos_index[word], i))
        freq_list.sort(key=lambda x: (x[1], x[2]))
        top_10 = freq_list[:10]
        top_10.sort(key=lambda x: query.index(x[0]))
        to_string = lambda lst: ' '.join([t[0] for t in lst])
        top_10 = to_string(top_10)
        return top_10

    def combine_search(self, query_a, query_b, search_type, num_top_search = 20,
                       coefficient_a = .7, coefficient_b =.3):

        result_list = []
        pos_index_a = {}
        spotify_ids_a = []
        pos_index_b = {}
        spotify_ids_b = []
        if query_a == "":
           # if len(query_b.split()) > 10:
            #    query_b = self.long_query_handling(query_b)
            spotify_ids_b = self.read_filemap_key_from_json(search_type)
            pos_index_b, real_query_b = self.read_index_from_json(search_type, query_b)
            if len(real_query_b.split()) >10:
                real_query_b = self.long_query_handling(real_query_b,pos_index_b)
            # it will return album , artist name or song (by song title)
            # case: only search b
            score_total = sorted(self.tfidf_ot(real_query_b, spotify_ids_b, pos_index_b).items(), key=lambda x: -x[1])
        else:
            #if len(query_a.split()) > 10:
             #   query_a = self.long_query_handling(query_a)
            spotify_ids_a = self.read_filemap_key_from_json('lyric')
            pos_index_a, real_query_a = self.read_index_from_json('lyric', query_a)
            if len(real_query_a.split()) > 10:
                real_query_a = self.long_query_handling(real_query_a,pos_index_a)
            score_a = self.lyric_search(real_query_a, spotify_ids_a,pos_index_a)
            if query_b == "":
                # case: only search a
                score_total = sorted(score_a.items(), key=lambda x: -x[1])
            else:
                # combine search on search a and search b
                #if len(query_b.split()) > 10:
                 #   query_b = self.long_query_handling(query_b)
                spotify_ids_b = self.read_filemap_key_from_json(search_type)
                pos_index_b, real_query_b = self.read_index_from_json(search_type, query_b)
                if len(real_query_b.split())>10:
                    real_query_b = self.long_query_handling(real_query_b, pos_index_b)
                score_b = self.tfidf_ot(real_query_b, spotify_ids_b, pos_index_b)
                score_total = {}
                for (k, v) in enumerate(score_a):
                    # if i in range(0, num_top_search):
                    # k is the song id
                    # using k to search in DB for score b id and its song name
                    id_b_list = self.read_related_info_from_mongodb(v, search_type)
                    max_score_b = 0
                    for id_b in id_b_list:
                        if id_b in score_b.keys():
                            if float(score_b[id_b]) > max_score_b:
                                max_score_b = float(score_b[id_b])
                    # only get the max score from search b
                    # v is the score a from that song; k is the song id
                    score_total[v] = coefficient_a * score_a[v] + coefficient_b * max_score_b
                score_total = sorted(score_total.items(), key=lambda x: -x[1])

        # k can be the song, album, artist id and v is their corresponding score
        for i, (k, v) in enumerate(score_total):
            if i in range(0, 40):
                result_list.append(str(k))

        return result_list



