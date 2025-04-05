import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="🔍 Google Business Lead Generator", layout="wide")

st.title("📍 Google Business Lead Generator")
st.markdown("Generate business leads by extracting contact details from Google Business Profiles.")

API_KEY = st.secrets["GOOGLE_API_KEY"]  # Set your API key in Streamlit secrets

# Input form
with st.form("lead_gen_form"):
    keyword = st.text_input("Enter Business Type or Keywords (e.g., pet salon, cafe, etc.)", "pet salon")
    location = st.text_input("Enter Location (e.g., Mumbai, Delhi, etc.)", "Mumbai")
    radius = st.slider("Search Radius (in meters)", 500, 50000, 5000)
    submitted = st.form_submit_button("Search Businesses")

# Function to get place details from Google Places API
def get_places(query, location, radius):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in {location}",
        "radius": radius,
        "key": API_KEY,
    }
    res = requests.get(url, params=params)
    return res.json().get("results", [])

# Function to get details (like phone number) for each place
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,website,url",
        "key": API_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("result", {})

# Search and collect data
if submitted:
    with st.spinner("Searching Google Business Profiles..."):
        results = get_places(keyword, location, radius)
        businesses = []

        for place in results:
            details = get_place_details(place['place_id'])
            businesses.append({
                "Name": details.get("name", ""),
                "Address": details.get("formatted_address", ""),
                "Phone": details.get("formatted_phone_number", ""),
                "Website": details.get("website", ""),
                "Google Maps URL": details.get("url", ""),
            })

        df = pd.DataFrame(businesses)
        if not df.empty:
            st.success(f"Found {len(df)} businesses!")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Lead List as CSV",
                data=csv,
                file_name=f"{keyword}_{location}_leads.csv",
                mime="text/csv"
            )
        else:
            st.warning("No businesses found.")
