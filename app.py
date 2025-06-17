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

# --- Google Analytics Tracking ---
# This code injects the GA tag into the Streamlit app's HTML head.
GA_MEASUREMENT_ID = "G-FW3VK54YNC"  # <-- Your specific ID

ga_script = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
"""
st.components.v1.html(ga_script, height=0)
# --- End of Google Analytics section ---

# --- API Configuration ---
# Pointing to the live API on your DigitalOcean Droplet
API_BASE_URL = 'https://apis.robwiederstein.org/states'

# --- Functions ---

@st.cache_data(ttl=600)  # Cache the data for 10 minutes
def fetch_states_data(filter_query: str = ""):
    """
    Fetches state data from the API. If a filter_query is provided,
    it passes it to the API to get a filtered list.

    Args:
        filter_query (str): The text to filter state names by.

    Returns:
        list | None: A list of state data dictionaries, or None if an error occurs.
    """
    # Construct the base URL
    api_url = f"{API_BASE_URL}/states"
    
    # If the user provided filter text, add it as a query parameter.
    # IMPORTANT: Verify the parameter name (e.g., 'name_contains') matches your API.
    if filter_query:
        api_url += f"?name_contains={filter_query}"
        
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None

# --- Main Application UI ---

# Header
st.title("🇺🇸 U.S. States Data Explorer")
st.markdown("Explore and sort data from the 1970s `state.x77` dataset, served via a live API.")

# --- User Controls in the Sidebar ---
st.sidebar.header("Controls")

# NEW: A text input for live filtering, replacing the old sort dropdown.
filter_text = st.sidebar.text_input(
    "Filter states by name:",
    placeholder="e.g., 'New' or 'Texas'"
)

# --- Data Display ---

# Fetch data based on the user's filter text
# The st.spinner will show while the API call is running.
with st.spinner(f"Searching for states matching '{filter_text}'..." if filter_text else "Fetching all states..."):
    data = fetch_states_data(filter_text)

if data:

    if isinstance(data, dict):
        data = [data]

    df = pd.DataFrame(data)

    # Reorder columns for a cleaner presentation
    desired_column_order = [
        'state_name', 'population', 'income', 'area', 'hs_grad',
        'murder', 'illiteracy', 'life_exp', 'frost'
    ]
    existing_columns_in_order = [col for col in desired_column_order if col in df.columns]
    other_columns = [col for col in df.columns if col not in existing_columns_in_order]
    df_display = df[existing_columns_in_order + other_columns]

    st.success(f"Loaded {len(df_display)} states.")

    # Display the DataFrame. Users can now sort by clicking column headers.
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "state_name": st.column_config.TextColumn("State Name", help="The name of the U.S. state."),
            "population": st.column_config.NumberColumn("Population", help="Estimated population in 1975.", format="%d"),
            "income": st.column_config.NumberColumn("Income", help="Per capita income in 1974.", format="$%d"),
            "illiteracy": st.column_config.NumberColumn("Illiteracy (%)", help="Illiteracy rate in 1970.", format="%.2f%%"),
            "life_exp": st.column_config.NumberColumn("Life Exp. (yrs)", help="Life expectancy in years (1969-71).", format="%.2f"),
            "murder": st.column_config.NumberColumn("Murder Rate", help="Murder rate per 100,000 population in 1976.", format="%.2f"),
            "hs_grad": st.column_config.NumberColumn("HS Grad (%)", help="Percent of high-school graduates in 1970.", format="%.1f%%"),
            "frost": st.column_config.NumberColumn("Frost Days", help="Mean number of days with minimum temperature below freezing.", format="%d"),
            "area": st.column_config.NumberColumn("Area (sq. mi)", help="Land area in square miles.", format="%d")
        }
    )
else:
    st.warning("Could not retrieve data, or no states matched your filter.")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.info(
    "This app is powered by a Python [FastAPI](https://fastapi.tiangolo.com/) backend "
    "and a [PostgreSQL](https://www.postgresql.org/) database, all deployed on "
    "[DigitalOcean](https://www.digitalocean.com/)."
)
# This footer URL is also something you might want to update later
st.sidebar.markdown(
    f"View Live API Docs: [{API_BASE_URL}/docs]({API_BASE_URL}/docs)"
)
