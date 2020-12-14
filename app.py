import streamlit as st
from multiapp import MultiApp
from apps import home, country, region, hostage # import your app modules here
import os

data_path =  os.path.join(os.getcwd(), "data")
app = MultiApp()

# Add all your application here
app.add_app("Human loss and property loss report", home.app)
# app.add_app("Hostage", hostage.app)
app.add_app("Hostage and ransom report", hostage.app)
# app.add_app("Country", country.app)
app.add_app("Country report", country.app)
# app.add_app("Region", region.app)
app.add_app("Region report", region.app)

# The main app
app.run()