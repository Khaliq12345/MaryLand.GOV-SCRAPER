import os
os.system("playwright install chromium")
import streamlit as st
import pandas as pd
import requests
from requests import session
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
from time import sleep
from latest_user_agents import get_random_user_agent

st.set_page_config(
    page_title= 'MaryLand.GOV SCRAPER', 
    page_icon=":smile:"
    layout="wide",
    initial_sidebar_state="expanded"
    )

if 'access' not in st.session_state:
    st.session_state['access'] = False

hide_menu = """
<style>
#MainMenu {
    visibility:hidden;}
footer {
    visibility:hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

def clean_data(df):
    first_name = []
    last_name = []
    middle_name = []
    suffix = []

    for x in df['Name']:
        name = x.split(' ')
        if len(name) == 3:
            first_name.append(name[0])
            middle_name.append(name[1])
            last_name.append(name[2])
            suffix.append(' ')
        elif len(name) == 2:
            first_name.append(name[0])
            last_name.append(name[1])
            middle_name.append(' ')
            suffix.append(' ')
        else:
            first_name.append(name[0])
            middle_name.append(name[1])
            last_name.append(name[2])
            suffix.append(name[3])       

    df['First Name'] = first_name
    df['Middle Name'] = middle_name
    df['Last Name'] = last_name
    df['Suffix'] = suffix
    df.drop(columns=['Name'], inplace=True)

    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='personal_rep.csv',
    mime='text/csv',
    )

def get_data(links):
    item_list = []
    col1, col2 = st.columns(2)
    progress = col1.metric('Rep scraped', 0)
    n = 0
    for link in links:
        n = n + 1
        header = {"User-Agent": get_random_user_agent()}
        response = requests.get(f"{link}")  # headers=header)
        progress.metric('Personal Reps Data scraped', value=n)
        soup = BeautifulSoup(response.text, "lxml")
        address = soup.select_one("#lblPersonalReps small").text
        name = (
            soup.select_one("#lblPersonalReps").text.replace(f"[{address}]", "").strip().title()
        )
        address = soup.select_one("#lblPersonalReps small").text.title()

        items = {"Name": name, "Prsonal Rep Address": address}

        item_list.append(items)
        sleep(2)

    df = pd.DataFrame(item_list)
    col2.metric('Total data scraped', value=len(df))
    clean_data(df)
    
def get_links():
    links = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://registers.maryland.gov/main/search.html", timeout=1000000)
        page.wait_for_load_state("networkidle", timeout=1000000)

        page.get_by_role("button", name="I Agree To The Terms And Conditions").click()
        page.wait_for_load_state("networkidle", timeout=10000000)
        page.locator("#cboCountyId").select_option(f"{selected_county}")
        page.locator("#cboStatus").select_option("OPEN")
        page.locator("#cboType").select_option("RE")
        page.locator("#cboPartyType").select_option("Personal Representative")
        page.locator("#DateOfFilingFrom").click()
        page.locator("#DateOfFilingFrom").fill(f"{date_from}")
        page.locator("#DateOfFilingTo").click()
        page.locator("#DateOfFilingTo").fill(f"{date_to}")
        page.get_by_role("button", name="Search").click()
        page.wait_for_load_state("networkidle", timeout=1000000)

        status = page.query_selector(".status").text_content().strip()
        match = re.search(r"of\s(\d+)", status)
        if match:
            number = match.group(1)

        n = 1
        for i in range(1, int(number) + 1):
            soup = BeautifulSoup(page.content(), "lxml")
            table = soup.select_one("#dgSearchResults")
            rows = table.select("tr")
            for row in rows:
                if "County" not in row.text:
                    try:
                        url = row.select_one("a")["href"]
                        url = "https://registers.maryland.gov/RowNetWeb/Estates/" + url
                        if "javascript" not in url:
                            links.append(url)
                        else:
                            pass
                    except:
                        pass
                else:
                    pass
            n = n + 1
            try:
                page.query_selector(
                    f"#dgSearchResults > tbody > tr.grid-pager > td > a:nth-child({n})"
                ).click()
                page.wait_for_load_state("networkidle", timeout=1000000)
            except:
                pass
        browser.close()
        get_data(links)
if st.session_state['access']:
    st.title('MaryLand.GOV SCRAPER')
    st.caption('Input a valid date. Any change in format in the date can cause an error in this web app')
    date_from = st.text_input('Date Range from', placeholder='12/1/2022')
    date_to = st.text_input('Date Range to', placeholder='01/15/2023')
    counties = [("Allegany", '1'), ("Anne Arundel", '2'), ("Baltimore", '3'), ("Baltimore City", '24'), ("Calvert", '4'), ("Caroline", '5'), ("Carroll", '6'), ("Cecil", '7'),
            ("Charles", '8'), ("Dorchester", '9'), ("Frederick", '10'), ("Garrett", '11'), ("Harford", '12'), ("Howard", '13'), ("Kent", '14'), ("Montgomery", '15'),
            ("Prince George's", '16'), ("Queen Anne's", '17'), ("Somerset", '19'), ("St. Mary's", '18'), ("Talbot", '20'), ("Washington", '21'), ("Wicomico", '22'), ("Worcester", '23')]

    county = st.selectbox("Select an option", counties)
    selected_county = county[1]

    button = st.button('Scrape!')

    if button:
        get_links()
        st.balloons()
        st.success('Done!')
else:
    st.warning('Login to acess the MaryLand.GOV SCRAPER')



