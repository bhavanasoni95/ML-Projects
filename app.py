import pickle
import gzip
import streamlit as st
import requests


# Function to fetch movie posters
def fetch_poster(movie_id):
    api_key = "68d7905979cec02596642f46b935d561"  # Your TMDB API key
    default_poster = "https://via.placeholder.com/500x750?text=No+Image+Available"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            print(f"Fetched poster URL: {poster_url}")  # Debugging
            return poster_url
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie_id {movie_id}: {e}")

    print("Returning default poster")  # Debugging
    return default_poster


# Function to recommend movies
def recommend(movie):
    if movie not in movies['title'].values:
        st.error("Selected movie not found in the dataset.")
        return [], []

    # Get the index of the movie
    index = movies[movies['title'] == movie].index[0]

    # Calculate distances
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    # Get top 5 recommendations (excluding the selected movie)
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# Streamlit app header
st.header('Movie Recommender System')

# Load movie data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    with gzip.open('compressed_similarity.pkl.gz', 'rb') as f:
        similarity = pickle.load(f)
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Movie selection dropdown
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Show recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    if not recommended_movie_names:
        st.error("No recommendations available for the selected movie.")
    else:
        # Display recommendations in columns
        cols = st.columns(5)
        for i, col in enumerate(cols):
            if i < len(recommended_movie_names):
                col.text(recommended_movie_names[i])
                col.image(recommended_movie_posters[i], use_container_width=True)  # Updated to use_container_width
