# Letterboxd-top-friend-movies

Find the movies, with the highest average rating from your Letterboxd friends.

The code works with 3.9.2 and requires the modules: 'Requests', 'bs4' (Beautiful Soup) and 'lxml'.

The programm takes your Letterboxd username and searches all users you are follwoing. You have also the choice to to select just some special users.
All rated movies of the given users are collected and an average rating for every movie is computed. You have the option to exclude the movies you watched.

The results can be filtered for the number of ratings per movie.
Finally the list is saved as csv in the same directioiry as this code.
