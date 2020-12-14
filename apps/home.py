import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit.proto.Checkbox_pb2 import Checkbox
from data.import_data import load_terrorism_data
import seaborn as sns


def app():
    st.title("TERRORISM RISK ACCESSMENT FOR BUSINESS")
    
    # Create a text element and let the reader know the data is loading.
    data_load_state = st.text('Loading data...')

    terrorism_df = load_terrorism_data()

    # Notify the reader that the data was successfully loaded.
    data_load_state.text('Loading data...done!')

    notRegion = ['South Asia', 'Middle East & North Africa', 'Sub-Saharan Africa']
    notRegion_df = terrorism_df[terrorism_df['region'].isin(notRegion)].groupby('region').apply(pd.DataFrame)[['region','country']].drop_duplicates().set_index('region').sort_index()

    st.markdown('COUNTRIES AND REGIONS BELOW ARE NOT INCLUDED IN THIS ACCESSMENT SUMMARY REPORT. PLEASE REFER IT IN THE PAGE "REGION" AND "COUNTRY" IF NEEDED.')
    st.dataframe(notRegion_df)
    working_data = terrorism_df[~terrorism_df['region'].isin(notRegion)]
    working_data['property_damage_USD'] = working_data['property_damage_USD'].abs()
    if st.checkbox('Include of the regions and countries to the report:', key='all_data'):
        terrorism_df = load_terrorism_data()
        working_data = terrorism_df
    if st.checkbox('Show working data sample:', key='check_box1'):
        st.write('Data')
        st.dataframe(working_data.sample(10))
    st.markdown('## SCOPE OF WORK')
    st.markdown('This accessment report is focused to business operators and insurance companies. In this report, we will focus on those quantity number of loss by terrorism in term of human loss (wounded and fatality number),'+
    ' property/asset loss (number of damaged properties and the damaged value in USD) and after all, the information about the terrorism related to kidnapping/ taking hostage and try to answer the question of how much ransom we need to pay to keep the hostage survive')
    
    ####################################
    #     TERRORISM OVER THE WORLD     #
    ####################################

    st.markdown('## TERRORISM OVER THE WORLD')

    st.markdown('### NUMBER OF TERRORISM ATTACKS IN THE WORLD SINCE 1970 BY REGIONS')

    terrorism_status = working_data.groupby(['year', 'region'], as_index=False).size()
    terrorism_status.columns = ['year', 'region', 'number_of_attack']
    st.dataframe(terrorism_status)
    if st.checkbox('Show chart', key='terrorism_stt1'):
        st.bar_chart(terrorism_status.groupby('region')['number_of_attack'].sum().drop(columns='year'), height=600)

        df = working_data[['region', 'year', 'country', 'attack_type', 'eventid']]
        df=df.groupby(['region', 'year', 'country', 'attack_type'], as_index=False)['eventid'].count()
        df.rename(columns={'eventid':'number_of_incidents'}, inplace=True)
        df = df[df['year'] >= 2000]
        fig = px.sunburst(df,
                        path=['region','year','country','attack_type'],
                        values='number_of_incidents',
                        color_continuous_scale = 'viridis',
                        height = 650,
                        maxdepth=2)
        fig.update_layout(
            title= 'Number of Terrorism Attack by Countries and Regions Since 2000',
            title_x = 0.5 )
        st.plotly_chart(fig)

    st.markdown('### HOW TERRORISM STATUS IN THE WORLD SINCE 2000 TO 2017')
    fig,ax = plt.subplots()
    terrorism_stt = pd.pivot_table(
        working_data[working_data['year']>=2000],
        values=['eventid', 'fatality_num', 'wounded_num'],
        index='year',
        aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
    )
    terrorism_stt.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
    st.dataframe(terrorism_stt)
  
    top_dead_number = terrorism_stt.sort_values('fatality_num', ascending=False).head(1)['fatality_num'].values[0]
    top_wounded_number = terrorism_stt.sort_values('wounded_num', ascending=False).head(1)['wounded_num'].values[0]
    top_attack_year = terrorism_stt.sort_values(['number_of_attacks'], ascending=False).index[0]
    top_attack_number = terrorism_stt.sort_values(['number_of_attacks'], ascending=False).head(1)['number_of_attacks'].values[0]
    st.markdown('Terrorism over the world reachs the highest number of attack at ***'+ top_attack_number.astype(str)+'***, highest number of fatality at ***'+(top_dead_number.astype(int)).astype(str)+'*** and highest number of wounded people at ***'+(top_wounded_number.astype(int)).astype(str)+'*** in **'+str(top_attack_year)+'**.')
    st.markdown('After 2014, the terrorism over the world step down in number of attacks, fatality and wounded people.')
    if st.checkbox('Show chart', key='terrorism_stt2'):
        working_data[working_data['year'] >= 2000].groupby('year')['eventid'].count().plot(ax=ax, xticks=[2000,2005,2010,2015] ,label="Number of attacks", legend=True, grid=True)
        working_data[working_data['year'] >= 2000].groupby('year')['fatality_num'].sum().plot(ax=ax, xticks=[2000,2005,2010,2015], label="Fatality", legend=True, grid=True)
        working_data[working_data['year'] >= 2000].groupby('year')['wounded_num'].sum().plot(ax=ax, xticks=[2000,2005,2010,2015], label="Wounded", legend=True, grid=True)
        st.pyplot(fig)

    # Terrorism hotspots since 2014
    st.markdown('### TERRORISM HOTSPOT SINCE 2014')

    # PREPARE DATAFRAME
    terrorism_stt1 = working_data[working_data['year'] >= 2014]
    terrorism_stt1 = terrorism_stt1[['city', 'country', 'region', 'eventid', 'fatality_num', 'wounded_num']]
    terrorism_stt2 = pd.pivot_table(
        terrorism_stt1,
        values=['eventid', 'fatality_num', 'wounded_num'],
        index=['country'],
        aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
    )
    terrorism_stt2.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
    top5_terrorism_attack_country = terrorism_stt2.sort_values(['number_of_attacks'], ascending=False).head(5)
    top5_safe_terrorism_attack_country = terrorism_stt2[terrorism_stt2['number_of_attacks'] == 1]
    
    # top 5 terrorrism hotspot countries over the world in term of number of attacks
    terrorism_stt4 = pd.pivot_table(
        terrorism_stt1[(terrorism_stt1['country'].isin(top5_terrorism_attack_country.index)) & (terrorism_stt1['city'] != 'Unknown')],
        values=['eventid', 'fatality_num', 'wounded_num'],
        index=['country','city'],
        aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
    ).reset_index()
    terrorism_stt4.columns = ['country','city','number_of_attacks', 'fatality_num', 'wounded_num']
    terrorism_stt4 = terrorism_stt4.sort_values(['country','number_of_attacks', 'fatality_num', 'wounded_num'], ascending=False)
    terrorism_stt4 = terrorism_stt4.loc[terrorism_stt4.groupby('country')['number_of_attacks'].nlargest(5).reset_index()['level_1']]

    # top 5 terrorism hotspot countries over the world in term of human loss (total of fatality and wounded people)
    terrorism_stt5 = pd.pivot_table(
        terrorism_stt1,
        values=['eventid', 'fatality_num', 'wounded_num'],
        index=['country'],
        aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
    )
    terrorism_stt5.columns = ['number_of_attacks', 'fatality_num', 'wounded_num']
    terrorism_stt5['total_human_loss'] = terrorism_stt5['fatality_num'] + terrorism_stt5['wounded_num']
    terrorism_stt5 = terrorism_stt5[['total_human_loss', 'number_of_attacks', 'fatality_num', 'wounded_num']]
    top5_human_loss_country = terrorism_stt5.sort_values(['total_human_loss'], ascending=False).head(5)
    top5_safe_human_loss_country = terrorism_stt5[terrorism_stt5['total_human_loss'] == 0]
    
    # top 5 terrorism hotspot cities in top 5 countries over the world in term of human loss (total of fatality and wounded people)
    terrorism_stt6 = pd.pivot_table(
        terrorism_stt1[(terrorism_stt1['country'].isin(top5_human_loss_country.index)) & (terrorism_stt1['city'] != 'Unknown')],
        values=['eventid', 'fatality_num', 'wounded_num'],
        index=['country', 'city'],
        aggfunc={'eventid':'count', 'fatality_num':sum, 'wounded_num':sum}
    ).reset_index()
    terrorism_stt6.columns = ['country', 'city','number_of_attacks', 'fatality_num', 'wounded_num']
    terrorism_stt6['total_human_loss'] = terrorism_stt6['fatality_num'] + terrorism_stt6['wounded_num']
    terrorism_stt6 = terrorism_stt6.sort_values(['country', 'total_human_loss'], ascending=False)
    terrorism_stt6 = terrorism_stt6.loc[terrorism_stt6.groupby('country')['total_human_loss'].nlargest(5).reset_index()['level_1']]

  


    # DISPLAY DATAFRAME 
    st.markdown('**TERRORISM HOTSPOT COUNTRIES OVER THE WORLD IN TERM OF NUMBER OF ATTACKS SINCE 2014**')
 


    fig = px.choropleth(terrorism_stt2.reset_index(),
                    hover_data=['country', 'number_of_attacks', 'fatality_num', 'wounded_num'],
                    locations = 'country',
                    locationmode = "country names",
                    projection="natural earth",
                    color='number_of_attacks',
                    color_continuous_scale = px.colors.diverging.balance,
                    color_continuous_midpoint=terrorism_stt2['number_of_attacks'].mean())
    fig.update_layout(
        title= "Terrorism hotspot countries over the world in term of attacks since 2014",
        title_x = 0.5 )
    st.plotly_chart(fig)

    st.dataframe(top5_terrorism_attack_country)
    if st.checkbox('Show top 5 hotspot cities in top 5 countries above', key='hotspot_1'):
        st.markdown('** Top 5 hotspot cities in top 5 hotspot countries**')
        st.dataframe(terrorism_stt4)

        if st.checkbox('Show chart', key='property_damage2'):
                
            fig = px.sunburst(terrorism_stt4,
                            path=['country', 'city'],
                            values='number_of_attacks',
                            color_continuous_scale = 'viridis',
                            maxdepth=2)
            fig.update_layout(
                title= 'Number of Terrorism Attack by Top 5 Countries and Cities Since 2014',
                title_x = 0.5 )
            st.plotly_chart(fig, use_container_width=True)

                
            fig = px.sunburst(terrorism_stt4,
                            path=['country', 'city'],
                            values='fatality_num',
                            color_continuous_scale = 'viridis',
                            maxdepth=2)
            fig.update_layout(
                title= 'Number of Fatality Numbers by Top 5 Countries and Cities Since 2014',
                title_x = 0.5 )
            st.plotly_chart(fig, use_container_width=True)

                
            fig = px.sunburst(terrorism_stt4,
                            path=['country', 'city'],
                            values='wounded_num',
                            color_continuous_scale = 'viridis',
                            maxdepth=2)
            fig.update_layout(
                title= 'Number of Wounded Numbers by Top 5 Countries and Cities Since 2014',
                title_x = 0.5,
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('**TOP 5 SAFEST COUNTRIES OVER THE WORLD IN TERM OF NUMBER OF ATTACKS SINCE 2014**')
    st.markdown('Countries from the list below have only 1 terrorism attack since 2014 and are quite safe from terrorism')
    st.dataframe(top5_safe_terrorism_attack_country)

    # display top 5 terrorism hotspot countries over the world in term of human loss (total of fatality and wounded people)
    st.markdown('**TERRORISM HOTSPOT COUNTRIES OVER THE WORLD IN TERM OF HUMAN LOSS**')

    fig = px.choropleth(terrorism_stt5.reset_index(),
                    hover_data=['country', 'total_human_loss', 'fatality_num', 'wounded_num'],
                    locations = 'country',
                    locationmode = "country names",
                    projection="natural earth",
                    color='total_human_loss',
                    color_continuous_scale = px.colors.diverging.balance,
                    color_continuous_midpoint=terrorism_stt5['total_human_loss'].mean())
    fig.update_layout(
        title= "Terrorism hotspot countries over the world in term of total human loss since 2014",
        title_x = 0.5 )
    st.plotly_chart(fig)

    st.markdown('The table below show the top 5 hotspot countries in the world in term of ***human loss (total number of fatality and wounded people)*** ')
    st.dataframe(top5_human_loss_country)
    if st.checkbox('Show top 5 hotspot cities in top 5 countries above', key='hotspot_2'):
        st.markdown('** Top 5 hotspot cities in top 5 hotspot countries**')
        st.dataframe(terrorism_stt6)

    #display top 5 countries that have least human loss in term of human loss since 2014
    st.markdown('**TOP 5 SAFEST COUNTRIES IN TERM OF HUMAN LOSS BY TERRORISM SINCE 2014**')
    st.markdown('Countries from table below are safe countries in term of human loss since 2014 even though some countries have many terrorisms incident. ')
    st.dataframe(top5_safe_human_loss_country)


    #####################################
    #          PROPERTY DAMAGE          #
    #####################################


    st.markdown('## PROPERTY DAMAGE BY TERRORISM')

    ## PREPARE DATA

    # property damage since 2000
    property_damage = working_data[working_data['property_damage'] != -9]
    property_damage = property_damage[property_damage['year'] >= 2000]
    property_damage['property_damage_USD'] = property_damage['property_damage_USD'].abs()

    # create the general dataframe to property damage, property damged in USD over the number of attacks in regions
    
    property_damage_stt = pd.pivot_table(property_damage, values=['property_damage', 'eventid', 'property_damage_USD'], index='attack_type', aggfunc={'property_damage':'sum', 'eventid':'count', 'property_damage_USD':'sum'})
    property_damage_stt = property_damage_stt.rename(columns={'eventid':'number_of_attacks'})
    property_damage_stt['avg_property_damage_USD'] = property_damage_stt['property_damage_USD'] / property_damage_stt['property_damage']
    property_damage_stt = property_damage_stt.sort_values(['property_damage', 'property_damage_USD'], ascending=[False, False])

    # dataframe of top 3 attack type damage in USD by region 
    top3_attack = ['Bombing/Explosion','Facility/Infrastructure Attack','Armed Assault']
    property_damage_stt1 = pd.pivot_table(property_damage[property_damage['attack_type'].isin(top3_attack)],
                                        values=['property_damage_USD'],
                                        index=['region', 'attack_type'],
                                        aggfunc=sum
    )

    # number of property damage terrorism over the year by year
    number_property_damage = pd.pivot_table(
        property_damage,
        values= ['eventid', 'property_damage', 'property_damage_USD'],
        index='year',
        aggfunc={'eventid':'count', 'property_damage':sum, 'property_damage_USD':sum}
    )
    number_property_damage.columns = ['number_of_attacks', 'property_damage', 'property_damage_USD']
    
    number_of_terrorism_attack = number_property_damage['number_of_attacks']
    property_damage_attack = number_property_damage['property_damage']
    property_damage_in_usd = number_property_damage['property_damage_USD']/10000

    max_property_damage_in_usd = number_property_damage['property_damage_USD'].max()
    min_property_damage_in_usd = number_property_damage['property_damage_USD'].min()

    # dataframe of top 1 damaged property attack type in USD by country
    property_damage_stt3 = pd.pivot_table(
        property_damage,
        values='property_damage_USD',
        index=['country','attack_type'],
        aggfunc=sum
    ).reset_index()
    property_damage_stt3_top1_attack = property_damage_stt3.loc[property_damage_stt3.groupby(['country'])['property_damage_USD'].nlargest(1).reset_index()['level_1']]

    #number of property damage attack and loss of property damage attack by country
    property_damage_stt2= pd.pivot_table(
        property_damage,
        values= ['property_damage', 'property_damage_USD'],
        index='country',
        aggfunc={'property_damage':sum, 'property_damage_USD':sum}
    )
    top5_property_damaged_country = property_damage_stt2.sort_values(['property_damage'], ascending=False).head(5)
    top5_property_damaged_country_USD = property_damage_stt2.sort_values(['property_damage_USD'], ascending=False).head(5)
    
    # top 5 terrorrism hotspot countries over the world in term of number of property damage attack
    property_damage_stt4 = pd.pivot_table(
        property_damage[(property_damage['country'].isin(top5_property_damaged_country.index)) & (property_damage['city'] != 'Unknown')],
        values=['property_damage', 'property_damage_USD'],
        index=['country','city'],
        aggfunc={'property_damage':sum, 'property_damage_USD':sum}
    ).reset_index()
    property_damage_stt4 = property_damage_stt4.sort_values(['country','property_damage', 'property_damage_USD'], ascending=False)
    property_damage_stt4 = property_damage_stt4.loc[property_damage_stt4.groupby('country')['property_damage'].nlargest(5).reset_index()['level_1']]

    # top 5 terrorism hotspot countries over the world in term of value of damaged property
    property_damage_stt5 = pd.pivot_table(
        property_damage[(property_damage['country'].isin(top5_property_damaged_country_USD.index)) & (property_damage['city'] != 'Unknown')],
        values=['property_damage', 'property_damage_USD'],
        index=['country', 'city'],
        aggfunc={'property_damage':sum, 'property_damage_USD':sum}
    ).reset_index()
    property_damage_stt5 = property_damage_stt5.sort_values(['country','property_damage_USD', 'property_damage'], ascending=False)
    property_damage_stt5 = property_damage_stt5.loc[property_damage_stt5.groupby('country')['property_damage_USD'].nlargest(5).reset_index()['level_1']]

    #the rising of facility attack
    facility_attack_df = pd.pivot_table(
        property_damage[property_damage['attack_type'].isin(['Bombing/Explosion', 'Facility/Infrastructure Attack'])],
        values=['property_damage','property_damage_USD'],
        index=['year', 'attack_type'],
        aggfunc=sum
    )
 


    ## DISPLAY DATA AND CHART
    st.markdown('**PROPERTY DAMAGE ATTACK STATUS SINCE 2000**')
    st.markdown('Every year, the world loss from ***' + '%.2f'%min_property_damage_in_usd +'*** to ***'+ '%.2f'%max_property_damage_in_usd +'*** USD because of terrorism attacks.')
    st.markdown('In 2014, both the number of property damage attack and the value of damaged property reach the highest points.')
    st.dataframe(number_property_damage)
    if st.checkbox('Show chart', key='property_damage3'):
        
        fig, ax = plt.subplots()
        temp_df = pd.DataFrame({'number of attack':number_of_terrorism_attack, 'number of property damage attack':property_damage_attack, 'total value of damaged property in 10000 USD':property_damage_in_usd})
        temp_df.plot.barh(ax=ax)
        st.pyplot(fig)
       
    st.markdown('**TYPE OF ATTACK THAT CAUSE THE MOST PROPERTY DAMAGE**')
    st.dataframe(property_damage_stt)
    if st.checkbox('Show chart', key='property_damage_1'):
        col1, col2 = st.beta_columns(2)
        with col1:
            fig, ax = plt.subplots()
            property_damage_stt['property_damage'].plot(ax=ax, label='number of property damaged', legend=True)
            property_damage_stt['number_of_attacks'].plot.bar(ax=ax, label='number of attacks', legend=True)
            ax.set_title('Terrorism attacks vs. Number of property damage since 2000')
            st.pyplot(fig)


        with col2:
            fig, ax = plt.subplots()
            number_of_terrorism_attack = property_damage_stt['number_of_attacks']
            property_damage_attack = property_damage_stt['property_damage']
            property_damage_in_usd = property_damage_stt['property_damage_USD']/10000
            temp_df = pd.DataFrame({'number of attack':number_of_terrorism_attack, 'number of property damage attack':property_damage_attack, 'total value of damaged property in 10000 USD':property_damage_in_usd})
            temp_df.plot.barh(ax=ax)
            st.pyplot(fig)

    #the rising of facility attack
    st.markdown('**THE RISING OF FACILITY ATTACK**')
    st.markdown('Since 2000, the facility attack keep increasing in over the world. And the average damage of facility attack is much higher than bombing/ explosion attack (more than  3 times higher).')
    st.markdown('The facility attack is the number 1 damaged attack in USD in the regions in the table below')
    st.dataframe(property_damage_stt1.reset_index().query('attack_type == "Facility/Infrastructure Attack"')['region'])
    st.markdown('The table below show the number of value loss of damaged property over the year in world by top 2 types of propert damage terrorism attack')
    st.dataframe(facility_attack_df)
    if st.checkbox('Show chart', key='top3'):
        col1, col2 = st.beta_columns(2)
        with col1:
            fig, ax = plt.subplots()
            property_damage[(property_damage['property_damage'] !=-9) & (property_damage['attack_type'] == 'Bombing/Explosion')].groupby('year')['property_damage_USD'].sum().abs().plot(ax=ax,
                                                                                                                                                        
                                                                                                                                                        ylabel='Number of property damage in USD',
                                                                                                                                                        label='Bombing/Explosion',
                                                                                                                                                        legend=True)
            property_damage[(property_damage['property_damage'] !=-9) & (property_damage['attack_type'] == 'Facility/Infrastructure Attack')].groupby('year')['property_damage_USD'].sum().abs().plot(ax=ax,
                                                                                                                                                        
                                                                                                                                                        ylabel='Number of property damage in USD',
                                                                                                                                                        label='Facility/Infrastructure Attack',
                                                                                                                                                        legend=True)
            ax.set_title('Property Damaged in USD over the year')
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            property_damage[(property_damage['property_damage'] !=-9) & (property_damage['attack_type'] == 'Bombing/Explosion')].groupby('year')['property_damage'].sum().abs().plot(ax=ax,
                                                                                                                                                        
                                                                                                                                                        ylabel='Number of property damage attack',
                                                                                                                                                        label='Bombing/Explosion',
                                                                                                                                                        legend=True)
            property_damage[(property_damage['property_damage'] !=-9) & (property_damage['attack_type'] == 'Facility/Infrastructure Attack')].groupby('year')['property_damage'].sum().abs().plot(ax=ax,
                                                                                                                                                        
                                                                                                                                                        ylabel='Number of property damage attack',
                                                                                                                                                        label='Facility/Infrastructure Attack',
                                                                                                                                                        legend=True)
            ax.set_title('Number of property damage attack over the year')
            st.pyplot(fig)


    st.markdown('**PROPERTY DAMAGED IN USD CAUSED BY TOP 3 ATTACK TYPES**')
    st.markdown('The type of attack that casue most of property damage in USD is vary from regions.')
    st.markdown('The table below will show more detail on with type of attack that cause most damage and how much the damage is')
    st.dataframe(property_damage_stt1)
    
    st.markdown('**PROPERTY DAMAGED BY ATTACK TYPE BY COUNTRY SINCE 2000**')

    fig = px.choropleth(property_damage_stt3_top1_attack,
                    hover_data=['country', 'attack_type', 'property_damage_USD'],
                    locations = 'country',
                    locationmode = "country names",
                    projection="natural earth",
                    color='property_damage_USD',
                    color_continuous_scale =  px.colors.diverging.balance,
                    color_continuous_midpoint=property_damage_stt3_top1_attack['property_damage_USD'].mean())
    fig.update_layout(
        title= "MOST PROPERTY DAMAGED ATTACK TYPE BY COUNTRY SINCE 2000",
        title_x = 0.5,
        showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    property_damage_stt6 = property_damage.groupby(['year', 'country'])['property_damage_USD'].sum().sort_values(ascending=False).reset_index()
    st.dataframe(property_damage_stt6[property_damage_stt6['property_damage_USD'] > 0])
    fig, ax = plt.subplots()
    st.markdown('In 1 year, countries could lost to ***100M USD*** due to property damage attack. However, typically, in 1 year, 1 country could loss arround ***70,000 USD*** due to terrorism attack')
    n, bins, pathches = plt.hist(property_damage_stt6[property_damage_stt6['property_damage_USD'] > 2000]['property_damage_USD'])
    plt.xticks(bins)
    st.pyplot(fig)

    st.markdown('The table below give you the information of the highest property damage in USD in country and the terrorism attack type that make those damage.')

    st.dataframe(property_damage_stt3_top1_attack)
    
    

    # Check the most property damage in USD attack type in each region
    st.markdown('**TOP 5 HOTSPOT COUNTRIES IN TERM OF NUMBER PROPERTY DAMAGE ATTACK**')
    st.write(top5_property_damaged_country)
    if st.checkbox('Show top 5 hotspot cities in top 5 countries above', key='property_damage6'):
        st.dataframe(property_damage_stt4)
    st.markdown('**TOP 5 HOTSPOT COUNTRIES IN TERM OF VALUE LOSS BY PROPERTY DAMAGE ATTACK IN USD**')
    st.write(top5_property_damaged_country_USD)
    if st.checkbox('Show top 5 hotspot cities in top 5 countries above', key='property_damage7'):
        st.dataframe(property_damage_stt5)

    st.markdown('The countries in the table below are safe from the property damaged by terrorism since 2000 to 2017')
    st.dataframe(property_damage_stt3_top1_attack[property_damage_stt3_top1_attack['property_damage_USD'] == 0][['country', 'property_damage_USD']].drop_duplicates())


    ##########################################
    #          WHAT HAPPENS IN 2014          #
    ##########################################
    st.markdown('## WHAT HAPPENED IN 2014')
    terrorism_2014 = working_data[working_data['year'] == 2014]
    terrorism_2014 = terrorism_2014[terrorism_2014['property_damage'] != -9]

    terrorism_2014_stt = pd.pivot_table(
        terrorism_2014,
        values=['eventid', 'property_damage', 'property_damage_USD', 'fatality_num', 'wounded_num'],
        index=['region', 'country'],
        aggfunc={'eventid':'count', 'property_damage':sum, 'property_damage_USD':sum, 'fatality_num':sum, 'wounded_num':sum }
    )
    terrorism_2014_stt = terrorism_2014_stt.rename(columns={'eventid':'number_of_attacks'})
    terrorism_2014_stt['total_human_loss'] = terrorism_2014_stt['fatality_num'] + terrorism_2014_stt['wounded_num']
    terrorism_2014_stt = terrorism_2014_stt[['number_of_attacks', 'total_human_loss', 'fatality_num', 'wounded_num', 'property_damage', 'property_damage_USD']]

    ukraine_df = terrorism_2014[terrorism_2014['country'] == 'Ukraine']
    ukraine_df['total_human_loss'] = ukraine_df['fatality_num'] + ukraine_df['wounded_num']
    ukraine_df = ukraine_df[['date', 'province', 'city', 'summary', 'total_human_loss', 'fatality_num', 'wounded_num','attack_type', 'target_type', 'target_subtype', 'target_entity', 'target', 'target_nationality', 'attacker', 'motive', 'weapon_type', 'property_damage_USD']]
    ukraine_df = ukraine_df.sort_values(['total_human_loss'], ascending=False).head(10)

    philippines_df = terrorism_2014[terrorism_2014['country'] == 'Philippines']
    philippines_df['total_human_loss'] = philippines_df['fatality_num'] + philippines_df['wounded_num']
    philippines_df = philippines_df[['date', 'province', 'city', 'summary', 'total_human_loss', 'fatality_num', 'wounded_num','attack_type', 'target_type', 'target_subtype', 'target_entity', 'target', 'target_nationality', 'attacker', 'motive', 'weapon_type', 'property_damage_USD']]
    philippines_df = philippines_df.sort_values(['total_human_loss'], ascending=False).head(10)

    thailand_df = terrorism_2014[terrorism_2014['country'] == 'Thailand']
    thailand_df['total_human_loss'] = thailand_df['fatality_num'] + thailand_df['wounded_num']
    thailand_df = thailand_df[['date', 'province', 'city', 'summary', 'total_human_loss', 'fatality_num', 'wounded_num','attack_type', 'target_type', 'target_subtype', 'target_entity', 'target', 'target_nationality', 'attacker', 'motive', 'weapon_type', 'property_damage_USD']]
    thailand_df = thailand_df.sort_values(['total_human_loss'], ascending=False).head(10)

    st.dataframe(terrorism_2014_stt)
    st.markdown('United States is the country that take most damage because of terrorism in property loss in USD (over ***100M USD*** of property damage in USD) even though United States only took 25 terrorism attacks.')
    st.markdown('Besides United States, Spain also loss over ***1M USD*** of property damage even it took only 4 of terrorism attack, and Germany loss around ***800,000 USD*** with only 10 of terrorism attack.')
    st.markdown('In term of numbers of terrorism attacks, there are total of ***' + str(terrorism_2014_stt['number_of_attacks'].sum()) + '*** attacks in the world in 2014. And Ukraine (584 attacks), Philippines (530 attacks) and Thailand (369 attacks) are top 3 countries that took most number of attack.'+'And only top 3 countries took ***' + '%.2f'%((584+530+369)*100/(terrorism_2014_stt['number_of_attacks'].sum()))+ '%*** of total number attacks in the world in 2014.')
    st.markdown('And Ukraine, Philippines and Thailand also took highest number of human loss. The number of human loss in top 3 countries are ***'+ '%.2f'%((1999+929+671)*100/(terrorism_2014_stt['total_human_loss'].sum()))+'%*** of total human loss in 2014 because of terrorism attack.')
    st.markdown('The table below show the top 10 of attacks that caused most of human loss in Ukraine')
    st.dataframe(ukraine_df)
    st.markdown('The table below show the top 10 of attacks that caused most of human loss in Philippines')
    st.dataframe(philippines_df)
    st.markdown('The table below show the top 10 of attacks that caused most of human loss in Thailand')
    st.dataframe(thailand_df)















