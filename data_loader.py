__author__ = 'Kara Schechtman <kws2121@columbia.edu>, Serina Chang <sc3003@columbia.edu>'
__date__ = 'Jan 15, 2019'

DATA_PATH = './data/movies/'
IMDB_KEY = 'IMDB: '
TITLE_KEY = 'Title: '
YEAR_KEY = 'Year: '
GENRE_KEY = 'Genre: '
DIRECTOR_KEY = 'Director: '
RATING_KEY = 'Rating: '
BECHDEL_SCORE_KEY = 'Bechdel score: '
IMDB_CAST_KEY = 'IMDB Cast: '
OSCAR_WINNER_KEY = 'Oscar Best Picture Winner: '

import os
from character import Character
from collections import OrderedDict
from movie import Movie

class DataLoader(object):
    """
    Loads metadata and data of movie files into Movie objects.
    """
    def __init__(self, data_path=DATA_PATH, verbose=True):
        print('Initializing DataLoader...')
        self.movies = {}
        data_dir = os.path.join(os.getcwd(), data_path)

        for filename in os.listdir(data_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                    _check_metadata_format(lines, filename)
                    # Get metadata.
                    imdb = _read_field(lines[0])
                    title = _read_field(lines[1])
                    if verbose:
                        print('Loading %s...' % (title) )
                    year = _read_field(lines[2], cast_fn=int)
                    genre = _read_field(lines[3], split=True)
                    director = _read_field(lines[4])
                    rating = _read_field(lines[5], cast_fn=float)
                    bechdel_score = _read_field(lines[6], cast_fn=int)
                    imdb_cast_list = _read_field(lines[7], split=True)
                    imdb_cast = _process_imdb_cast(imdb_cast_list)
                    oscar_winner = _process_oscar_winner(lines[8])
                    characters = _extract_characters(lines[9:])

                # Create movie object and save.
                self.movies[title] = Movie(imdb, title, year,
                                           genre, director, rating,
                                           bechdel_score, imdb_cast,
                                           oscar_winner, characters)
        print('All data loaded!')
        print('----------------------------')

    def get_movie(self, title):
        """
        Get a mutable Movie object with a given title.
        Raises a KeyError if the movie does not exist.
        """
        return self.movies[title]

def _read_field(line, cast_fn = None, split = False):
    """
    Helper function to handle retrieve field value from the text file.
    """
    field = line.split(': ', 1)[1].rstrip() # Read in the field.
    if field == 'None' or field == 'N/A':
        return None
    elif split == True:
        return field.split(', ')
    elif cast_fn:
        return cast_fn(field)
    else:
        return field

def _check_metadata_format(lines, filename):
    """
    Helper function to check format of the metadata in Agarwal.
    """
    # Ensure the metadata order is correct.
    if IMDB_KEY not in lines[0] or \
       TITLE_KEY not in lines[1] or \
       YEAR_KEY not in lines[2] or \
       GENRE_KEY not in lines[3] or \
       DIRECTOR_KEY not in lines[4] or \
       RATING_KEY not in lines[5] or \
       BECHDEL_SCORE_KEY not in lines[6] or \
       IMDB_CAST_KEY not in lines[7]:

       raise Exception(filename +
                       ' metadata formatted incorrectly.')

def _process_imdb_cast(imdb_cast_list):
    """
    Processes IMDB character data from file and makes a dictionary
    mapping from their names to the actor names and gender of the
    actor that portrays them in a tuple.
    If there are two characters with the same name in IMDB, then
    the character key is character (actor last name).
    """
    if imdb_cast_list:
        imdb_cast = OrderedDict()
        dup_character_names = set()
        for entry in imdb_cast_list:
            c = entry.split(' | ')
            char_name = c[0].lower().strip()
            actor_name = c[1].split('(')[0].lower().strip()
            gender = c[1].split('(')[-1].strip(')')
            if char_name in imdb_cast: # first duplicate character
                # Handle the old duplicate
                actor_name = imdb_cast[char_name][0]
                paren_name = char_name + ' (' + actor_name +')'
                __change_key(imdb_cast, char_name, paren_name)
                dup_character_names.add(char_name)
            elif char_name in dup_character_names: # duplicate caught before
                imdb_cast[char_name + ' (' + actor_name + ')'] = (actor_name, gender)
            else:
                imdb_cast[char_name] = (actor_name, gender)
        return imdb_cast
    else:
        return None

def _process_oscar_winner(line):
    """
    Helper function to check whether the Oscar Winner field is
    in this file, and if so, returns whether this movie was a winner
    or not of Oscars Best Picture.
    """
    if OSCAR_WINNER_KEY in line:
        oscar_winner_bool = _read_field(line)
        if oscar_winner_bool == 'True':
            return True
        else:
            return False
    return None

# From stackoverflow: https://bit.ly/2Cznq8R
def __change_key(dict, old, new):
    for _ in range(len(dict)):
        k, v = dict.popitem(False)
        dict[new if old == k else k] = v

def _extract_characters(script):
    """
    Helper function to create Character objects from file. If
    the file has no characters (either we were missing the screenplay
    for this movie or no characters could be found in the screenplay),
    this function returns an empty set.
    """
    characters = {}
    for person in script:
        name_to_lines = person.rstrip().split(': ')
        name = ': '.join(name_to_lines[0:-1])
        line_data = [int(num) for num in name_to_lines[-1].split(', ')]
        characters[name] = Character(name, line_data)
    return characters
