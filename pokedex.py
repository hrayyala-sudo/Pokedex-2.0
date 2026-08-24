import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title="Streamlit Pokédex", page_icon="🔴", layout="wide")

# Title and introduction
st.title("🔴 Streamlit Pokédex")
st.write("Browse, search, and view detailed statistics for your favorite Pokémon.")

# Helper function to fetch data from PokéAPI
@st.cache_data(show_spinner=False)
def fetch_pokemon_data(name_or_id):
    try:
        url = f"https://pokeapi.co{str(name_or_id).lower().strip()}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None

# Helper function to get a list of Pokémon for the sidebar selection
@st.cache_data(show_spinner=False)
def get_pokemon_list(limit=151):
    url = f"https://pokeapi.co{limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return [p['name'].title() for p in response.json()['results']]
    return ["Pikachu"]

# Sidebar Navigation
st.sidebar.header("🔍 Search & Filter")
pokemon_list = get_pokemon_list()
selected_pokemon = st.sidebar.selectbox("Choose a Pokémon:", pokemon_list)
search_query = st.sidebar.text_input("Or type name/ID manually:")

# Determine which Pokémon to look up
lookup_target = search_query if search_query else selected_pokemon

if lookup_target:
    with st.spinner(f"Fetching data for {lookup_target}..."):
        data = fetch_pokemon_data(lookup_target)
    
    if data:
        # Main layout columns: Image left, details right
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # High quality official artwork
            image_url = data['sprites']['other']['official-artwork']['front_default']
            if image_url:
                st.image(image_url, use_column_width=True)
            else:
                st.image(data['sprites']['front_default'], use_column_width=True)
                
            # Formatting ID to look like #001
            st.metric(label="Pokédex ID", value=f"#{data['id']:03d}")

        with col2:
            st.header(data['name'].title())
            
            # Types
            types = [t['type']['name'].title() for t in data['types']]
            st.subheader("Type")
            st.write(" | ".join(types))
            
            # Physical Traits
            col_weight, col_height = st.columns(2)
            with col_weight:
                # Convert hectograms to kg
                st.metric(label="Weight", value=f"{data['weight'] / 10} kg")
            with col_height:
                # Convert decimeters to meters
                st.metric(label="Height", value=f"{data['height'] / 10} m")
            
            # Base Stats
            st.subheader("Base Stats")
            stats_dict = {s['stat']['name'].replace('-', ' ').title(): s['base_stat'] for s in data['stats']}
            
            # Display stats as progress bars
            for stat_name, stat_value in stats_dict.items():
                st.write(f"**{stat_name}**: {stat_value}")
                st.progress(min(stat_value / 255.0, 1.0))
                
            # Abilities
            st.subheader("Abilities")
            abilities = [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
            st.write(", ".join(abilities))
    else:
        st.error(f"Could not find Pokémon: '{lookup_target}'. Please check the spelling or ID.")
