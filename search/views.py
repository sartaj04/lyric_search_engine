from bson import ObjectId
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

from search.cw3_ir_integrated import lyricsearchengine
from search.recommender import recommender_system
from search.inverted_index import invertedindex
# from .models import song_lyrics2
from .models import albums
from .models import artists
from .models import tracks

from pymongo import MongoClient

# importing ObjectId from bson library
from bson.objectid import ObjectId

# Establishing connection with
# mongodb on localhost
client = MongoClient('34.121.79.26', 27017)

# Access database object
db = client['trackInfo']

# Access collection object
collection = db['tracks']

index_obj = invertedindex.instance()


# Create your views here.

def home(request):
    if request.method == "POST":
        obj = lyricsearchengine(index_obj)
        # query_search = obj.combine_search()

        query = obj.combine_search(query_a=request.POST['searched_lyrics'],query_b=request.POST['searched_filter'],search_type=request.POST['searchtype'])

        searched_lyrics = request.POST['searched_lyrics']

        return render(request, "search/search.html", {'searched_lyrics': searched_lyrics, 'query': query})
    else:
        return render(request, "search/search.html")


# def display(request):
#     if request.method == "POST":
#         query = query_search(query=request.POST['searched_lyrics'])
#
#         searched_lyrics = request.POST['searched_lyrics']
#
#         return render(request, "search/search-results.html", {'searched_lyrics': searched_lyrics, 'query': query})
#     else:
#         return render(request, "search/search-results.html")
def getRecommendations(request):
    song_details = []
    if request.method == "POST":
        song_id = recommender_system(song_id=request.POST['id'])
        #print("values", song_id)

        song_id = list(set(song_id))
        for i in range(len(song_id)):
            #print("song_id:", song_id[i])
            try:
                song_l = collection.find_one({"track_spotify_idx": song_id[i]})
                #print("song_l:", song_l)

                title = song_l.get('track_name')
                #print("title:", title)

                album = song_l.get('album').get('album_name')
                #print("album:", album)
                artist = song_l.get('artists')[0].get('artist_name')
                #print("artist:", artist)
                if (song_l.get('image_url')):
                    img = song_l.get('image_url')
                else:
                    img = "/static/image_not_found.jpeg"
                # if len(song_details) > 0:
                #
                #     for d in song_details:
                #
                #
                #         if title != d[0]['title']:
                #             if [{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}] not in song_details:
                #                 song_details.append(
                #                     [{'img': img, 'artist': artist, 'title': title, 'id': song_id[i], 'album': album}])
                #
                # else:
                song_details.append(
                    [{'img': img, 'artist': artist, 'title': title, 'id': song_id[i], 'album': album}])

                if len(song_details) == 15:
                    break

            except:
                continue

        return render(request, "search/recommender.html",
                      {'song_details': song_details})


    else:
        return render(request, "search/search-results.html")
    '''
    song_details = []
    #data = index_obj.get_recommender_data()
    if request.method=="POST":
        #r_obj = recommender(index_obj)
        song_id = recommender_system(song_id=request.POST['id'])
        print("values",song_id)

        song_id = list(set(song_id))
        for i in range(len(song_id)):
            print("song_id:", song_id[i])
            try:
                song_l = collection.find_one({"track_spotify_idx": song_id[i]})

                print(song_l)
                title = song_l.get('track_name')
                print(title)
                album = song_l.get('album').get('album_name')
                artist = song_l.get('artists')[0].get('artist_name')
                if (song_l.get('image_url')):
                    img = song_l.get('image_url')
                else:
                    img = "/static/image_not_found.jpeg"
                #if len(song_details) > 0:
                #if len(song_details)>0:

                    #for d in song_details:

                        #if title != d[0]['title']:
                    #if [[{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}]] not in song_details:
                      #  song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i], 'album': album}])
                        #song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}])

                #else:
                song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i], 'album': album}])

                    #song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}])

                if len(song_details) == 15:
                    break

                
                    for d in song_details:

                        if title != d[0]['title']:
                            if [{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}] not in song_details:
                                song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}])

                else:
                
                
                song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': song_id[i]}])

                if len(song_details) == 15:
                    break
                
                # if len(song_details)>0:
                #
                #     for d in song_details:
                #
                #         if title != d[0]['title']:
                #             song_details.append([{'artist': artist, 'title': title, 'id': song_id[i]}])
                #
                # else:
                # song_details.append([{'artist': artist, 'title': title, 'id': song_id[i]}])



                #if len(song_details)==20:
                 #   break

            except:
                continue
            print(song_details)

        return render(request, "search/recommender.html",
                              {'song_details': song_details})



        # return JsonResponse({'artist_details': JSON.stringify(artist_id_1)})
        # return JsonResponse({'data':song_details,'len':len(song_details)})
    else:
        return render(request, "search/search-results.html")
    '''
def getLyrics(request):
    if request.method == "POST":
        id_song = request.POST['id']
        song = collection.find_one({"track_spotify_idx":id_song})
        lyrics = song.get('lyrics')
        title = song.get('track_name')

        album = song.get('album').get('album_name')
        artist = song.get('artists')[0].get('artist_name')
        if (song.get('image_url')):
            img = song.get('image_url')
        else:
            img = "/static/image_not_found.jpeg"

        object_id = request.POST['id']

        return render(request, "search/lyrics.html", {'img': img, 'lyrics':lyrics, 'artist':artist,'title':title, 'album':album, 'id':object_id})
    else:
        return render(request, "search/lyrics.html")


def display(request):
    if request.method == "POST":
        searched_lyrics = request.POST['searched_lyrics']
        searched_filter = request.POST['searched_filter']
        song_details = []
        artist_names=[]
        album_names=[]
        search_type = request.POST['searchtype']
        #index_obj = invertedindex.instance()
        obj = lyricsearchengine(index_obj)
        # query_search = obj.combine_search()

        ids = obj.combine_search(query_a=request.POST['searched_lyrics'], query_b=request.POST['searched_filter'],
                                   search_type=request.POST['searchtype'])
        #print("ids",ids)

        # ids = ['6403da5a449d11411de029c4', '6403da5a449d11411de029cc', '6403da5a449d11411de029d5',
        #        '6403da5a449d11411de029d9', '6403da5a449d11411de029db']
        '''
        for i in range(len(ids)):
            song_l = collection.find_one({"track_spotify_idx":ids[i]})
            try:
                title = song_l.get('track_name')

                album = song_l.get('album').get('album_name')
                artist = song_l.get('artists')[0].get('artist_name')
                if(song_l.get('image_url')):
                    img = song_l.get('image_url')
                else:
                    img = "/static/image_not_found.jpeg"
        '''
        for i in range(len(ids)):

            if(search_type=='album' and searched_lyrics == ""):

                song_l = collection.find_one({"album.album_spotify_idx": ids[i]})
                try:
                    album_filter = song_l.get('album').get('album_name')
                    album_names.append([{'album_filter':album_filter,'id':ids[i]}])
                except:
                    continue

            elif(search_type=='artist' and searched_lyrics == ""):

                song_l = collection.find_one({"artists.artist_spotify_idx":ids[i]})
                try:
                    artist_filter = song_l.get('artists')[0].get('artist_name')
                    #print('artist_name',artist_filter)
                    artist_names.append([{'artist_filter':artist_filter,'id':ids[i]}])
                except:
                    continue

            else:
                song_l = collection.find_one({"track_spotify_idx": ids[i]})
                #print("song", song_l)
                try:

                    title = song_l.get('track_name')
                    #print("title", title)

                    album = song_l.get('album').get('album_name')
                    artist = song_l.get('artists')[0].get('artist_name')
                    #print("arist", artist)
                    if (song_l.get('image_url')):
                        img = song_l.get('image_url')
                    else:
                        img = "/static/image_not_found.jpeg"
                    #if len(song_details)>0:

                    #for d in song_details:

                        #if title != d[0]['title']:
                        #if [[{'img': img, 'artist': artist, 'title': title, 'id': ids[i]}]] not in song_details:
                            #song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i]}])
                            #song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i], 'album': album}])

                    #else:
                    song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i], 'album': album}])
                        #song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': ids[i]}])

                    if len(song_details) == 15:
                        break
                
                except:
                    continue
            # song_details.append([{'img': img,'artist': artist, 'title': title, 'id': ids[i]}])

        # song_details = list(set(song_details))
        return render(request, "search/search-results.html",
                      {'song_details': song_details, 'searched_lyrics': searched_lyrics,
                       'searched_filter': searched_filter,'artist_names':artist_names,'album_names':album_names})

        #return render(request, "search/search-results.html",
         #             {'song_details': song_details, 'searched_lyrics': searched_lyrics})
        #return JsonResponse({'artist_details': JSON.stringify(artist_id_1)})
        # return JsonResponse({'data':song_details,'len':len(song_details)})
    else:
        return render(request, "search/search-results.html")
    # song = song_lyrics2.objects.get(_id=ObjectId(id))
    # val = "lyrics :" + song.lyrics
    # return HttpResponse(val)
    # artist = request.GET.get('artist')
    # payload = []
    # if artist:
    #
    #     lyrics_objs = song_lyrics2.objects.get.filter(artist__icontains=artist)
    #     for lyrics_obj in lyrics_objs:
    #         payload.append(lyrics_obj.artist)
    # # console.log(data)
    #
    # return JsonResponse({'status': 200, 'data': payload})


def filters(request):
    if request.method == "POST":
        id_filter = request.POST['id']
        filter_value = request.POST['filter']
        filter_name = request.POST['value-name']
        song_details=[]
        #print('values',id_filter,filter_value,filter_name)
        if(filter_value== "album"):
            songs = collection.find({"album.album_spotify_idx": id_filter})
        else:
            songs = collection.find({"artists.artist_spotify_idx": id_filter})
        #print("songs",songs)
        for song in songs:
            #print("song",song)

            try:
                id_song = song.get('track_spotify_idx')
                title = song.get('track_name')
                #print("title", title)

                album = song.get('album').get('album_name')
                artist = song.get('artists')[0].get('artist_name')
                if (song.get('image_url')):
                    img = song.get('image_url')
                else:
                    img = "/static/image_not_found.jpeg"
                song_details.append([{'img': img, 'artist': artist, 'title': title, 'id': id_song, 'album': album}])
            except:
                continue

    return render(request, "search/filters.html",{'song_details': song_details,'filter_name':filter_name})
