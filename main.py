#!/usr/bin/env python
# coding: utf-8

# In[12]:


client_id = input('Enter Client ID: ')
client_secret = input('Enter Client Secret: ')
playlist_id = input('Enter Playlist ID: ')


# In[62]:


import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import ListedColormap, BoundaryNorm, LinearSegmentedColormap
import seaborn as sns 
import numpy as np


# In[16]:


# ------------------------------ Get Data from Spotify API ------------------------------ #
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Retrieve all tracks in the playlist
tracks = []
offset = 0
limit = 100
delay = 1  # Initial delay between requests (in seconds)
max_delay = 60  # Maximum delay between requests (in seconds)

while True:
    try:
        response = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        tracks.extend(response['items'])
        offset += limit
        
        if len(response['items']) < limit:
            break
        
        time.sleep(delay)  # Delay before the next request
    except spotipy.exceptions.SpotifyException as e:
        if "rate/request limit" in str(e):
            print(f"Rate limit exceeded. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # Increase the delay exponentially
        else:
            raise e

# Extract relevant information from each track
data = []
for track in tracks:
    artist_id = track['track']['artists'][0]['id']
    artist_info = sp.artist(artist_id)
    
    genres = artist_info['genres']
    artist_pop = artist_info['popularity']
    followers = artist_info['followers']
    
    track_info = {
        'name': track['track']['name'],
        'artist': track['track']['artists'][0]['name'],
        'artist_pop': artist_pop,
        'followers': followers,
        'album': track['track']['album']['name'],
        'duration_ms': track['track']['duration_ms'],
        'track_pop': track['track']['popularity'],
        'released': track['track']['album']['release_date'],
        'added_by': track['added_by']['id'],
        'genres': genres
    }
    data.append(track_info)

print('Done!')


# In[146]:


# ---------------------------------------------- Read in Collaborators -------------
user_ids = []
for track in data:
    user_ids.append(track['added_by'])
user_ids = list(set(user_ids))
print('Total Collaborators: %d' % (len(user_ids)))
print('Total # of Tracks: %d' % (len(tracks)))

def get_user_songs(user_id, data):
    user_songs = []
    for track in data:
        if track['added_by'] == user_id:
            song_info = {
                'name': track['name'],
                'artist': track['artist'],
                'artist_pop': track['artist_pop'],
                'followers': track['followers'],
                'album': track['album'],
                'duration_ms': track['duration_ms'],
                'track_pop': track['track_pop'],
                'released': track['released'],
                'genres': track['genres']
            }
            user_songs.append(song_info)
    return user_songs

def get_all_songs(data):
    all_songs = []
    for track in data:
        song_info = {
            'name': track['name'],
            'artist': track['artist'],
            'artist_pop': track['artist_pop'],
            'followers': track['followers'],
            'album': track['album'],
            'duration_ms': track['duration_ms'],
            'track_pop': track['track_pop'],
            'released': track['released'],
            'added_by': track['added_by'],
            'genres': track['genres']
        }
        all_songs.append(song_info)
    return all_songs

print("\nI will now provide you with a sample of songs from the playlist. \nFor each song, enter the first name of the person who added that song.\n\n")

collaborators = []
user_names = []

for user_id in user_ids:
    song = get_user_songs(user_id, data)[0]
    print('%s added %s by %s. ' % (user_id, song['name'], song['artist']))
    user_name = (input("What is this collaborator's first name? "))
    print('\n')

    collaborators.append(tuple([user_id, user_name]))
    user_names.append(user_name)


# In[148]:


def get_user_genres(user_id, data, N):
    # return N genres for each artist (set to N = -1 to return all genres)
    user_genres = []
    for track in data:
        if track['added_by'] == user_id:
            if N == -1:
                genres = track['genres']
            else:
                genres = track['genres'][:N]
            if not genres: continue
            user_genres.append(genres)
    return user_genres

def get_total_genres(data):
    nulls = 0
    genres = []
    for track in data:
        genre = track['genres'][:1]    # modify this to limit genres
        if not genre: 
            nulls = nulls + 1
            continue
        genres.append(genre)
    return genres

def genre_count(user_genres):
    genre_count = {}
    
    for track_genres in user_genres:
        for genre in track_genres:
            if genre in genre_count:
                genre_count[genre] += 1
            else:
                genre_count[genre] = 1
    
    return genre_count

def plot_genres(genre_count, user):
    if genre_count is None or not genre_count:
        print("No data available to create the pie chart.")
        return

    # Sort the dictionary by frequency in descending order
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)

    # Extract the genres and their counts
    genres, counts = zip(*sorted_genres)

    # Create a pie chart
    plt.figure(figsize=(10, 10))
    plt.pie(counts, labels=genres, autopct='%1.1f%%', colors=sns.color_palette('Paired'))
    plt.title('Genre Distribution: ' + user)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.tight_layout()

    # Save the chart
    plt.savefig('genres_' + str.lower(user) + '.png')

def plot_total_genres(genre_count):
    if genre_count is None or not genre_count:
        print("No data available to create the pie chart.")
        return

    # Sort the dictionary by frequency in descending order
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    other_count = 0
    for genre in sorted_genres:
        if genre[1] <= 2:
            other_count = other_count + genre[1]

    sorted_genres = [g for g in sorted_genres if g[1] > 2]    
    sorted_genres.append(('other', other_count))
    
    # Extract the genres and their counts
    genres, counts = zip(*sorted_genres)
    
    # Create a pie chart
    plt.figure(figsize=(10, 10))
    plt.pie(counts, labels=genres, autopct='%1.1f%%', colors=sns.color_palette('Paired'))
    plt.title('Genre Distribution: Total')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.tight_layout()

    # Save the chart
    plt.savefig('genres_total.png')


# In[150]:


def get_userid(name):
    for u in collaborators:
        if u[1] == name: return u[0]
    print('Collaborator does not exist.')


# In[162]:


# needs to be updated to limit number of genres?
def genre_chart(name):
    if name == 'all': # all users individually 
        for u in collaborators:
            plot_genres(genre_count(get_user_genres(u[0],data,-1)), u[1])
    elif name == 'total': # overall playlist data
        plot_total_genres(genre_count(get_total_genres(data)))
    elif user in user_names:
        user_id = get_userid(name)
        plot_genres(genre_count(get_user_genres(user_id,data,-1)), name)
    else:
        print('Invalid User\n')
        return


# In[192]:


# Create a correlation matrix showing taste match between users
def plot_correlation():
    user_genres = {}
    for u in collaborators:
        user_genres[u[1]] = list((genre_count(get_user_genres(u[0],data,-1))).keys())
    
    # Initialize the correlation matrix with zeros
    num_users = len(collaborators)
    correlation_matrix = np.zeros((num_users, num_users))

    # Calculate the percentage of shared genres for each pair of users
    for i in range(num_users):
        for j in range(num_users):
            if i == j:
                correlation_matrix[i, j] = None  # Set self-match to -1
            else:
                user1_genres = set(user_genres[user_names[i]])
                user2_genres = set(user_genres[user_names[j]])
            
                shared_genres = len(user1_genres.intersection(user2_genres))
                total_genres = len(user1_genres.union(user2_genres))
            
                percentage = shared_genres / total_genres
                correlation_matrix[i, j] = percentage

    # Save the correlation matrix as a heatmap
    # max match set to 25%; make this a variable!
    plt.figure(figsize=(8, 6))
    im = plt.imshow(correlation_matrix, cmap=sns.color_palette("crest", as_cmap=True), interpolation='nearest', vmin=0, vmax=1)
    cbar = plt.colorbar(im, label='Taste Match')
    plt.clim(0,0.25)
    cbar.set_ticks([0, 0.05, 0.1, 0.15, 0.2, 0.25]) 
    cbar.set_ticklabels(['0%', '5%', '10%', '15%', '20%', '25%'])
    plt.xticks(range(num_users), user_names, rotation=45)
    plt.yticks(range(num_users), user_names)

    plt.title('Genre Correlation Matrix')
    plt.tight_layout()
    plt.savefig('correlation.png')


# In[166]:


# Find the number of different genres a specific user listened to
def calculate_genre_variety(user_genres):
    genre_variety = {}
    
    for user, genres in user_genres.items():
        unique_genres = set(genres)
        genre_count = len(unique_genres)
        genre_variety[user] = genre_count
    
    return genre_variety

def create_variety_chart(users, genre_varieties):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create the bar chart
    ax.bar(users, genre_varieties, color=sns.color_palette('Paired'))
    ax.bar_label(ax.containers[0])
    
    # Set the chart title and labels
    ax.set_title('Genre Variety')
    ax.set_xlabel('Collaborator')
    ax.set_ylabel('Number of Different Genres')
    
    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust the layout to prevent overlapping labels
    plt.tight_layout()
    
    # Save the chart
    plt.savefig('genre_variety.png')

# Make a plot showing how many different genres each user listened to
def plot_varieties():
    variety = sorted(calculate_genre_variety(user_genres).items(), key=lambda x: x[1], reverse=True)
    users, genre_varieties = zip(*variety)
    create_variety_chart(users, genre_varieties)


# In[178]:


# How many followers do each user's artists have?
def create_follower_chart(user_songs, user):
    followers_buckets = {
        '< 1K': 0,
        '1K - 10K': 0, 
        '10K - 100K': 0,
        '100K - 500K': 0,
        '500K - 1M': 0,
        '1M - 5M': 0,
        '5M - 10M': 0,
        '> 10M': 0
    }
    
    for song in user_songs:
        followers = song['followers']['total']

        if followers < 1000:
            print(song['artist']+" ("+str(followers)+") - "+song['name']+' | added by: '+user_id_to_name[song['added_by']])
            followers_buckets['< 1K'] += 1
        elif followers < 10000:
            followers_buckets['1K - 10K'] += 1
        elif followers < 100000:
            followers_buckets['10K - 100K'] += 1
        elif followers < 500000:
            followers_buckets['100K - 500K'] += 1
        elif followers < 1000000:
            followers_buckets['500K - 1M'] += 1
        elif followers < 5000000:
            followers_buckets['1M - 5M'] += 1
        elif followers < 10000000:
            followers_buckets['5M - 10M'] += 1
        else:
            followers_buckets['> 10M'] += 1
    
    buckets = list(followers_buckets.keys())
    counts = list(followers_buckets.values())

    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(buckets, counts, color=sns.color_palette('Paired'))
    ax.bar_label(ax.containers[0])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.xlabel('Followers/Artist')
    plt.ylabel('Number of Artists')
    plt.title('Artist Popularity: ' + user)
    plt.tight_layout()
    plt.savefig('artistpop_'+str.lower(user)+'.png')

def plot_followers(name):
    if name == 'all': # all users individually 
        for u in collaborators:
            create_follower_chart(get_user_songs(u[0],data), u[1])
    elif name == 'total': # overall playlist data
        create_follower_chart(get_all_songs(data), 'Total')
    elif name in user_names:
        user_id = get_userid(name)
        create_follower_chart(get_user_songs(user_id,data), name)
    else: 
        print('Invalid User\n')
        return


# In[186]:


# How popular are the songs each user listened to?
def create_popularity_chart(user_songs, user):
    popularity_buckets = {
        '0 - 10': 0,
        '10 - 20': 0,
        '20 - 30': 0,
        '30 - 40': 0,
        '40 - 50': 0,
        '50 - 60': 0,
        '60 - 70': 0,
        '70 - 80': 0,
        '80 - 90': 0,
        '90 - 100': 0
    }
    
    for song in user_songs:
        popularity = song['track_pop']
        if popularity < 10:
            popularity_buckets['0 - 10'] += 1
        elif popularity < 20:
            popularity_buckets['10 - 20'] += 1
        elif popularity < 30:
            popularity_buckets['20 - 30'] += 1
        elif popularity < 40:
            popularity_buckets['30 - 40'] += 1
        elif popularity < 50:
            popularity_buckets['40 - 50'] += 1
        elif popularity < 60:
            popularity_buckets['50 - 60'] += 1
        elif popularity < 70:
            popularity_buckets['60 - 70'] += 1
        elif popularity < 80:
            popularity_buckets['70 - 80'] += 1
        elif popularity < 90:
            popularity_buckets['80 - 90'] += 1
        else:
            popularity_buckets['90 - 100'] += 1
    
    buckets = list(popularity_buckets.keys()) 
    counts = list(popularity_buckets.values())
    
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(buckets, counts, color=sns.color_palette('Paired'))
    ax.bar_label(ax.containers[0])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.xlabel('Popularity Score/Track')
    plt.ylabel('Number of Tracks')
    plt.title('Track Popularity: ' + user)
    plt.tight_layout()
    plt.savefig('trackpop_'+str.lower(user)+'.png')

def plot_popularity(name):
    if name == 'all': # all users individually 
        for u in collaborators:
            create_popularity_chart(get_user_songs(u[0],data), u[1])
    elif name == 'total': # overall playlist data
        create_popularity_chart(get_all_songs(data), 'Total')
    elif name in user_names:
        user_id = get_userid(name)
        create_popularity_chart(get_user_songs(user_id,data), name)
    else: 
        print('Invalid User\n')
        return


# In[212]:


# What decades were each user's songs released in?
def create_decades_chart(user_songs, user):
    decade_counts = {}
    
    for song in user_songs:
        if song['released']:
            year = int(song['released'][:4])
            decade = (year // 10) * 10
            decade_counts[decade] = decade_counts.get(decade, 0) + 1
            
    decade_list = list(decade_counts.keys())
    
    min_decade = min(decade_list) if decade_counts else 1900
    max_decade = max(decade_list) if decade_counts else 2020
    all_decades = range(min_decade, max_decade + 10, 10)

    counts = [decade_counts.get(decade, 0) for decade in all_decades]
    
    fig, ax = plt.subplots(figsize=(6,6))
    # width variable may need to be modified for each chart?
    ax.bar(all_decades, counts, color=sns.color_palette('Paired'), width=6) 
    ax.bar_label(ax.containers[0])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.xlabel('Decade')
    plt.ylabel('Number of Songs')
    plt.title('Track Release Dates: '+user)
    plt.xticks(all_decades, [str(d)+'s' for d in all_decades])
    plt.tight_layout()
    plt.savefig('released_'+str.lower(user)+'.png')

def plot_decades(name):
    if name == 'all': # all users individually 
        for u in collaborators:
            create_decades_chart(get_user_songs(u[0],data), u[1])
    elif name == 'total': # overall playlist data
        create_decades_chart(get_all_songs(data), 'Total')
    elif name in user_names:
        user_id = get_userid(name)
        create_decades_chart(get_user_songs(user_id,data), name)
    else: 
        print('Invalid User\n')
        return

