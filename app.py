import streamlit as st
from multiapp import MultiApp
from apps import home, country, region # import your app modules here
import os

data_path =  os.path.join(os.getcwd(), "data")
app = MultiApp()

# Add all your application here
app.add_app("Home", home.home)
# app.add_app("Country", country.app)
app.add_app("Country", country.app)
# app.add_app("Region", region.app)
app.add_app("Region", region.app)
# The main app
app.run()