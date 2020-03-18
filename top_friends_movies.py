import sys
from multiprocessing import Pool
from time import sleep, time

import requests
from bs4 import BeautifulSoup
from urllib3 import disable_warnings, exceptions


def timer(func):
    def f(*args, **kwargs):
        start = time()
        rv = func(*args, **kwargs)
        end = time()
        print("Elapsed time:", end - start, "s")
        return rv

    return f


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


def save_csv(data, filename, head1, head2):
    import csv

    if not filename:
        filename = "results.csv"

    with open(filename, "w", newline="\n") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC, escapechar='"')
        writer.writerow(head1)
        writer.writerow(head2)
        for row in data:
            writer.writerow(row)


def user_check(username):
    # Checks is the user does exist on Letterboxd
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


def find_following():
    following = []
    url = "https://letterboxd.com/" + user + "/following/"
    while True:
        code = get_code(url)
        for person in code.find_all("td", class_="table-person"):
            user_url = person.h3.a["href"].replace("/", "")
            following.append(user_url)
        try:
            next_link = code.find("div", class_="pagination").find("a", class_="next")[
                "href"
            ]
            url = "https://letterboxd.com/" + next_link
        except (TypeError, AttributeError):
            return following


def movie_finder(username):
    movies = []
    url = "https://letterboxd.com/" + username + "/films/ratings/"
    while True:
        code = get_code(url)
        for item in code.find_all("li", class_="poster-container"):
            new_title = item.div["data-target-link"]
            rating = item.p.span["class"][1]
            rating = int(rating.replace("rated-", ""))
            if new_title in my_movies:
                pass
            else:
                movies.append([new_title, rating])
        try:
            next_link = code.find("div", class_="pagination").find("a", class_="next")[
                "href"
            ]
            url = "https://letterboxd.com/" + next_link
        except (TypeError, AttributeError):
            return movies


def my_movie_finder():
    url = "https://letterboxd.com/" + user + "/films"
    while True:
        code = get_code(url)
        for item in code.find_all("li", class_="poster-container"):
            new_title = item.div["data-target-link"]
            my_movies.append(new_title)
        try:
            next_link = code.find("div", class_="pagination").find("a", class_="next")[
                "href"
            ]
            url = "https://letterboxd.com/" + next_link
        except (TypeError, AttributeError):
            return my_movies


def movie_scraper(username):
    movies = []
    print(f'All of "{username}"s rated movies are searched...\n')
    movies = movie_finder(username)
    # comb_movies.append(movies)
    # {n} of {len(friend_li)} Users are already searched.')
    print(f'"{username}" is finished.')
    print(f"{len(movies)} movies were found \n")
    return movies


def init():
    global user, friend_li
    user, friend_li = None, None

    while not user:
        user = input(f"\nYour Letterboxd Username:\n")
        if not user:
            continue
        user = user_check(user)
        if not user:
            print("\nThis user does not exist!")

    while not friend_li:
        print(
            "\nIf you don't want all your friends to be included, add just some users in the form of:"
        )
        print('\t"user1, user2, user3"')
        friend_li = input(f"Else just press Enter.\n")

        if not friend_li:
            print("The friends list is generated...")
            friend_li = find_following()
        else:
            print("\nThe given users are checked...")
            friend_li = friend_li.replace(" ", "").split(",")

            # for i in range(len(friend_li)):
            #     friend_li[i] = user_check(friend_li[i])
            friend_li = [user_check(friend) for friend in friend_li]
            friend_li = [friend for friend in friend_li if friend]  # is not None

        if not friend_li:
            print("\nNo user was found!")

    print("\nThe number of rated movies is colleced...")
    movie_count = []
    for friend in friend_li:
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
    movie_sum = sum(movie_count)
    print(f"{movie_sum} movies were found.")
    comb_list = tuple(zip(friend_li, movie_count))
    comb_list = sorted(comb_list, key=lambda comb_list: comb_list[1], reverse=True)
    friend_li = [row[0] for row in comb_list]

    print(f"\n \nThese eligible users were given:")
    # readout of all user in friend_li
    for friend in comb_list:
        print(f"{friend[0]}, {friend[1]} rated movies")
    print("\n \n")

    return movie_sum


def preps():
    def ex_qu():
        exc = input(f"Should your watched movies be excluded from the list (y/n)?\n")
        if exc == "n":
            return False
        elif exc == "y":
            return True
        else:
            print('Please only enter "y" or "n"')
            return ex_qu()

    global my_movies
    # global user
    movie_sum = init()
    # user = "klaspas"
    # friend_li = ["mimiblitz", "slavae", "bleibtreuboy"]
    # movie_sum = 350

    exc = ex_qu()
    # If exclud your movies is True, here your watchlist is searched
    # and all movies are collected in my_movies
    my_movies = []
    if exc:
        url = "https://letterboxd.com/" + user + "/films"
        code = get_code(url)
        try:
            movie_c = code.find(text="Watched").parent["title"]
        except AttributeError:
            pass
        else:
            numb = ""
            for char in movie_c:
                if char.isdigit():
                    numb += char
        numb = int(numb)
        print(f"All {numb} movies '{user}' marked as watched are collected...")
        my_movies = my_movie_finder()
        print(f"{len(my_movies)} movies found. These will be excluded. \n\n")

    # Warning if a lot of movies will be searched
    if movie_sum > 1000:
        print(f"\n{movie_sum} movies will be searched.")
        print("This could take a while (about 1 min for 1000 movies).")
        start = input("Do you want to start? (y/n) \n")
        if "y" not in start:
            sys.exit()


@timer
def combine_movies():
    unique_movies = [item[0] for item in comb_movies[0]]
    unique_ratings = [[item[1]] for item in comb_movies[0]]
    for lst in comb_movies[1:]:
        for item in lst:
            if item[0] in unique_movies:
                ind = unique_movies.index(item[0])
                unique_ratings[ind].append(item[1])
                continue
            else:
                unique_movies.append(item[0])
                unique_ratings.append([item[1]])
    movie_rating = [[x, y] for x, y in zip(unique_movies, unique_ratings)]
    return movie_rating


def finish():
    # all ratings for a movie are collected and put in a list in unique_movies
    print("All ratings are combined...")
    unique_movies = combine_movies()

    # for every movie the average rating is calculated and the number of votes is written to the list
    unique_movies = [
        [round(sum(item[1]) / len(item[1]), 3), (len(item[1]))] + item
        for item in unique_movies
    ]

    print(f"{len(unique_movies)} unique rated movies are found. \n")
    print("Minimum number of ratings per movie? (You can changes this later)")

    output_s, rating_nr = results(unique_movies)

    # the list is saved as a csv file
    print("If you want to specifiy the dir and filename, enter it here.")
    filename = input('Else it will be saved as "results.csv" in the current dir')
    head1 = [f"Movies with at least {rating_nr} Votes, ranked by Avg and No. Votes."]
    head2 = ["Avg Rating, No Votes, Movies, all Votes"]
    save_csv(output_s, filename, head1, head2)
    print("List is saved")
    print("\n --------------------------------END--------------------------------\n")


def results(unique_movies, rating_nr=None):

    # Checks the input is an interger
    def check_nr(nr):
        if not nr.isdigit():
            print(f"Please enter a whole number. \n")
            return None
        nr = int(nr)
        if nr > friend_len:
            print(f"Please enter a number smaller than {friend_len+1}. \n")
            return None
        else:
            return nr

    while True:
        # if a number is already given, it is checked here
        if rating_nr:
            rating_nr = check_nr(rating_nr)

        # else the user is here asked for a number (and checked)
        while not rating_nr:
            nr = input(f"Enter a number between 1 and {friend_len}. \n")
            rating_nr = check_nr(nr)

        # the list is filterd. Movies with less than rating_nr votes are omitted
        # the list is sorted from the highes to lowest average, if equal it is sorted for the most votes
        output = [item for item in unique_movies if item[1] >= rating_nr]
        output_s = sorted(
            output, key=lambda output: (output[0], output[1]), reverse=True
        )
        out_len = len(output_s)
        print(f"\n \n{out_len} movies have at least {rating_nr} Vote(s)")
        print(
            f"Here are the top {min(out_len, 15)} movie(s), sorted by average rating and number of votes. \n"
        )
        print("Avg, Nr V, Titel, Individ Votes")
        for i in range(min(out_len, 15)):
            print(
                output_s[i][0],
                "\t",
                output_s[i][1],
                "\t",
                output_s[i][2].replace("/film/", "").replace("/", ""),
                output_s[i][3],
            )
        print("\n\n")

        # possibility to change rating_nr or to end the program
        print("If you want to change the rating number, enter a new number.")
        soc = input(
            'If you want to save the complete results write "s", if you want to end without saving press "x". \n'
        )
        if soc == "x":
            r = input("Are you shure you want to end without saving (y/n)?")
            if r == "y":
                print(
                    "\n --------------------------------END--------------------------------\n"
                )
                sys.exit()

        if soc == "s":
            return output_s, rating_nr

        rating_nr = soc


disable_warnings(exceptions.InsecureRequestWarning)

preps()

friend_len = len(friend_li)

proces = int(friend_len / 3) + 1
if proces > 12:
    proces = 12
if proces < 2:
    proces = friend_len

# Every rated movie from every user in friend_li is collected in comb_movies
comb_movies = []

if __name__ == "__main__":
    new_pool = Pool(processes=proces)
    comb_movies = new_pool.map(movie_scraper, friend_li, chunksize=1)

finish()
