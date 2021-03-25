import csv
import sys
from functools import partial
from multiprocessing import Pool, set_start_method
from time import sleep
from statistics import median
from math import sqrt

import requests
from bs4 import BeautifulSoup
from urllib3 import disable_warnings, exceptions


def avg(liste):
    return sum(liste) / len(liste)


def least_square(liste):
    liste = [i**2 for i in liste]
    return sqrt(sum(liste) / len(liste))


def weighted(liste):
    w_list = []
    weights = [100, 95, 80, 65, 40, 20, 5, 0, 0, 0]
    for i in liste:
        w_list.append(weights[int(i)])

    return avg(w_list)


class ltbxd():
    def __init__(self):
        pass

    def start(self):
        ''' Get info through user input
            All input is checked if it makes sense
            the friends list is sorted by rated movies
            user movies are collected if chosen
        '''

        user = get_user()
        friends = get_friends(user)
        movie_count = get_movie_count(friends)

        movie_sum = sum(movie_count)
        print(f"{movie_sum} movies were found.")

        # Sort friends for number of rated movies
        # to speed up collecting process
        comb_list = tuple(zip(friends, movie_count))
        comb_list = sorted(comb_list,
                           key=lambda comb_list: comb_list[1],
                           reverse=True)
        friends = [row[0] for row in comb_list]

        # readout of all friends
        print(f"\n \nThese eligible users were given:")
        for friend in comb_list:
            print(f"{friend[0]}, {friend[1]} rated movies")
        print("\n \n")

        # Question if movies in Watchlist should be excluded
        exc = ex_qu()
        # If exclud your movies is True, here your watchlist is searched
        # and all movies are collected in my_movies
        if exc:
            my_movies = movie_scraper(user, [])
            my_movies = [line[0] for line in my_movies]
            print(f"{len(my_movies)} movies found. These will be excluded. \n\n")

        else:
            my_movies = []

        # Warning if a lot of movies will be searched
        if movie_sum > 3000:
            print(f"\n{movie_sum} movies will be searched.")
            print(
                f"This could take a while, estimated time: {round(max(movie_count)/3000,1)} min.")
            start = input("Do you want to start? (y/n) \n")
            if "y" not in start:
                sys.exit()

        self.user = user
        self.friends = friends
        self.my_movies = my_movies

    def start_manuell(self):
        ''' same as start, just everything is already given
            just change the info here
        '''

        user = 'klaspas'
        print('User:', user)
        friends = ['zaron', 'dieserdopo']
        print('Given Friends: ', friends)

        my_movies = []
        self.user = user
        self.friends = friends
        self.my_movies = my_movies

    def sp_scraper(self):
        ''' Singel Process Scraping
            for all friends all rated movies are collected
            in comb_movies
        '''
        comb_movies = []
        for friend in self.friends:
            movies = movie_scraper(friend, self.my_movies)
            comb_movies += movies

        self.comb_movies = comb_movies

    def mp_scraper(self):
        ''' Multi Process/Pralell Scraping
            else is same as sp_scraper
            The nuber of precesses is calculated by the number of friends
        '''

        if __name__ == "__main__":
            set_start_method("fork")

            # Number of paralles requests to Letteboxd is calculated
            # OPtimze time and don't risk to aktivate some spam filter
            friends_len = len(self.friends)
            proces = int(friends_len / 3) + 1
            if proces > 12:
                proces = 12
            if proces < 2:
                proces = friends_len

            # Every rated movie from every
            # user in friend_li is collected in comb_movies

            movie_scraper_fixed = partial(
                movie_scraper, my_movies=self.my_movies)

            new_pool = Pool(processes=proces)
            comb_movies_sep = []
            comb_movies_sep = new_pool.map(
                movie_scraper_fixed, self.friends, chunksize=1)

            comb_movies = []
            for usr in comb_movies_sep:
                comb_movies += usr
            self.comb_movies = comb_movies

    def top_movies(self):

        # all ratings for a movie are collected and put in a list in unique_movies
        print("All ratings are combined...")
        unique_movies = merge_movies(self.comb_movies)
        print(f"{len(unique_movies)} unique and rated movies are found. \n")
        # for every movie the average rating is calculated and the number of votes is written to the list
        movies_list = [[round(sum(item[1]) / len(item[1]), 3),
                        (len(item[1]))] + item for item in unique_movies]
        show_results(movies_list, len(self.friends))

    '''
    def closest_user(self, avg_fkt=avg):
        print('Your rated movies are collected')
        my_movies_rating = movie_scraper(self.user, [])
        my_movies = [item[0] for item in my_movies_rating]
        results = []

        for i, li in enumerate(self.comb_movies):
            diff_list = []
            counter = 0
            for item in li:
                if item[0] in my_movies:
                    index = my_movies.index(item[0])
                    other_rating = item[1]
                    my_rating = my_movies_rating[index][1]
                    difference = abs(my_rating - other_rating)
                    diff_list.append(difference)
                    counter += 1

            if counter > 0:
                result = [diff_list, counter, self.friends[i]]
                results.append(result)

        method1 = []
        for list_ in results:
            avg1 = [avg_fkt(list_[0]), list_[1], list_[2]]
            method1.append(avg1)
        method1_sorted = sorted(
            method1, key=lambda method1: (method1[0], method1[1]), reverse=True)

        method2 = []
        for list_ in results:
            avg2 = [least_square(list_[0]), list_[1], list_[2]]
            method2.append(avg2)
        method2_sorted = sorted(
            method2, key=lambda method2: (method2[0], method2[1]))

        method3 = []
        for list_ in results:
            avg3 = [avg(list_[0]), list_[1], list_[2]]
            method3.append(avg3)
        method3_sorted = sorted(
            method3, key=lambda method3: (method3[0], method3[1]))

        print('Weighted Avg')
        for line in method1_sorted:

            print(
                f'{line[2]}: {line[0]}%, {line[1]} Filmen')
        print('\n\nLeast Square')
        for line in method2_sorted:

            print(
                f'{line[2]}: {line[0]}, {line[1]} Filmen')

        print('\n\nAvgerage')
        for line in method3_sorted:
            print(
                f'{line[2]}: {line[0]}, {line[1]} Filmen')
    '''


def get_code(url):

    for _ in range(10):
        try:
            r = requests.get(url, verify=False, timeout=10)
            break
        except (
                requests.ConnectionError,
                requests.ConnectTimeout,
                requests.ReadTimeout,
                requests.exceptions.ChunkedEncodingError,
        ):
            print("Some connection problem, retry in 1s")
            sleep(1)
    else:
        print("No Connection available. The programm is stopped")
        sys.exit()

    code = BeautifulSoup(r.text, features="lxml")
    return code


def get_user():
    user = None
    while not user:
        user = input(f"\nYour Letterboxd Username:\n")
        if not user:
            continue
        user = user_check(user)
        if not user:
            print("\nThis user does not exist!")
    return user


def user_check(username):
    # Checks if the username does exist on Letterboxd
    username_c = username.replace("_", "")
    if not username_c.isalnum():
        print(f'The user "{username}" does not exist.')
        return None
    url = "https://letterboxd.com/" + username
    code = get_code(url)
    try:
        code.body.header.section
    except AttributeError:
        print(f'The user "{username}" does not exist.')
        return None
    return username


def get_friends(user):
    friends = None
    while not friends:
        print(
            "\nIf you don't want all your friends to be included, add just some users in the form of:"
        )
        print('\t"user1, user2, user3"')
        friends = input(f"Else just press Enter.\n")

        if not friends:
            print("The friends list is generated...")
            friends = find_following(user)
        else:
            print("\nThe given users are checked...")
            friends = friends.replace(" ", "").split(",")
            #  Checks if given names are real users
            #  and deltes if not
            friends = [friend for friend in friends if user_check(friend)]

        if not friends:
            print("\nNo user was found!")

    return friends


def find_following(user):
    following = []
    url = "https://letterboxd.com/" + user + "/following/"
    while True:
        code = get_code(url)
        for person in code.find_all("td", class_="table-person"):
            user_url = person.h3.a["href"].replace("/", "")
            following.append(user_url)
        try:
            next_link = code.find("div", class_="pagination").find(
                "a", class_="next")["href"]
            url = "https://letterboxd.com/" + next_link
        except (TypeError, AttributeError):
            return following


def get_movie_count(friends):
    print("\nThe number of rated movies is colleced...")
    movie_count = []
    for friend in friends:
        url = "https://letterboxd.com/" + friend + "/films/ratings/"
        code = get_code(url)
        try:
            movie_c = code.find(text="Ratings").parent["title"]
        except AttributeError:
            movie_c = 0
        else:
            numb = ""
            for char in movie_c:
                if char.isdigit():
                    numb += char
        movie_count.append(int(numb))
    return movie_count


def ex_qu():
    while True:
        exc = input(
            f"Should your watched movies be excluded from the list (y/n)?\n")
        if exc == "n":
            return False
        elif exc == "y":
            return True
        else:
            print('Please only enter "y" or "n"')


def movie_scraper(username, my_movies):
    movies = []
    print(f'All of "{username}"s rated movies are searched...\n')

    url = "https://letterboxd.com/" + username + "/films/by/member-rating/"
    while True:
        code = get_code(url)
        for item in code.find_all("li", class_="poster-container"):
            new_title = item.div["data-target-link"]
            if item.p.find("span", class_="rating") == None:
                print(f'"{username}" is finished.')
                print(f"{len(movies)} movies were found \n")
                return movies

            else:
                rating = item.p.span["class"][-1]
                rating = rating.replace("rated-", "")

            if new_title in my_movies:
                pass
            else:
                movies.append([new_title, int(rating)])

        try:
            next_link = code.find("div", class_="pagination").find(
                "a", class_="next")["href"]
            url = "https://letterboxd.com/" + next_link
        except (TypeError, AttributeError):
            print(f'"{username}" is finished.')
            print(f"{len(movies)} movies were found \n")
            return movies


def merge_movies(comb_movies):

    unique_movies = []
    comb_movies = sorted(comb_movies, key=lambda comb_movies: comb_movies[0])
    while comb_movies:
        rating = [None]
        movie, rating[0] = comb_movies[0]

        for item in comb_movies[1:]:
            if item[0] == movie:
                rating.append(item[1])
                continue
            else:
                break
        unique_movies.append([movie, rating])
        del comb_movies[:len(rating)]
    return unique_movies


def show_results(movies_list, friends_nr):

    threshold = None
    print("Minimum number of ratings per movie? (You can changes this later)")
    while True:
        # if a number is already given, it is checked here
        if threshold:
            threshold = check_nr(threshold, friends_nr)

        # else the user is here asked for a number (and checked)
        while not threshold:
            threshold = input(f"Enter a number between 1 and {friends_nr}. \n")

            threshold = check_nr(threshold, friends_nr)

        # the list is filterd. Movies with less than threshold votes are omitted
        # the list is sorted from the highes to lowest average, if equal it is sorted for the most votes
        movies_filtered = [
            movie for movie in movies_list if movie[1] >= threshold]
        print(movies_filtered[:3])
        movies_sorted = sorted(movies_filtered, key=lambda movies_filtered: (
            movies_filtered[0], movies_filtered[1]), reverse=True)
        print(movies_sorted[:3])
        movies_nr = len(movies_sorted)
        print(f"\n \n{movies_nr} movies have at least {threshold} Vote(s)")
        print(
            f"Here are the top {min(movies_nr, 15)} movie(s), sorted by average rating and number of votes. \n"
        )
        print("Avg, Nr V, Titel, Individ Votes")
        for i in range(min(movies_nr, 15)):
            print(
                movies_sorted[i][0], "\t",
                movies_sorted[i][1], "\t",
                movies_sorted[i][2].replace("/film/", "").replace("/", ""),
                movies_sorted[i][3])
        print("\n\n")

        # possibility to change threshold or to end the program
        print("If you want to change the rating number, enter a new number.")
        question = input(
            'If you want to save the complete results write "s", if you want to end without saving press "x". \n'
        )
        if question == "x":
            r = input("Are you shure you want to end without saving (y/n)?")
            if r == "y":
                print(
                    "\n --------------------------------END--------------------------------\n"
                )
                sys.exit()

        if question == "s":
            save_results(movies_sorted, threshold)

        threshold = question


def check_nr(threshold, friends_nr):
    # Checks the input is an interger, if not it returns None
    if not threshold.isdigit():
        print(f"Please enter a whole number. \n")
        return None
    elif (int(threshold) > friends_nr):
        print(f"Please enter a number smaller than {friends_nr+1}. \n")
        return None
    else:
        return int(threshold)


def save_results(data, threshold):

    print("If you want to specifiy the dir and filename, enter it here.")
    filename = input(
        'Else it will be saved as "results.csv" in the current dir \n')
    head1 = [
        f"Movies with at least {threshold} Votes, ranked by Avg and No. Votes."
    ]
    head2 = ["Avg Rating, No Votes, Movie, List of  Votes"]

    if not filename:
        filename = "results.csv"

    # the list is saved as a csv file
    with open(filename, "w", newline="\n") as csv_file:
        writer = csv.writer(csv_file,
                            quoting=csv.QUOTE_NONNUMERIC,
                            escapechar='"')
        writer.writerow(head1)
        writer.writerow(head2)
        for row in data:
            writer.writerow(row)

    print("List is saved")


if __name__ == '__main__':

    disable_warnings(exceptions.InsecureRequestWarning)

    lb = ltbxd()

    lb.start_manuell()
    # lb.start()

    lb.mp_scraper()

    lb.top_movies()
