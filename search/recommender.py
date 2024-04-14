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

song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),
                                          ('kmeans', KMeans(n_clusters=20,
                                                            verbose=False))
                                          ], verbose=False)
number_cols = ['acousticness', 'danceability', 'duration', 'energy',
                   'instrumentalness', 'explicit', 'liveness', 'loudness',
                   'speechiness', 'tempo', 'valence', 'cluster_label']
def get_song_data(song, features_data):
    try:
        song_data = features_data[(features_data['track_spotify_idx'] == song['track_spotify_idx'])].iloc[0]
        return song_data

    except IndexError:
        return None


def get_mean_vector(song_list, features_data):
    song_vectors = []
    #     number_cols.remove('cluster_label')

    for song in song_list:
        song_data = get_song_data(song, features_data)
        if song_data is None:
            #print('Warning: {} does not exist in database'.format(song['name']))
            continue
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)

    song_matrix = np.array(list(song_vectors))

    return np.mean(song_matrix, axis=0)


def flatten_dict_list(dict_list):
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []

    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)

    return flattened_dict


def recommend_songs(song_list, features_data, n_songs=50):
    metadata_cols = ['track_spotify_idx']
    song_dict = flatten_dict_list(song_list)

    song_center = get_mean_vector(song_list, features_data)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(features_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])

    rec_songs = features_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['track_spotify_idx'].isin(song_dict['track_spotify_idx'])]
    return rec_songs[metadata_cols].to_dict(orient='records')




def recommender_system(song_id):
    # myclient = pymongo.MongoClient("mongodb://34.121.79.26:27017")
    # mydb = myclient["trackinfo"]
    # mycol = mydb["tracks"]
    #
    # features = ['_id','acousticness', 'danceability', 'duration', 'energy',
    #             'instrumentalness', 'explicit', 'liveness', 'loudness',
    #             'speechiness', 'tempo', 'valence']
    #
    # data = pd.DataFrame(columns=features)
    #
    # for doc in mycol.find():
    #     print(doc["_id"])
    #     break
    #     values = [doc[feat] for feat in features]
    #     print(values)
    #     data = data.append(dict(zip(features, values)))
    global song_cluster_pipeline
    global number_cols
    recommend_file = 'search/recommender_tracks.csv'
    file_exists_r = exists(recommend_file)
    if file_exists_r:
        data= pd.read_csv("search/recommender_tracks.csv")
        data.drop(['Unnamed: 0'],axis=1,inplace =True)
        # data = data.reset_index()
    else:
        data = pd.read_csv('search/tracks.csv')

        data.drop_duplicates(inplace=True)
        # print(data.columns)
        # data = data.reset_index()
        # data.drop(['index'],axis=1,inplace =True)
        data.drop(['album.album_name',
                   'album.album_release_day', 'album.album_release_month',
                   'album.album_release_year', 'album.album_spotify_idx', 'album.artists'], axis=1, inplace=True)
        data = data.fillna(0)
        data["explicit"] = data["explicit"].astype(int)
        data.to_csv("recommender_tracks.csv")
        # feature_cols = ['acousticness', 'danceability', 'duration', 'energy',
        #                 'instrumentalness', 'explicit', 'liveness', 'loudness',
        #                 'speechiness', 'tempo', 'valence']
        #
        # scaler = MinMaxScaler()
        # normalized_df = scaler.fit_transform(data[feature_cols])
        # Load the KMeans model
    X = data.select_dtypes(np.number)
    # print(X)
    number_cols = list(X.columns)
    kmeans_model = 'kmeans_model.joblib'
    file_exists = exists(kmeans_model)
    if file_exists:
        song_cluster_pipeline = joblib.load('kmeans_model.joblib')
        song_cluster_labels = song_cluster_pipeline.predict(X)
        data['cluster_label'] = song_cluster_labels

    else:
        # print(X)
        song_cluster_pipeline.fit(X)
        # print(X)
        song_cluster_labels = song_cluster_pipeline.predict(X)
        data['cluster_label'] = song_cluster_labels
        joblib.dump(song_cluster_pipeline, 'kmeans_model.joblib')
    recom = recommend_songs([{'track_spotify_idx': song_id}], data)
    suggestions = []
    for r in recom:
        for r1 in r:
            suggestions.append(str(r[r1]))
    # suggestions = list(recom.values())
    return suggestions


# print(recommender_system('6403da5a449d11411de029c4'))

