__author__ = 'Serina Chang <sc3003@columbia.edu>'
__date__ = 'Jan 28, 2019'

from bs4 import BeautifulSoup
import csv
from make_data import *
import os
import requests

PATH_TO_OSCARS = '../data/oscars/'
IMDB_ID_LENGTH = 7

def pad_id(id):
    """
    Pads id to the standard length.
    """
    len_padding = IMDB_ID_LENGTH - len(id)
    padding = '0' * len_padding
    return padding + id

def parse_oscars_csv():
    """
    Parses the csv that contains information on Oscar-nominated movies.
    """
    movies = []
    with open(PATH_TO_OSCARS + 'noms.csv', 'r') as f:
        for row in csv.DictReader(f):
            name = row['Movie Name'].strip()
            year = row['Nom. Year'].strip()
            id = row['IMDB ID'].strip()
            won = row['Won (Y/N)'].strip().upper() == 'Y'
            movies.append((name, year, id, won))
    return movies

def get_num_oscars_parsed():
    """
    Returns how many data files exist in the corpus already.
    """
    files = os.listdir(PATH_TO_OSCARS)
    count = [1 if f.endswith('.txt') else 0 for f in files]
    return sum(count)

def make_imdb_url(id):
    """
    Creates the IMDb movie page url for movie with the given IMDb id.
    """
    return 'https://www.imdb.com/title/tt{}/'.format(id)

def make_corpus(max_movies = None, continue_work = True):
    """
    Primary function. Creates the Oscars metadata corpus by scraping metadata
    from IMDb for each Oscar-nominated movie in the "noms.csv" file.
    Metadata includes title, year, genres, movie rating, director
    names and genders, actor names and genders, and Bechdel score.
    """
    movies = parse_oscars_csv()
    if continue_work:
        processed_before = get_num_oscars_parsed()
        print('Processed {} Oscar noms before'.format(processed_before))
        movies = movies[processed_before:]
    print('Num to process:', len(movies))
    bechdel_dict = make_bechdel_dict()
    if max_movies is not None and len(movies) > max_movies:
        movies = movies[:max_movies]
    for name, year, id, won in movies:
        print(name, year)
        try:
            id = pad_id(id)
            movie_url = make_imdb_url(id)
            movie_page = BeautifulSoup(requests.get(movie_url).content, 'html.parser')
            title, year, genres = extract_imdb_headings(movie_page)
            rating = extract_imdb_rating(movie_page)
            credits_url = make_full_credits_url(id)
            credits_page = BeautifulSoup(requests.get(credits_url).content, 'html.parser')
            dir_tuples, char_tuples = extract_credits(credits_page)
            bechdel_score = bechdel_dict.get(id)
            metadata = format_metadata(id, title, year, genres, rating, dir_tuples, char_tuples, bechdel_score)
            new_fn = PATH_TO_OSCARS + '{}___{}.txt'.format('_'.join(name.split()), year)
            with open(new_fn, 'w') as f:
                f.write(metadata)
                f.write('Oscar Best Picture Winner: {}\n'.format(won))
        except ValueError:
            print('ValueError: skipping', name)

if __name__ == "__main__":
    make_corpus()