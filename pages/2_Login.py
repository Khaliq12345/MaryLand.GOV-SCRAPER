import streamlit as st
from streamlit_extras.colored_header import colored_header

if 'access' not in st.session_state:
    st.session_state['access'] = False

username = st.secrets['username']
pswd = st.secrets['pswd']
    
def login_app():
    st.set_page_config(
        page_title="Login",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    colored_header(
        label='🔑 Login',
        description= 'Welcome back! Please enter your username and password to log in.',
        color_name= 'blue-green-70'
    )
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == f"{username}" and password == f"{pswd}":
            st.success("Logged in as {}".format(username))
            st.session_state['access'] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def access_app():
    st.set_page_config(
        page_title="MaryLand Scraper",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    colored_header(
    label='📊 MARYLAND.GOV Scraper',
    description= 'Get Accurate and Reliable Data from MaryLand.GOV',
    color_name= 'green-70'
    )

    st.success('Welcome! GO to Scraper Page located at the sidebar to run the scraper')

    if st.button('Logout!'):
        st.session_state['access'] = False
        st.experimental_rerun()


if st.session_state['access']:
    access_app()
else:
    login_app()