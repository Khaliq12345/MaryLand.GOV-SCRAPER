import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
from time import sleep
from latest_user_agents import get_random_user_agent

def clean_data(df):
    first_name = []
    last_name = []
    middle_name = []
    suffix = []
    street_address = []
    city = []
    state = []
    zip_code = []

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
    df.drop(columns=['Name'])

    street_address = []
    city = []
    state = []
    zip_code = []
    for y in df['Address']:
        address = y.split(',')
        street_address.append(address[0])
        city.append(address[1])
        state_zip = address[2]
        zip_code.append(state_zip[3:])
        state.append(state_zip.replace(state_zip[3:], ''))
        

    df['Street Address'] = street_address
    df['City'] = city
    df['State'] = state
    df['Zip Code'] = zip_code
    df.drop(columns=['Address'], inplace=True)

    df.to_csv('maryland_gov.csv', index=False)

    return df


def get_data(links):
    item_list = []
    n = 0
    for link in links:
        n = n + 1
        header = {"User-Agent": get_random_user_agent()}
        response = requests.get(f"{link}")  # headers=header)
        print(f"Link {n}")
        soup = BeautifulSoup(response.text, "lxml")
        address = soup.select_one("#lblPersonalReps small").text
        name = (
            soup.select_one("#lblPersonalReps").text.replace(f"[{address}]", "").strip().title()
        )
        address = soup.select_one("#lblPersonalReps small").text.title()

        items = {"Name": name, "Address": address}

        item_list.append(items)
        sleep(2)

    df = pd.DataFrame(item_list)
    clean_data(df)



def get_links():
    links = []
    date_from = input('Date from: ')
    date_to = input('Date to: ')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://registers.maryland.gov/main/search.html", timeout=1000000)

        page.wait_for_load_state("networkidle", timeout=1000000)

        page.get_by_role("button", name="I Agree To The Terms And Conditions").click()
        page.wait_for_load_state("networkidle", timeout=10000000)
        page.locator("#cboCountyId").select_option("2")
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
            print(f"Page {n}")
            soup = BeautifulSoup(page.content(), "lxml")
            print("good")
            table = soup.select_one("#dgSearchResults")
            rows = table.select("tr")
            for row in rows:
                if "County" not in row.text:
                    url = row.select_one("a")["href"]
                    url = "https://registers.maryland.gov/RowNetWeb/Estates/" + url
                    if "javascript" not in url:
                        links.append(url)
                    else:
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


get_links()
