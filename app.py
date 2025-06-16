import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
# Set the page title and layout. This should be the first Streamlit command.
st.set_page_config(
    page_title="US States Data Explorer",
    page_icon="🇺🇸",
    layout="wide"
)

# --- API Configuration ---
API_BASE_URL = 'https://apis.robwiederstein.org'
# --- Functions ---

@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_states_data(sort_by: str):
    """
    Fetches state data from the API, sorted by the selected column.
    Uses Streamlit's caching to avoid redundant API calls.

    Args:
        sort_by (str): The column name to sort the data by.

    Returns:
        list | None: A list of state data dictionaries, or None if an error occurs.
    """
    api_url = f"{API_BASE_URL}/states?sort_by={sort_by}"
    try:
        response = requests.get(api_url, timeout=30) # Increased timeout to 30s for cold starts
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        st.error(f"Error fetching data from API: {e}")
        return None

# --- Main Application UI ---

# Header
st.title("🇺🇸 U.S. States Data Explorer")
st.markdown("Explore and sort data from the 1970s `state.x77` dataset, served via a live API.")

# --- User Controls in the Sidebar ---
st.sidebar.header("Controls")

# A dictionary to map user-friendly names to the actual column names for the API
sort_options = {
    "Name": "name",
    "Population": "population",
    "Income": "income",
    "Illiteracy (%)": "illiteracy",
    "Life Expectancy (yrs)": "life_exp",
    "Murder Rate": "murder",
    "High-School Graduates (%)": "hs_grad",
    "Days with Frost": "frost",
    "Area (sq. mi)": "area"
}

# Create a dropdown (selectbox) for sorting
selected_option = st.sidebar.selectbox(
    "Sort data by:",
    options=list(sort_options.keys()),
    index=0  # Default to 'Name'
)

# Get the corresponding API column name from the user's selection
sort_by_column = sort_options[selected_option]

# --- Data Display ---

# Fetch data based on user selection
with st.spinner(f"Fetching data sorted by {selected_option}..."):
    data = fetch_states_data(sort_by_column)

if data:
    # Convert the list of dictionaries to a Pandas DataFrame for better display
    df = pd.DataFrame(data)

    # --- FIX for KeyError ---
    # Define the desired column order
    desired_column_order = [
        'name', 'population', 'income', 'area', 'hs_grad',
        'murder', 'illiteracy', 'life_exp', 'frost'
    ]
    
    # Filter the desired order to only include columns that actually exist in the DataFrame.
    # This makes the code robust against missing or differently named columns from the API.
    existing_columns_in_order = [col for col in desired_column_order if col in df.columns]
    
    # Get any other columns that were in the df but not in our desired list
    other_columns = [col for col in df.columns if col not in existing_columns_in_order]

    # Reorder the DataFrame using the new, safe column list
    df = df[existing_columns_in_order + other_columns]
    # --- END FIX ---

    st.success(f"Displaying data sorted by **{selected_option}**.")

    # Display the DataFrame as an interactive table
    st.dataframe(
        df,
        key=f"states_table_{sort_by_column}", # FIX: Add a dynamic key
        use_container_width=True,
        hide_index=True,
        # Configure column display properties
        column_config={
            "name": st.column_config.TextColumn("State Name", help="The name of the U.S. state."),
            "population": st.column_config.NumberColumn("Population", help="Estimated population in 1975.", format="%d"),
            "income": st.column_config.NumberColumn("Income", help="Per capita income in 1974.", format="$%d"),
            "illiteracy": st.column_config.NumberColumn("Illiteracy (%)", help="Illiteracy rate in 1970 (percent of population).", format="%.2f%%"),
            "life_exp": st.column_config.NumberColumn("Life Exp. (yrs)", help="Life expectancy in years (1969-71).", format="%.2f"),
            "murder": st.column_config.NumberColumn("Murder Rate", help="Murder and non-negligent manslaughter rate per 100,000 population in 1976.", format="%.2f"),
            "hs_grad": st.column_config.NumberColumn("HS Grad (%)", help="Percent of high-school graduates in 1970.", format="%.1f%%"),
            "frost": st.column_config.NumberColumn("Frost Days", help="Mean number of days with minimum temperature below freezing (1931-1960) in capital or large city.", format="%d"),
            "area": st.column_config.NumberColumn("Area (sq. mi)", help="Land area in square miles.", format="%d")
        }
    )
else:
    st.warning("Could not retrieve data. The API might be starting up or temporarily unavailable.")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.info(
    "This app is powered by a Python [FastAPI](https://fastapi.tiangolo.com/) backend "
    "and a [PostgreSQL](https://www.postgresql.org/) database, all hosted on a vps at "
    "[DigitalOcean](https://www.digitalocean.com/)."
)
st.sidebar.markdown(
    "View API Docs: [states-api-1fug.onrender.com/docs](https://states-api-1fug.onrender.com/docs)"
)

