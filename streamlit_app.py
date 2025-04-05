import streamlit as st
import requests
import pandas as pd

# -------------------------
# 🔑 Insert your Google API key
API_KEY = "YOUR_GOOGLE_API_KEY"
# -------------------------

# ----------- Function to get lat/lng for a location
def geocode_location(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": API_KEY}
    res = requests.get(url, params=params)
    if res.status_code == 200:
        data = res.json()
        if data["results"]:
            return data["results"][0]["geometry"]["location"]
    return None

# ----------- Function to search nearby places using lat/lng
def get_places(keyword, location, radius):
    coords = geocode_location(location)
    if not coords:
        st.warning("Could not find coordinates for the location.")
        return []

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{coords['lat']},{coords['lng']}",
        "radius": radius,
        "keyword": keyword,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error("Failed to fetch places.")
        return []

    return response.json().get("results", [])

# ----------- Function to get more details like phone number, website
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,international_phone_number,website,rating",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json().get("result", {})
        return {
            "Name": result.get("name"),
            "Address": result.get("formatted_address"),
            "Phone": result.get("international_phone_number"),
            "Website": result.get("website"),
            "Rating": result.get("rating")
        }
    return {}

# ----------------------
# Streamlit UI
st.set_page_config(page_title="Google Business Lead Generator", layout="centered")

st.title("📍 Google Business Lead Generator")
st.write("Generate business leads by extracting contact details from Google Business Profiles.")

keyword = st.text_input("Enter Business Type or Keywords (e.g., pet salon, cafe, etc.)", "pet salon")
location = st.text_input("Enter Location (e.g., Mumbai, Delhi, etc.)", "Mumbai")
radius = st.slider("Search Radius (in meters)", 500, 50000, 5000)

if st.button("🔍 Search Businesses"):
    with st.spinner("Searching..."):
        results = get_places(keyword, location, radius)
        if not results:
            st.warning("No businesses found.")
        else:
            leads = []
            for r in results:
                details = get_place_details(r["place_id"])
                if details:
                    leads.append(details)
            if leads:
                df = pd.DataFrame(leads)
                st.success(f"Found {len(leads)} businesses!")
                st.dataframe(df)

                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, file_name="business_leads.csv", mime='text/csv')
            else:
                st.warning("No details found for the listed businesses.")
