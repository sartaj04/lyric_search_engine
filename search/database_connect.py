# import pymongo



# def search_lyrics(title):


#     myclient = pymongo.MongoClient("mongodb://34.121.79.26:27017")
#     mydb = myclient["LyricsSearchEngine"]
#     mycol = mydb["lyrics5M"]

#     for x in mycol.find():
#         if x["title"] == title:
#             print(x["lyrics"])