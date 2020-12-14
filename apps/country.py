
from pandas.core.dtypes.missing import notna
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import altair as alt
from data.import_data import load_terrorism_data

def app():
    
    try:
        st.title(country_option.upper())
    except:
        st.title('ALL COUNTRIES')

    st.write("Please select your COUNTRY and YEAR of your desire.")
    st.write("If you DO NOT choose, the default dataset is the terrorism data of ALL COUNTRIES since 2000")

    terrorism_df = load_terrorism_data()

    country = terrorism_df['country'].unique()
    country_option_list = np.insert(country.astype(str), 0, 'All countries')
    
    year = terrorism_df['year'].unique()
    year_option_list = np.insert(year.astype(str), 0, 'All years since 2000')

    working_data = terrorism_df[terrorism_df['year'] >= 2000]

    @st.cache(suppress_st_warning=True)
    def load_terrorism_data_by_country(country_name=None, year=None):
        if country_name == None and year == None:
            return terrorism_df[terrorism_df['year'] >= 2000]
        elif country_name == None and year != None:
            return terrorism_df[terrorism_df['year'] >= year]
        elif country_name != None and year == None:
            return terrorism_df[(terrorism_df['country'] == country_name) & (terrorism_df['year'] >= 2000)]
        else:
            return terrorism_df[(terrorism_df['country'] == country_name) & (terrorism_df['year'] >= year)]
    

    
    which_year = st.selectbox('Choose the year that your want to view:', year_option_list, key='select_box1')
    country_option= st.selectbox('Choose the country that your want to view:', country_option_list, key='select_box2')
    
    if which_year != 'All years since 2000' and country_option != 'All countries':
        year_choice = int(which_year)
        
        st.write('You choose to work with data of ' + country_option + ' since ' + which_year)
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_country(country_name=country_option, year=year_choice)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')
        
    elif which_year == 'All years since 2000' and country_option != 'All countries':
        
        st.write('Terrorism raw data of ' + country_option + ' since 2000')
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_country(country_name=country_option)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')

    elif which_year != 'All years since 2000' and country_option == 'All countries':
        year_choice = int(which_year)
        st.write('Terrorism raw data of ' + country_option + ' since ' + which_year)
        # Create a text element and let the reader know the data is loading.
        data_load_state = st.text('Loading data...')
        working_data = load_terrorism_data_by_country(year=year_choice)
        # Notify the reader that the data was successfully loaded.
        data_load_state.text('Loading data...done!')
        
    else:
        st.write('Terrorism raw data of all countries since 2000')
        data_load_state = st.text('Loading data...')
        working_data = terrorism_df[terrorism_df['year'] >= 2000]
        data_load_state.text('Loading data...done!')

    if st.checkbox('Show terrorism data', key='check_box2'):
        st.write('Data', working_data)


    st.markdown('## HUMAN LIFE LOSS BY TERRORISM IN ' + country_option.upper())

    # Map of terrorism attack location in country since the desired year to 2017
    @st.cache(suppress_st_warning=True)
    def draw_map(working_df):
        df = working_df[(working_df['latitude'].notnull()) & (working_df['longitude'].notnull()) & (working_df['successful_attack'] > 0)]
        df['text'] = "City : " + df["city"].astype(str) + " <br>"+"Year : " + df['year'].astype(str) +\
                 " <br>" + "Casualties : " + (df["fatality_num"]).astype(str) +\
                 " <br>" + "Wounded : " + (df["wounded_num"]).astype(str) +\
                 " <br>" + "Attack Type : " + df['attack_type'] +\
                 " <br>" + "Target Type : " + df['target_type'] +\
                 " <br>" + "Attacker : " + df['attacker']

        df['fatality_wounded'] = df[['fatality_num', 'wounded_num']].apply(lambda x: x[0].astype(int)+x[1].astype(int) if pd.notna(x[1]) and pd.notna(x[0]) else x[0] if pd.notna(x[0]) else x[1], axis=1)
        fig = go.Figure(data = go.Scattergeo(
            locationmode = 'ISO-3',
            lon = df['longitude'],
            lat = df['latitude'],
            text = df['text'],
            mode = 'markers',
            marker = dict(
                size =8,
                opacity = 0.8,
                reversescale = True,
                symbol = 'square',
                line = dict(
                    width=1,
                    color='rgba(102,102,102)'
                ),
                colorscale='Blues',
                cmin = 0,
                color = df['fatality_wounded'],
                cmax = df['fatality_wounded'].max(),
                colorbar_title = 'Total number of fatality and wounded people'
            ),

        ))
        fig.update_geos(

            projection= dict(
                type='miller',
                scale=8
            ),
            center=dict(
                    lon= df['longitude'].median(),
                    lat= df['latitude'].median()
                )

        )
        fig.update_layout(
            title = 'Terrorism in {country_option} since 2000',
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        return fig

    if which_year != 'All years since 2000':
        st.subheader('TERRORISM ATTACKS LOCATION IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        if st.checkbox('Show map'):
            fig = draw_map(working_df = working_data)
            st.plotly_chart(fig)
    else:
        st.subheader('TERRORISM ATTACKS LOCATION IN ' + country_option.upper() + ' SINCE 2000')

        if st.checkbox('Show map'):
            fig = draw_map(working_df = working_data)
            st.plotly_chart(fig)

    # Number of people dead and wounded by terrorism by year

    if which_year != 'All years since 2000':
        st.subheader('NUMBER OF FATAL AND WOUNDED PEOPLE BY TERRORISM IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        
        dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='year', aggfunc=sum)
        st.markdown('EVERY YEAR, THERE ARE ***'+ str(round(dead_people['fatality_num'].mean())) +'*** people died because of terrorism in ' + country_option.upper())
        st.markdown('Since 2000, there are total of ***' + (dead_people['fatality_num'].sum()).astype(str) + '*** people died and ***' + (dead_people['wounded_num'].sum()).astype(str) + '*** people wounded in ' + country_option + ' because of terrorism.')
        st.markdown('The table below will show the detailed number of dead and wounded people by year since ' + which_year)
        st.markdown('The next part will show the top 5 killing people terrorism.')
        st.dataframe(dead_people)
        if st.checkbox('Show chart', key='dead_wounded1'):
            st.line_chart(dead_people)
    else:
        st.subheader('NUMBER OF FATAL AND WOUNDED PEOPLE BY TERRORISM IN ' + country_option.upper() + ' SINCE 2000')
        dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='year', aggfunc=sum)
        st.markdown('EVERY YEAR, THERE ARE ***'+  str(round(dead_people['fatality_num'].mean()))+'*** people died because of terrorism in ' + country_option.upper())
        st.markdown('Since 2000, there are total of ***' + (dead_people['fatality_num'].sum()).astype(str) + '*** people died and ***' + (dead_people['wounded_num'].sum()).astype(str) + '*** people wounded in ' + country_option + ' because of terrorism.')
        st.markdown('The table below will show the detailed number of dead and wounded people by year since 2000.')
        st.markdown('The next part will show the top 5 killing people terrorism.')
        st.dataframe(dead_people)
        if st.checkbox('Show chart', key='dead_wounded2'):
            st.line_chart(dead_people)

    # Which city have most WOUNDED and DEAD people due to terrorism

    if which_year != 'All years since 2000':
        st.subheader('CITIES THAT HAVE HIGHEST NUMBER OF FATAL AND WOUNDED PEOPLE BY TERRORISM IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        
        city_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='city', aggfunc=sum)
        a7 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a8 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0]
        a9 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['wounded_num'][0]
        b7 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b8 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        b9 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['fatality_num'][0]
        
        st.markdown('Since 2000, the city ***'+ a7 +'*** is the most dangerous city in ' + country_option + '. There are total of ***' + a8.astype(str) + '*** people died and ***' + a9.astype(str) + '*** people wounded in the city because of terrorism.')
        st.markdown('And the city ***'+b7+'*** is the city that have the highest number of wounded people (***'+ b8.astype(str) +'*** wounded people in total, besides ***'+ b9.astype(str) +'*** of dead people)')
        st.markdown('The table below will show the detailed number of dead and wounded people by year since ' + which_year)
    
        st.dataframe(dead_people)
        if st.checkbox('Show chart', key='city_and_dead_wounded1'):
            st.line_chart(dead_people)
    else:
        st.subheader('CITIES THAT HAVE HIGHEST NUMBER OF FATAL AND WOUNDED PEOPLE BY TERRORISM IN ' + country_option.upper() + ' SINCE 2000')
        city_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='city', aggfunc=sum)
        a7 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a8 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0]
        a9 = city_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['wounded_num'][0]
        b7 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b8 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        b9 = city_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['fatality_num'][0]
        
        st.markdown('Since 2000, the city ***'+ a7 +'*** is the most dangerous city in ' + country_option + '. There are total of ***' + a8.astype(str) + '*** people died and ***' + a9.astype(str) + '*** people wounded in the city because of terrorism.')
        st.markdown('And the city ***'+b7+'*** is the city that have the highest number of wounded people (***'+ b8.astype(str) +'*** wounded people in total, besides ***'+ b9.astype(str) +'*** of dead people)')
        st.markdown('The table below will show the detailed number of dead and wounded people by year since 2000')
        st.dataframe(dead_people)
        if st.checkbox('Show chart', key='city_and_dead_wounded2'):
            st.line_chart(dead_people)


    # Which attacker kill most of people

    if which_year != 'All years since 2000':
        st.subheader('ATTACKERS THAT KILL AND INJURE MOST PEOPLE IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        attacker_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='attacker',aggfunc = sum)
        a1 = attacker_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a2 = attacker_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b1 = attacker_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b2 = attacker_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        st.markdown('***'+ a1 + '*** is the top 1 killer. They killed total of ***' + a2.astype(str) + '*** people since ' + which_year)
        st.markdown('***'+ b1 + '*** is the top 1 injuring, dangerous terrorism attacker. They injured total of ***' + b2.astype(str) + '*** people since ' + which_year) 
        st.dataframe(attacker_and_dead_people)
        
        if st.checkbox('Show chart', key='attacker_and_dead_wounded1'):
            fig, ax = plt.subplots()
            attacker_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)
    else:
        st.subheader('ATTACKERS THAT KILL AND INJURE MOST PEOPLE IN ' + country_option.upper() + ' SINCE 2000')
        attacker_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='attacker',aggfunc = sum)
        a1 = attacker_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a2 = attacker_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b1 = attacker_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b2 = attacker_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        st.markdown('***' + a1 + '*** is the top 1 killer. They killed total of ***' + a2.astype(str) + '*** people since 2000')
        st.markdown('***' + b1 + '*** is the top 1 injuring, dangerous terrorism attacker. They injured total of ***'+ b2.astype(str)  + '*** people since 2000') 
        st.dataframe(attacker_and_dead_people)
        if st.checkbox('Show chart', key='attacker_and_dead_wounded2'):
            # fig,ax = plt.subplots()
            attacker_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)

    # Which type of attack kill most of people

    if which_year != 'All years since 2000':
        st.subheader('TYPE OF ATTACK THAT KILL AND INJURE MOST PEOPLE IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        attack_type_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='attack_type',aggfunc = sum)
        a3 = attack_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a4 = attack_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b3 = attack_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b4 = attack_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        st.markdown('***'+a3 + '*** is the top 1 terrorism type killer. They killed total of ***' + a4.astype(str) + '*** people since ' + which_year)
        st.markdown('***'+b3 + '*** is the top 1 terrorism injuring, dangerous terrorism attacker. They injured total of ***' + b4.astype(str) + '*** people since ' + which_year) 
        st.dataframe(attacker_and_dead_people)
        
        if st.checkbox('Show chart', key='attack_type_and_dead_wounded1'):
            fig, ax = plt.subplots()
            attack_type_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)

    else:
        st.subheader('TYPE OF ATTACK THAT KILL AND INJURE MOST PEOPLE IN ' + country_option.upper() + ' SINCE 2000')
        attack_type_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='attack_type',aggfunc = sum)
        attack_type_and_dead_people['total_human_loss'] = attack_type_and_dead_people['fatality_num'] + attack_type_and_dead_people['wounded_num']
        a3 = attack_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a4 = attack_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b3 = attack_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b4 = attack_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        st.markdown('***'+a3 + '*** is the top 1 terrorism type killer. They killed total of ***' + a4.astype(str) + '*** people since 2000')
        st.markdown('***'+b3 + '*** is the top 1 terrorism injuring, dangerous terrorism attacker. They injured total of ***' + b4.astype(str)  + '*** people since 2000') 
        st.dataframe(attacker_and_dead_people)
        if st.checkbox('Show chart', key='attack_type_and_dead_wounded2'):
            fig,ax = plt.subplots()
            attack_type_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)


    # The most KILLED and WOUNDED people

    if which_year != 'All years since 2000':
        st.subheader('TARGET GROUPS THAT GOT MOST FATAL AND WOUNDED IN ' + country_option.upper() + ' SINCE ' + which_year.upper() )
        target_type_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='target_type',aggfunc = sum)
        target_type_and_dead_people['total_human_loss']= target_type_and_dead_people['fatality_num'] + target_type_and_dead_people['wounded_num']
        a5 = target_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a6 = target_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b5 = target_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b6 = target_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        c5 = target_type_and_dead_people.sort_values(['total_human_loss'], ascending=False).head(5).index[0]
        c6 = target_type_and_dead_people.sort_values(['total_human_loss'], ascending=False).head(5)['total_human_loss'][0]
        st.markdown('***'+a5 + '*** is the top 1 targeted and killed group. They was killed total of ***' + a6.astype(str) + '*** people since ' + which_year)
        st.markdown('***'+b5 + '*** is the top 1 targeted and got wound group. They got total of ***' + b6.astype(str) + '*** wounded people since ' + which_year) 
        st.markdown('***'+c5 + '*** is the top 1 targeted group. They got total of ***' + c6.astype(str)  + '*** loss people since '+which_year)
        st.dataframe(target_type_and_dead_people)
        
        if st.checkbox('Show chart', key='target_type_and_dead_wounded1'):
            fig, ax = plt.subplots()
            attack_type_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)
    else:
        st.subheader('TARGET GROUPS THAT GOT MOST FATAL AND WOUNDED IN ' + country_option.upper() + ' SINCE 2000')
        target_type_and_dead_people = pd.pivot_table(working_data, values=['wounded_num', 'fatality_num'], index='target_type',aggfunc = sum)
        target_type_and_dead_people['total_human_loss']= target_type_and_dead_people['fatality_num'] + target_type_and_dead_people['wounded_num']
        a5 = target_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5).index[0] 
        a6 = target_type_and_dead_people.sort_values(['fatality_num'], ascending=False).head(5)['fatality_num'][0] 
        b5 = target_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5).index[0]
        b6 = target_type_and_dead_people.sort_values(['wounded_num'], ascending=False).head(5)['wounded_num'][0]
        c5 = target_type_and_dead_people.sort_values(['total_human_loss'], ascending=False).head(5).index[0]
        c6 = target_type_and_dead_people.sort_values(['total_human_loss'], ascending=False).head(5)['total_human_loss'][0]
        st.markdown('***'+a5 + '*** is the top 1 targeted and killed group. They was killed total of ***' + a6.astype(str) + '*** people since 2000')
        st.markdown('***'+b5 + '*** is the top 1 targeted and got wound group. They got total of ***' + b6.astype(str)  + '*** wounded people since 2000') 
        st.markdown('***'+c5 + '*** is the top 1 targeted group. They got total of ***' + c6.astype(str)  + '*** loss people since 2000') 
        st.dataframe(target_type_and_dead_people)
        if st.checkbox('Show chart', key='target_type_and_dead_wounded2'):
            fig,ax = plt.subplots()
            target_type_and_dead_people.sort_values(['wounded_num', 'fatality_num'], ascending=False).head(5).plot(ax=ax, kind='barh')
            st.pyplot(fig)

    


    