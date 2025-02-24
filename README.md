# Collaborative Playlist Analyzer
This program takes data from any collaborative playlist on Spotify and produces some interesting plots. Here are some things you can do with it!
All of the functions with input take one string: a name, "all", or "total"

## make pie charts showing the genre distribution:
- `genre_chart(name)` for a specific user, where name is their first name
- `genre_chart(all)` to plot individual charts for all users
- `genre_chart(total)` for overall playlist data

## make a correlation matrix showing the taste match between collaborators:
- `plot_correlation()`

## make a chart showing the different number of genres each user listened to:
- `plot_varieties()`

## make a chart showing the number of followers for artists in the playlist:
- `plot_followers(name)`
- `plot_followers(all)`
- `plot_followers(total)`

## make a chart showing the popularity of songs in the playlist:
- `plot_popularity(name)`
- `plot_popularity(all)`
- `plot_popularity(total)`

## make a chart showing which decades the songs were released in:
- `plot_decades(name)`
- `plot_decades(all)`
- `plot_decades(total)`
