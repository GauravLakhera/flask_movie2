import pickle
import pandas as pd
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9c746a7a0f8b89e0bb88628dc94bd9b6&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path


def recommend(movie, movies, similarity):
    movie_lower = movie.lower().strip()  # Normalize the incoming movie name

    # Normalize movie titles in the dataset for comparison
    movies['title_lower'] = movies['title'].str.lower().str.strip()

    index = movies[movies['title_lower'] == movie_lower].index
    print("Index for movie:", index)  # Add this line to log the index

    movies.drop('title_lower', axis=1, inplace=True)

    if len(index) > 0:
        index = index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

        recommended_movie_names = []
        recommended_movie_posters = []
        movie_ids = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            movie_ids.append(movie_id)
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)


        return recommended_movie_names, recommended_movie_posters,movie_ids
    else:
        return [], []


# Load data and similarity matrix
movies = pickle.load(open('movie_list2.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_list = pd.DataFrame(movies)


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    movie_name = data.get('movie_name')
    print(f"Received movie name: {movie_name}")

    recommended_movie_names, recommended_movie_posters,movie_ids = recommend(movie_name, movie_list, similarity)

    response = {
        'recommended_movie_names': recommended_movie_names,
        'recommended_movie_posters': recommended_movie_posters,
        'movie_ids': str(movie_ids)
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run()
