import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import pickle
import os
from pathlib import Path

# --- USER AUTHENTICATION ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Initialize session state for login status if not exists
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Path to save credentials
credentials_path = Path("credentials.pkl")

# Create default users if file doesn't exist
def create_default_users():
    default_users = {
        "admin": make_hashes("admin123"),
        "user": make_hashes("user123")
    }
    with open(credentials_path, 'wb') as file:
        pickle.dump(default_users, file)
    return default_users

# Load or create credentials
def load_credentials():
    if not os.path.exists(credentials_path):
        return create_default_users()
    else:
        with open(credentials_path, 'rb') as file:
            return pickle.load(file)

def save_credentials(credentials):
    with open(credentials_path, 'wb') as file:
        pickle.dump(credentials, file)

# Login widget
def login_widget():
    st.subheader("Login Section")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        credentials = load_credentials()
        hashed_pswd = credentials.get(username)
        
        if hashed_pswd is not None and check_hashes(password, hashed_pswd):
            st.success(f"Logged in as {username}")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()  # Updated from experimental_rerun()
        else:
            st.error("Incorrect username or password")

# Registration widget
def registration_widget():
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    
    if st.button("Sign Up"):
        credentials = load_credentials()
        if new_user in credentials:
            st.error("Username already exists")
        elif new_user == "" or new_password == "":
            st.error("Username and password cannot be empty")
        else:
            credentials[new_user] = make_hashes(new_password)
            save_credentials(credentials)
            st.success("You have successfully created an account")
            st.info("Go to Login to access the map")

# Logout function
def logout():
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()  # Updated from experimental_rerun()

# World map function
def display_world_map():
    st.title("Interactive World Map")
    st.markdown("Hover over countries to see their names")
    
    # Create a sample dataframe with country data
    df = px.data.gapminder().query("year == 2007")
    
    # Create the choropleth map
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        color="continent",
        hover_name="country",
        projection="natural earth",
        title="World Map - Hover to See Country Names",
        height=700,
    )
    
    # Customize the layout
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_showscale=False,
    )
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True)
    
   

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Interactive World Map", layout="wide")
    
    # Sidebar 
    st.sidebar.title("Navigation")
    
    # Show logout in sidebar if logged in
    if st.session_state['logged_in']:
        st.sidebar.text(f"Logged in as {st.session_state['username']}")
        logout()
        display_world_map()
    else:
        # Display menu in sidebar
        menu = ["Login", "Sign Up"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        # Main content based on selection
        if choice == "Login":
            st.title("Welcome to World Map Explorer")
            st.write("Please log in to access the interactive world map.")
            login_widget()
        elif choice == "Sign Up":
            st.title("Create an Account")
            registration_widget()

if __name__ == "__main__":
    main()