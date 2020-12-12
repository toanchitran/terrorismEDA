from pandas.core.dtypes.missing import notna
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from data.import_data import load_terrorism_data

def app():
    
    try:
        st.title(region_option.upper())
    except:
        st.title('ALL REGIONS')

    st.write("Please select your REGION and YEAR of your desire.")
    st.write("If you DO NOT choose, the default dataset is the terrorism data of ALL REGIONS since 2000")

    terrorism_df = load_terrorism_data()

    region = terrorism_df['region'].unique()
    region_option_list = np.insert(region.astype(str), 0, 'All regions')
    
    year = terrorism_df['year'].unique()
    year_option_list = np.insert(year.astype(str), 0, 'All years since 2000')

    working_data = terrorism_df[terrorism_df['year'] >= 2000]

    @st.cache(suppress_st_warning=True)
    def load_terrorism_data_by_region(region_name=None, year=None):
        if region_name == None and year == None:
            return terrorism_df[terrorism_df['year'] >= 2000]
        elif region_name == None and year != None:
            return terrorism_df[terrorism_df['year'] >= year]
        elif region_name != None and year == None:
            return terrorism_df[(terrorism_df['region'] == region_name) & (terrorism_df['year'] >= 2000)]
        else:
            return terrorism_df[(terrorism_df['region'] == region_name) & (terrorism_df['year'] >= year)]


    
    # if st.checkbox('Select specific REGION and YEAR', key='check_box1'):
    which_year = st.selectbox('Choose the year that your want to view:', year_option_list, key='select_box1')
    region_option= st.selectbox('Choose the region that your want to view:', region_option_list, key='select_box2')
    
    if which_year != 'All years since 2000' and region_option != 'All regions':
        year_choice = int(which_year)
        
        st.write('You choose to work with data of ' + region_option + ' since ' + which_year)
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_region(region_name=region_option, year=year_choice)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')
        
    elif which_year == 'All years since 2000' and region_option != 'All regions':
        
        st.write('Terrorism raw data of ' + region_option + ' since 2000')
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_region(region_name=region_option)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')

    elif which_year != 'All years since 2000' and region_option == 'All regions':
        year_choice = int(which_year)
        st.write('Terrorism raw data of ' + region_option + ' since ' + which_year)
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_region(year=year_choice)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')
        
    else:
        st.write('Terrorism raw data of all countries since 2000')
        data_load_state = st.text('Loading data...')
        working_data = terrorism_df[terrorism_df['year'] >= 2000]
        data_load_state.text('Loading data...done!')

    if st.checkbox('Show terrorism data', key='check_box2'):
        st.write('Data', working_data)


    if region_option != 'All regions' and which_year == 'All years since 2000':
        terrorism_stt3 = pd.pivot_table(
            working_data[(working_data['city'] != 'Unknown') & (working_data['region'] == region_option)],
            values=['eventid', 'fatality_num', 'wounded_num'],
            index=['city'],
            aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
        )
        terrorism_stt3.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
        terrorism_stt3 = terrorism_stt3.sort_values(['number_of_attacks'], ascending=False).head(5)
        st.markdown('**TOP 5 TERRORISM HOTSPOT CITIES IN '+region_option.upper()+' SINCE 2000**')
        st.dataframe(terrorism_stt3)

    elif region_option != 'All regions' and which_year != 'All years since 2000':            

        
        terrorism_stt3 = pd.pivot_table(
            working_data[(working_data['city'] != 'Unknown') & (working_data['region'] == region_option)],
            values=['eventid', 'fatality_num', 'wounded_num'],
            index=['city'],
            aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
        )
        terrorism_stt3.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
        terrorism_stt3 = terrorism_stt3.sort_values(['number_of_attacks'], ascending=False).head(5)
        st.markdown('**TOP 5 TERRORISM HOTSPOT CITIES IN '+region_option.upper()+' SINCE ' + which_year +'**')
        st.dataframe(terrorism_stt3)

    elif region_option == 'All regions' and which_year != 'All years since 2000':
        
        for c in working_data['region'].unique():
            terrorism_stt3 = pd.pivot_table(
                working_data[(working_data['city'] != 'Unknown') & (working_data['region'] == c)],
                values=['eventid', 'fatality_num', 'wounded_num'],
                index=['city'],
                aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
            )
            terrorism_stt3.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
            terrorism_stt3 = terrorism_stt3.sort_values(['number_of_attacks'], ascending=False).head(5)

            st.markdown('**TOP 5 TERRORISM HOTSPOT CITIES IN '+c.upper()+' SINCE ' + which_year +'**')
            st.dataframe(terrorism_stt3)
    else:
        working_data = terrorism_df[terrorism_df['year'] >= 2000]

        for c in working_data['region'].unique():
            terrorism_stt3 = pd.pivot_table(
                working_data[(working_data['city'] != 'Unknown') & (working_data['region'] == c)],
                values=['eventid', 'fatality_num', 'wounded_num'],
                index=['city'],
                aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
            )
            terrorism_stt3.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
            terrorism_stt3 = terrorism_stt3.sort_values(['number_of_attacks'], ascending=False).head(5)

            st.markdown('**TOP 5 TERRORISM HOTSPOT CITIES IN '+c.upper()+' SINCE 2000**')
            st.dataframe(terrorism_stt3)