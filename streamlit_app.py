import streamlit as st
import requests
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import pandas as pd
import re
import warnings
from urllib.parse import urlparse

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Lead Generator", layout="centered")
st.title("🔍 Lead Generation Web App")
st.markdown("Enter your business keyword or segment below to search for potential leads using Google Search API.")

# Input
query = st.text_input("🔑 Enter Keyword or Business Segment", placeholder="e.g., pet salons mumbai")

# API keys (secure with Streamlit secrets)
API_KEY = st.secrets["GOOGLE_API_KEY"]
CX = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]

# Utility: Extract email and phone
def extract_contacts(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    phones = set(re.findall(r"\+?\d[\d\s\-()]{7,}\d", text))
    emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
    return list(emails), list(phones)

# Button to trigger search
if st.button("🚀 Search Businesses"):
    if not query.strip():
        st.warning("Please enter a keyword.")
    else:
        with st.spinner("Searching for businesses and extracting contact info..."):
            try:
                service = build("customsearch", "v1", developerKey=API_KEY)
                results = service.cse().list(q=query, cx=CX, num=10).execute()

                lead_data = []

                for item in results.get("items", []):
                    title = item.get("title")
                    link = item.get("link")
                    snippet = item.get("snippet", "")
                    domain = urlparse(link).netloc

                    st.write(f"🔗 Scanning: {link}")
                    try:
                        res = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                        if res.status_code == 200:
                            emails, phones = extract_contacts(res.text)
                            lead_data.append({
                                "Business Name": title,
                                "Website": link,
                                "Domain": domain,
                                "Snippet": snippet,
                                "Email(s)": ", ".join(emails),
                                "Phone(s)": ", ".join(phones)
                            })
                    except:
                        continue

                # Convert to DataFrame
                if lead_data:
                    df = pd.DataFrame(lead_data)
                    st.success(f"Found {len(df)} business leads!")
                    st.dataframe(df)

                    # Downloadable CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Lead Data as CSV",
                        data=csv,
                        file_name="business_leads.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No contacts found from the top results.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
