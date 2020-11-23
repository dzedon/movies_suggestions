import requests, json
from PIL import Image


def get_movies_from_tastedive(movie_name):

    url = 'https://tastedive.com/api/similar'
    param_dict = {"q": movie_name, "type": "movies", "limit": 9}
    response = requests.get(url, params=param_dict)
    json_file = response.json()
    suggestions =  [y['Name'] for y in json_file['Similar']['Results']]

    return suggestions


def get_related_titles(movie_lst):

    multiple_movies  = { y for movie in movie_lst for y in get_movies_from_tastedive(movie) }
    return multiple_movies


def get_movie_data(movie_title):
    url = 'http://www.omdbapi.com/?apikey=995e507c&'
    param_dict = {"t": movie_title, "r": "json"}
    response = requests.get(url, params=param_dict)

    return response.json()


def get_movie_rating(json_file):
    ratings = json_file['Ratings']
    for rating in ratings:
        if rating['Source'] == 'Rotten Tomatoes':
            user_rating = int(rating['Value'].rstrip("%"))
            return user_rating
        else:
            user_rating = 0

    return user_rating


def fix_title(path):
    words = ""
    for char in path:
        if char.isalnum():
            words = words + str(char)
        elif char == " ":
            words = words + " "

    return " ".join(words.split())


def get_movie_poster(movie):
    movie_poster = get_movie_data(movie)
    response = requests.get(movie_poster['Poster'])
    title = fix_title(movie_poster['Title'])
    img_path = f"img/{title}"
    with open(img_path, "wb") as file:
        file.write(response.content)

    return img_path


def make_poster(posters):

    all_pictures = [Image.open(f"{poster}").convert('RGB') for poster in posters]

    img_w, img_h = 300, 444

    canvas = Image.new('RGB', (img_w*3, img_h*3))

    x = 0
    y = 0

    for item in all_pictures:
        canvas.paste(item, (x,y))
        if x + item.width == canvas.width:
            x = 0
            y = int(y + item.height)
        else:
            x = int(x + item.width)

    canvas = canvas.resize((int(canvas.width/2), int(canvas.height/2)))

    canvas.save("img/movie_recomendations.jpg")

    return canvas


def get_sorted_recommendations(movie_lst):
    movie_recomendations = get_related_titles(movie_lst)

    movies_posters = [get_movie_poster(movie) for movie in movie_recomendations]

    # uncomment to get the list of movies order by rating
    # movie_and_ratings= {movie: get_movie_rating(get_movie_data(movie)) for movie in movie_recomendations}
    # sorted_movies = [x for x in sorted(movie_and_ratings.keys(), key=lambda k: (movie_and_ratings[k], k), reverse=True)]

    suggestions_poster = make_poster(movies_posters)

    return suggestions_poster



user_input = "Batman Begins"

movies = get_sorted_recommendations([user_input])

movies.show()
