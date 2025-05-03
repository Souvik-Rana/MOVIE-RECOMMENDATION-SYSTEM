import streamlit as st
import pickle
import requests
import time
import streamlit.components.v1 as components
import json
import gdown
import os

# --- Function Definitions ---
def fetch_poster(movie_id):
    """Fetches the movie poster from TMDB API, returns None on failure."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    try:
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            # Return None if no poster path is available
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for ID {movie_id}: {e}")
        # Return None on request error
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Invalid JSON response from TMDB API for poster ID {movie_id}.")
        # Return None on JSON error
        return None

def fetch_movie_details(movie_id):
    """Fetches movie details (including rating and overview) from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    try:
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        data = data.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie details for ID {movie_id}: {e}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Invalid JSON response from TMDB API for details ID {movie_id}.")
        return None

@st.cache_data()
def load_movie_data():
    """Downloads and loads movie data and similarity matrix from Google Drive."""
    try:
        # Define Google Drive file IDs
        movie_list_id = "19vr5jCRy3HLAfve1U0A1dAoiIaWDYudl"
        similarity_id = "1hpjPEAhdY52YDfT2qpHRXjzM7X0Lh_sV"

        # Define destination file names
        movie_list_file = "movies_list.pkl"
        similarity_file = "similarity.pkl"

        # Download files if they don't exist
        if not os.path.exists(movie_list_file):
            gdown.download(f"https://drive.google.com/uc?id={movie_list_id}", movie_list_file, quiet=False)

        if not os.path.exists(similarity_file):
            gdown.download(f"https://drive.google.com/uc?id={similarity_id}", similarity_file, quiet=False)

        # Load pickled data
        movies_df = pickle.load(open(movie_list_file, 'rb'))
        similarity_matrix = pickle.load(open(similarity_file, 'rb'))

        return movies_df, similarity_matrix

    except FileNotFoundError:
        st.error("Error: 'movies_list.pkl' or 'similarity.pkl' not found or failed to download.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during loading: {e}")
        st.stop()

movies, similarity = load_movie_data()

if 'title' in movies.columns:
    movies_list = movies['title'].values
else:
    st.error("Error: 'title' column not found in 'movies_list.pkl'.")
    movies_list = []
    st.stop()

# --- Streamlit UI ---
st.title("THE  WATCH  LIST 🎬 ")
st.markdown("*Explore a galaxy of handpicked movies.*", unsafe_allow_html=True)

# --- Custom CSS ---
background_image_url = "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1471&q=80"

st.markdown(
    f"""
    <style>
    /* Apply background image */
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Original CSS rules (mostly unchanged) */
    .big-font {{ /* ... */ }} /* Keeping original rules collapsed for brevity */
    .movie-title {{
        font-size: 1.2rem;
        font-weight: bold;
        /* Reduced margin-bottom */
        margin-bottom: 0.2rem;
        color: #FFF;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
    }}
    .movie-rating {{
        font-size: 1rem;
        color: #FFD700; /* Gold color */
        margin-bottom: 0.5rem;
    }}
    
    .recommendation-container:hover {{ transform: scale(1.03); }}
    .movie-poster {{
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease-in-out;
        width: 100%;
        max-width: 100%;
        height: auto;
        display: block;
        /* Removed margin-bottom to reduce space below poster */
        margin-bottom: 0;
    }}
    .movie-poster:hover {{ transform: scale(1.1); }}

    .overlay {{ /* Original overlay style */
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        color: white; opacity: 0; transition: opacity 0.3s ease-in-out;
        border-radius: 10px; padding: 1rem; text-align: center; box-sizing: border-box;
    }}
    .recommendation-container:hover .overlay {{ opacity: 1; }}

    .image-carousel-container {{ /* ... */ }} /* Original */

    /* --- MODIFIED: Link Button Styling --- */
    .link-button {{
        background-color: transparent; /* Make background transparent */
        color: #FFD700; /* Use gold color for text (matches rating) */
        border: 1px solid #FFD700; /* Add gold border */
        padding: 0.4rem 0.8rem; /* Slightly adjust padding */
        border-radius: 5px;
        margin-top: auto; /* Push button to bottom */
        cursor: pointer;
        transition: background-color 0.3s ease-in-out, color 0.3s ease-in-out, transform 0.2s ease; /* Smooth transitions */
        font-size: 0.9rem;
        font-weight: bold; /* Make text bold */
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }}
    .link-button:hover {{
        background-color: rgba(255, 215, 0, 0.2); /* Light gold background on hover */
        color: #FFFFFF; /* Change text to white on hover */
        border-color: #FFD700; /* Keep border color */
        transform: scale(1.05); /* Slight scale effect on hover */
    }}
    /* --- End of Modified Link Button Styling --- */


    /* Original Media Queries (Adjusted slightly for container) */
    @media screen and (max-width: 768px) {{
        .recommendation-container {{ margin-bottom: 1.5rem; min-height: auto; }} /* Adjust min-height */
        .movie-title {{ font-size: 1rem; }}
        .movie-rating {{ font-size: 0.9rem; }}
        .movie-overview {{ display: none; }} /* Keep hidden on mobile */
        .link-button {{ font-size: 0.8rem; padding: 0.4rem 0.6rem; }}
        .overlay {{ font-size: 0.9rem; }}
    }}
    @media screen and (min-width: 769px) and (max-width: 1024px) {{
        .recommendation-container {{ margin-bottom: 1.5rem; }}
        .movie-title {{ font-size: 1.1rem; }}
        .movie-rating {{ font-size: 0.95rem; }}
        /* Original overview font size for tablets */
        .movie-overview {{ font-size: 0.9rem; }}
    }}
    @media screen and (min-width: 1025px) {{
        .recommendation-container {{ margin-bottom: 2rem; }}
        /* Original overview font size for desktop */
        .movie-overview {{ font-size: 0.9rem; }}
    }}

    /* Added simple scrollbar for overview where visible */
    .movie-overview {{
       font-size: 0.85rem; color: #E0E0E0; line-height: 1.3;
       max-height: 6em; /* Approx 4-5 lines */
       overflow-y: auto; margin-bottom: 1rem; text-align: left; padding: 0 5px; /* Align left */
       /* Simple scrollbar styling for webkit browsers */
        &::-webkit-scrollbar {{ width: 5px; }}
        &::-webkit-scrollbar-track {{ background: rgba(255, 255, 255, 0.1); border-radius: 10px; }}
        &::-webkit-scrollbar-thumb {{ background: #888; border-radius: 10px; }}
        &::-webkit-scrollbar-thumb:hover {{ background: #555; }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# --- Image Carousel ---
# Filter out None values from the fetched posters
valid_image_urls = [url for url in [
    fetch_poster(155), fetch_poster(572154), fetch_poster(299536), fetch_poster(1632),
    fetch_poster(17455), fetch_poster(2830), fetch_poster(429422), fetch_poster(9722),
    fetch_poster(13972), fetch_poster(240), fetch_poster(598), fetch_poster(914),
    fetch_poster(255709)
] if url is not None][:10]

if valid_image_urls:
    try:
        imageCarouselComponent = components.declare_component(
            "image-carousel-component", path="public"
        )
        imageCarouselComponent(imageUrls=valid_image_urls, height=400)
    except Exception as e:
        st.warning(f"Could not load image carousel component: {e}")
else:
    st.info("Could not fetch enough valid posters for the carousel.")


# --- Movie Selection (Original Logic) ---
selectvalue = st.selectbox("Select a movie to get recommendations", movies_list)


# --- Recommendation Logic ---
def recommend(movie):
    try:
        index_list = movies[movies['title'] == movie].index
        if not index_list.empty:
            index = index_list[0]
        else:
            st.error(f"Error: Movie '{movie}' not found.")
            return [], [], [], [], []

        if index < len(similarity):
            distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
        else:
            st.error(f"Error: Index out of bounds for similarity matrix.")
            return [], [], [], [], []

        recommended_movies, recommended_posters, recommended_ratings, recommended_overviews, recommended_movie_ids = [], [], [], [], []
        count = 0
        # Iterate through the recommendations
        for i in distance[1:]:
            if count >= 12: break # Limit to 12 recommendations
            movie_index = i[0]
            if movie_index < len(movies):
                movie_row = movies.iloc[movie_index]
                if 'id' in movie_row and 'title' in movie_row:
                    movie_id, movie_title = movie_row.id, movie_row.title
                    if movie_title == movie: continue # Skip the input movie itself

                    # --- NEW: Fetch poster and details, and only append if poster is available ---
                    poster_url = fetch_poster(movie_id)

                    if poster_url is not None: # Check if poster was fetched successfully
                        movie_details = fetch_movie_details(movie_id)
                        rating, overview = 'N/A', 'No overview available.'
                        if movie_details:
                            raw_rating = movie_details.get('vote_average')
                            rating = f"{raw_rating:.1f}" if isinstance(raw_rating, (int, float)) and raw_rating > 0 else "N/A"
                            overview = movie_details.get('overview', '') or 'No overview available.'

                        recommended_movies.append(movie_title)
                        recommended_posters.append(poster_url)
                        recommended_ratings.append(rating)
                        recommended_overviews.append(overview)
                        recommended_movie_ids.append(movie_id)
                        count += 1 # Only increment count if a valid recommendation was added
                    # --- END NEW ---
                else: st.warning(f"Skipping: Missing 'id' or 'title' at index {movie_index}.")
            else: st.warning(f"Skipping: Index {movie_index} out of bounds.")
        return recommended_movies, recommended_posters, recommended_ratings, recommended_overviews, recommended_movie_ids
    except IndexError:
        st.error(f"Error: Movie '{movie}' index issue.")
        return [], [], [], [], []
    except Exception as e:
        st.error(f"Unexpected error during recommendation: {e}")
        import traceback
        st.error(traceback.format_exc())
        return [], [], [], [], []


# --- Display Recommendations ---
if st.button("Show Recommendations"):
    with st.spinner("Fetching recommendations..."):
        time.sleep(1)
        # The recommend function now only returns movies with fetched posters
        recommended_movie_names, recommended_movie_posters, recommended_movie_ratings, recommended_movie_overviews, recommended_movie_ids = recommend(selectvalue)

    if recommended_movie_names:
        st.markdown("---")
        st.markdown("### Recommended Movies")

        # Display in columns
        num_recommendations = len(recommended_movie_names)
        # Ensure we have enough columns for the number of recommendations
        if num_recommendations > 0:
            # Calculate number of columns needed, up to a maximum of 4
            num_cols_to_display = min(num_recommendations, 4)
            cols = st.columns(num_cols_to_display)

            for i in range(num_recommendations):
                 # Use modulo to cycle through the available columns
                with cols[i % num_cols_to_display]:
                    # Main container div for card styling
                    st.markdown('<div class="recommendation-container">', unsafe_allow_html=True)

                    # Content div to help with flex layout if needed
                    st.markdown('<div>', unsafe_allow_html=True)
                    # We are guaranteed to have a valid poster_url here
                    st.image(recommended_movie_posters[i], use_container_width=True, output_format='auto')
                    st.markdown(f'<div class="movie-title">{recommended_movie_names[i]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="movie-rating">⭐ {recommended_movie_ratings[i]}</div>', unsafe_allow_html=True)
                    # Overview - visible on larger screens, scrollable
                    st.markdown(f'<div class="movie-overview">{recommended_movie_overviews[i]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True) # Close content div

                    # Link Button div (placed after content div for bottom alignment)
                    tmdb_url = f"https://www.themoviedb.org/movie/{recommended_movie_ids[i]}"
                    st.markdown(f'<div><a href="{tmdb_url}" target="_blank" class="link-button">View on TMDB</a></div>', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True) # Close recommendation-container div
        else:
             # This case should ideally be covered by the outer if recommended_movie_names: check
             st.info("No recommendations with available posters found for this movie.")


    elif selectvalue:
        # This else block is for when the button is pressed but no recommendations were found at all
        st.info("No recommendations found for this movie.")


# --- Footer (Original) ---
st.markdown("---")
st.markdown("*Made by Souvik Rana*", unsafe_allow_html=True)