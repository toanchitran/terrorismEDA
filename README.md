# terrorismEDA - Streamlit

## Introduction

This project use the information of more than 180,000 Terrorist Attacks from the Global Terrorism Database (GTD).

## HOW TO RUN


1. Clone the repository:
```
$ git clone git@github.com:upraneelnihar/streamlit-multiapps
$ cd terrorism
```
2. Install dependencies:
```
$ pip install -r requirements.txt
```
4. Download the file terrorism.csv at https://drive.google.com/file/d/1WguiiP5qRVNtC3SwonorFvmBTC3msdlT/view?usp=sharing and add to root folder of terrorism
5. Start the application:
```
streamlit run app.py
```

## STRUCTURE OF PROJECT
1. Main app: **app.py**
2. In app folder:
    * **home.py** for the Home page
    * **country.py** for the Country report
    * **region.py** for the Region report

## HOW TO ADD MORE PAGE TO APP

In case taht you would like to add more page / analysis report to the app, please follow:

1. Write your **new_app.py** and save it to folder `apps/`
```
# apps/new_app.py

import streamlit as st

def app():
    st.title('New App')
```
2. Now, add it to `app.py`
```
from apps import newapp # import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("New App", newapp.app)
```

