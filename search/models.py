from djongo import models


# Create your models here.
# class Songs(models.Model):
#     title = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     lyrics = models.TextField()
#     date_released = models.DateTimeField()
#
#
# class song_lyrics(models.Model):
#     _id = models.AutoField(primary_key=True, editable=False)
#     title = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     year = models.IntegerField(max_length=4)
#     views = models.IntegerField(max_length=20)
#     # lyrics = models.CharField(max_length=100000000)
#     id = models.IntegerField
#
#
# class song_lyrics1(models.Model):
#     _id = models.AutoField(primary_key=True, editable=False)
#     title = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     year = models.IntegerField(max_length=4)
#     views = models.IntegerField(max_length=20)
#     lyrics = models.CharField(max_length=100000000)
#     id = models.IntegerField


# class song_lyrics2(models.Model):
#     _id = models.ObjectIdField()
#     title = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     year = models.IntegerField(max_length=4)
#     views = models.IntegerField(max_length=20)
#     lyrics = models.CharField(max_length=100000000)
#     id = models.IntegerField


# class Testing2(models.Model):
#     id = models.ObjectIdField()
#     title = models.CharField(max_length=100)
#     tag = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     year = models.IntegerField(max_length=4)
#     views = models.IntegerField(max_length=20)
#     features = models.CharField(max_length=100)
#     lyrics = models.CharField(max_length=100000000)
#     id = models.IntegerField
#     image = models.CharField(max_length=300)

# class Testing3(models.Model):
#     _id = models.ObjectIdField()
#     title = models.CharField(max_length=100)
#     tag = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)
#     year = models.IntegerField(max_length=4)
#     views = models.IntegerField(max_length=20)
#     features = models.CharField(max_length=100)
#     lyrics = models.CharField(max_length=100000000)
#     id = models.IntegerField
#     image = models.CharField(max_length=300)

class albums(models.Model):
    _id = models.ObjectIdField()
    artist = models.JSONField
    album_name = models.CharField(max_length=100)
    album_release_year = models.IntegerField
    album_release_month = models.IntegerField
    album_release_day = models.IntegerField
    album_spotify_idx = models.CharField(max_length=200)


class artists(models.Model):
    _id = models.ObjectIdField()
    artist_name = models.CharField(max_length=100)
    album_spotify_idx = models.CharField(max_length=200)
    artist_popularity = models.IntegerField
    artist_genres = models.JSONField


class tracks(models.Model):
    _id = models.ObjectIdField()
    duration = models.IntegerField
    explicit = models.BooleanField
    track_spotify_idx = models.CharField(max_length=200)
    track_name = models.CharField(max_length=200)
    danceability = models.DecimalField
    energy = models.DecimalField
    loudness = models.DecimalField
    speechiness = models.DecimalField
    acousticness = models.DecimalField
    instrumentalness= models.DecimalField
    liveness = models.DecimalField
    valence = models.DecimalField
    tempo = models.DecimalField
    artists = models.JSONField
    album = models.JSONField
    lyrics = models.TextField()
    objects = models.DjongoManager()


