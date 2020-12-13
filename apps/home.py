import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit.proto.Checkbox_pb2 import Checkbox
from data.import_data import load_terrorism_data
import seaborn as sns


def home():
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
    if st.checkbox('Show working data sample:', key='check_box1'):
        st.write('Data')
        st.dataframe(working_data.sample(10))
    st.markdown('## SCOPE OF WORK')
    st.markdown('This accessment report is focused to business operators and insurance companies. In this report, we will focus on those quantity number of loss by terrorism in term of human loss (wounded and fatality number),'+
    ' property/asset loss (number of damaged properties and the damaged value in USD) and after all, the information about the terrorism related to kidnapping/ taking hostage and try to answer the question of how much ransom we need to pay to keep the hostage survive')
    # Terrorism trend over the world
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
    
    # Property damage
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
    
    st.dataframe(property_damage_stt1)
    
    st.markdown('**PROPERTY DAMAGED BY ATTACK TYPE BY COUNTRY SINCE 2000**')

    fig = px.choropleth(property_damage_stt3_top1_attack,
                    hover_data=['country', 'attack_type', 'property_damage_USD'],
                    locations = 'country',
                    locationmode = "country names",
                    projection="natural earth",
                    color='property_damage_USD',
                    color_continuous_scale =  px.colors.diverging.balance,
                    color_continuous_midpoint=property_damage_stt3['property_damage_USD'].mean())
    fig.update_layout(
        title= "MOST PROPERTY DAMAGED ATTACK TYPE BY COUNTRY SINCE 2000",
        title_x = 0.5,
        showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

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
    st.dataframe(property_damage_stt3[property_damage_stt3['property_damage_USD'] == 0][['country', 'property_damage_USD']])

    #Hostage incident

    # PREPARE DATA
    hostage_incident_df = terrorism_df[(terrorism_df['hostage'] == 1) | (terrorism_df['attack_type'] == 4) | (terrorism_df['attack_type'] == 5) | (terrorism_df['attack_type'] == 6)].reset_index()
    hostage_incidents = len(hostage_incident_df)
    non_hostage_incidents = len(terrorism_df) - hostage_incidents
    a = (hostage_incidents * 100)/ (len(terrorism_df))

    hostage_incidents_ransom = (hostage_incident_df['ransom_demand'] == 1).sum()
    hostage_incidents_non_ransom = hostage_incidents - hostage_incidents_ransom
    b =  (hostage_incidents_ransom * 100)/hostage_incidents

    ransom_paid = (hostage_incident_df['ransom_paid'] > 0).sum()
    no_ransom_paid = hostage_incidents_ransom - ransom_paid
    c = (ransom_paid * 100)/hostage_incidents_ransom

    # DISPLAY DATA
    st.markdown('## HOSTAGE INCIDENT')

    st.markdown('**Hostage incidents compared to all incidents**')
    st.markdown('Since 1970, there are total ***'+ str(hostage_incidents) +'***, compared to ***'+ str(non_hostage_incidents)+'*** in total of ***'+str(len(terrorism_df))+'*** terrorism attacks since 1970.'+
    'Within hostage taking incidents, there are ***'+str(hostage_incidents_ransom)+'*** incidents that required ransom. And only ***'+str(ransom_paid)+'*** incidents, required ransom were paid '
    )
    st.markdown('In other word, ***'+'%.2f'%a+'%*** of all terrorism incidents take hostages. And ***'+ '%.2f'%b +'%*** of hostage taking incident required ransom. But only ***'+'%.2f'%c+'%*** of them were paid.')

    group1 = [non_hostage_incidents, hostage_incidents]
    group2 = [non_hostage_incidents, hostage_incidents_non_ransom, hostage_incidents_ransom]


    fig, ax = plt.subplots(figsize=(10, 10))
    size = 0.35

    cmap = plt.get_cmap("tab20c")
    outer_colors = cmap(np.arange(2)*5)
    inner_colors = cmap([3, 7, 4])

    ax.pie(group1, radius=1, colors=outer_colors,
        wedgeprops=dict(width=size, edgecolor='w'))

    ax.pie(group2, radius=1-size, colors=inner_colors,
        wedgeprops=dict(width=size, edgecolor='w'), labeldistance=1.5)


    ax.annotate( 'no hostage taken', (-0.2, 0.8))
    ax.annotate( 'hostage(s) \n taken', (0.7, -0.25))
    ax.annotate( 'ransom\n demand', (0.35, 0.03))
    ax.annotate( 'no ransom \n demand', (0.35, -0.15))

    ax.set_title('Proportion of attacks involving hostages', fontsize=15)
    st.pyplot(fig)

    st.markdown('**Which countries take the most hostages?**')
    # top countries where hostage incidents take place
    top_hostage_takers_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] == 4) & (hostage_incident_df['year'] > 2007)].groupby('country')['eventid'].count().sort_values(ascending=False).head(20)
    top_hostage_takers_non_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] != 4) & (hostage_incident_df['year'] > 2007)].groupby('country')['eventid'].count().sort_values(ascending=False).head(20)
    top_hostage_takers = pd.merge(top_hostage_takers_non_fatality, top_hostage_takers_fatality, on='country').reset_index().head(10)
    top_hostage_takers = top_hostage_takers.rename(columns={'eventid_x':'total_non_fatal','eventid_y':'total_fatal'})
    fig, ax = plt.subplots(figsize=(12,9))
    top_hostage_takers.plot.bar(x='country', stacked=True, ax=ax)
    ax.set(xlabel='Country', ylabel='Total hostage incidents')
    ax.set_title('Total attacks involving hostages by country (2007 - 2017)', fontsize=15)
    ax.legend(['No fatalities', 'One or more fatalities'], fontsize=12)
    st.pyplot(fig)

    st.markdown("The chances of survival in the countries that take the most captives during terrorist incidents very much depends on which country you are taken in. However, these charts don't tell us much about which types of hostage are targeted by the groups. Are you more likely to be taken as a local or foreigner?")

    st.markdown('**What are your real chances of being taken hostage as a foreigner?**')
    # add here countries with highest proportion of foreigners, stacked with ransom/non-ransom
    hostage_incident_foreigner_df = hostage_incident_df[(hostage_incident_df['target_nationality'] != hostage_incident_df['country']) & (hostage_incident_df['year'] > 2007)].reset_index(drop=True)
    # pie chart of hostage incidents, foreign vs local target
    local_vs_foreign_target = [(len(hostage_incident_df) - len(hostage_incident_foreigner_df)), len(hostage_incident_foreigner_df)]
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.pie(local_vs_foreign_target, labels=['Local target', 'Foreign target'], autopct='%1.1f%%')
    ax.set_title("Hostage incidents: local vs foreign targets", fontsize=15)
    st.pyplot(fig)
    # top 10 countries where you are more likely to be taken hostage as a foreigner
    hostage_incident_foreigner_top_10 = hostage_incident_foreigner_df.groupby('country')['eventid'].count().sort_values(ascending=False).head(10).index
    hostage_incident_foreigner_df_top_10 = hostage_incident_foreigner_df[hostage_incident_foreigner_df['country'].isin(hostage_incident_foreigner_top_10)].reset_index(drop=True)
    hostage_incident_foreigner_df_top_10 = hostage_incident_foreigner_df_top_10[hostage_incident_foreigner_df_top_10['ransom_demand'] >= 0]
    fig, ax = plt.subplots(figsize=(15, 8))
    sns.countplot(y = 'country', 
                hue = 'ransom_demand', 
                data = hostage_incident_foreigner_df_top_10)
    ax.set_title("Top Countries with Hostage Incidents Targeting Foreigners", fontsize=15)
    ax.legend(['No ransom demanded', 'Ransom demanded'])
    st.pyplot(fig)
    st.markdown("One country stands out: Philippines. Though the total number of foreign hostage events is not the highest, if you are kidnapped in Philippines there is a 50% chance of ransom demand.")
    focus = ['Syria', 'Philippines', 'Libya']
    hostage_incident_foreigner_ransom_df = hostage_incident_foreigner_df[hostage_incident_foreigner_df['country'].isin(focus)].reset_index(drop=True)
    hostage_incident_foreigner_ransom_df = hostage_incident_foreigner_ransom_df[(hostage_incident_foreigner_ransom_df['hostage_survived_num'] != -99) & (hostage_incident_foreigner_ransom_df['hostage_num'] != -99) & (hostage_incident_foreigner_ransom_df['ransom_paid'] != -99) & (hostage_incident_foreigner_ransom_df['ransom_demand_USD'] != -99)]
    hostage_incident_foreigner_ransom_df['hostage_fatalities'] = hostage_incident_foreigner_ransom_df['hostage_num'] - hostage_incident_foreigner_ransom_df['hostage_survived_num']
    # we can only do a 
    philippines_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Philippines'].reset_index(drop=True)
    philippines_corr_df = philippines_df[['ransom_demand_USD', 'hostage_fatalities', 'hostage_num']]
    philippines_corr = philippines_corr_df.corr()

    syria_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Syria'].reset_index(drop=True)
    syria_df = syria_df[['ransom_demand_USD', 'hostage_num', 'hostage_fatalities']]
    syria_corr = syria_df.corr()

    libya_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Libya'].reset_index(drop=True)
    libya_df = libya_df[['ransom_demand_USD', 'hostage_num', 'hostage_fatalities']]
    libya_corr = libya_df.corr()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Correlations between ransom and hostages", fontsize=18)
    heatmap_labels = ['Demand (USD)', '# abducted', '# killed']
    sns.heatmap(philippines_corr, linewidths=1, ax=axes[0], square=True, cbar=False, annot=True, cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[0].set_title("Philppines", fontsize=13)
    sns.heatmap(syria_corr, linewidths=1, ax=axes[1], square=True, cbar=False, annot=True, cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[1].set_title("Syria", fontsize=13)
    sns.heatmap(libya_corr, linewidths=1, ax=axes[2], square=True, cbar=False, annot=True, cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[2].set_title("Libya", fontsize=13)
    st.pyplot(fig)

    st.markdown('**Hostage incidents and ransom**')
    top_ransom_demander_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] == 4) & (hostage_incident_df['year'] > 2007) & (hostage_incident_df['ransom_demand'] == 1)].groupby('attacker')['eventid'].count().sort_values(ascending=False).head(20)
    top_ransom_demander_non_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] != 4) & (hostage_incident_df['year'] > 2007) & (hostage_incident_df['ransom_demand'] == 1)].groupby('attacker')['eventid'].count().sort_values(ascending=False).head(20)
    top_ransom_demander = pd.merge(top_ransom_demander_non_fatality, top_ransom_demander_fatality, on='attacker').reset_index().head(5) 
    top_ransom_demander = top_ransom_demander.rename(columns={'eventid_x':'total_non_fatal','eventid_y':'total_fatal'})
    top_ransom_demander_nat_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] == 4) & (hostage_incident_df['year'] > 2007) & (hostage_incident_df['ransom_demand'] == 1)].groupby('target_nationality')['eventid'].count().sort_values(ascending=False).head(20)
    top_ransom_demander_nat_non_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] != 4) & (hostage_incident_df['year'] > 2007) & (hostage_incident_df['ransom_demand'] == 1)].groupby('target_nationality')['eventid'].count().sort_values(ascending=False).head(20)
    top_ransom_demander_nat = pd.merge(top_ransom_demander_nat_non_fatality, top_ransom_demander_nat_fatality, on='target_nationality').reset_index().head(5)
    top_ransom_demander_nat = top_ransom_demander_nat.rename(columns={'eventid_x':'total_non_fatal','eventid_y':'total_fatal'})
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle("Hostage incidents demanding ransoms (2007 - 2017)", fontsize=18)

    top_ransom_demander.plot(x='attacker', kind='barh', ax=axes[0], stacked=True)
    axes[0].set_title("Total by hostage taker group", fontsize=15)
    axes[0].set_xlabel('Incident count')
    axes[0].set_ylabel('Group')
    axes[0].legend(['No fatalities', 'One or more fatalities'], fontsize=12)


    top_ransom_demander_nat.plot(x='target_nationality', kind='barh', ax=axes[1], stacked=True)
    axes[1].set_title("Total by hostage nationality", fontsize=15)
    axes[1].set_xlabel('Incident count')
    axes[1].set_ylabel('Hostage nationality')
    axes[1].legend(['No fatalities', 'One or more fatalities'], fontsize=12)
    st.pyplot(fig)

    st.markdown('**How much ransom money is demanded/paid?**')
    ransom_demand_USD_df = hostage_incident_df[['eventid', 'year', 'target','month', 'day', 'attacker','hostage_num', 'hostage_hours', 'hostage_days', 'ransom_demand_USD', 'ransom_paid', 'hostage_outcome','hostage_survived_num']]
    ransom_demand_USD_df = ransom_demand_USD_df[(ransom_demand_USD_df['ransom_demand_USD'] != -99) & (ransom_demand_USD_df['ransom_demand_USD'] > 0)]
    ransom_paid_USD_df = ransom_demand_USD_df.loc[ransom_demand_USD_df['ransom_paid'] > 0]

    fig, ax = plt.subplots(figsize=(15, 10))

    ransom_demand_USD_df.hist(column='ransom_demand_USD', bins = 20, range=[0,200000], ax=ax)
    ransom_paid_USD_df.hist(column='ransom_paid', range=[0,200000], bins = 20, ax=ax)
    ax.set_title('Frequency of ransom demand (USD - up to 200k)', size=15)
    ax.set_xlabel('Ransom demand (USD)')
    ax.set_ylabel('Frequency')
    ax.legend(['Ransom amount demanded', 'Ransom amount paid'], fontsize=12)
    st.pyplot(fig)
    st.markdown('Typically, most ransom demands are below USD $75,000. <br> However, the amount actually paid to the abductees is typically lower and less frequent.')
    st.markdown('Does paying less than the requested amount of ransom decrease the chances of a successful release (no hostages killed)?')
    ransom_paid_USD_df['hostage_killed_num'] = ransom_paid_USD_df['hostage_num'] - ransom_paid_USD_df['hostage_survived_num']
    ransom_paid_USD_df['hostage_killed'] = ransom_paid_USD_df['hostage_killed_num'].apply(lambda x: 'One or more fatality' if x > 0 else 'No fatalities')
    st.dataframe(ransom_paid_USD_df)
    st.markdown('In cases where ransom was demanded and paid, most demands were met.')
    st.markdown('A handful of cases paid under the requested amount, and one case paid more.')
    st.markdown("There doesn't seem to be a correlation between meeting the reqested amount and a successful outcome: hostages died when demands were met, and when they weren't. ")
    fig, ax = plt.subplots(figsize=(12, 12))
    sns.scatterplot(x = 'ransom_demand_USD',
                    y = 'ransom_paid', 
                    hue = 'hostage_killed', 
                    data = ransom_paid_USD_df,
                    legend="full")

    ax.set_title('Ransom requested vs paid (up to 200k)', size=15)
    ax.set_xlabel('Ransom demand USD')
    ax.set_ylabel('Ransom paid USD')
    ax.set_xlim([0, 200000])
    ax.set_ylim([0, 200000])
    ax.set_aspect('equal', 'box')
    ax.legend(['No fatalities', 'One or more fatalities'], fontsize=12)

    st.pyplot(fig)

    st.markdown("**What happens if you don't pay?**")
    ransom_not_paid = hostage_incident_df[(hostage_incident_df['ransom_demand_USD'] > 0) & (hostage_incident_df['ransom_paid'] == 0)]
    ransom_not_paid['hostage_killed_num'] = ransom_not_paid['hostage_num'] - ransom_not_paid['hostage_survived_num']
    hostages_killed_per_incident_ransom_not_paid_a = ((len(ransom_not_paid[ransom_not_paid['hostage_killed_num'] > 0])) * 100)/len(hostage_incident_df)
    hostages_killed_per_incident_ransom_not_paid_b = ((len(ransom_not_paid[ransom_not_paid['hostage_killed_num'] > 0])) * 100)/len(ransom_not_paid)
    st.markdown('There are ***'+'%2.2f'%hostages_killed_per_incident_ransom_not_paid_a+' %*** of the hostages in the total taken hostage incidents were killed even they paid the ransom.')
    st.markdown('And there are ***' + '%2.2f'%hostages_killed_per_incident_ransom_not_paid_b +'%*** of hostages that paid ransom were killed (The percentage is calculated as the killed and paid ransom hostages over the total of paid ransom hostages')
    hostages_killed_per_incident_ransom_paid_a = ((len(ransom_paid_USD_df[ransom_paid_USD_df['hostage_killed_num'] > 0])) * 100)/len(hostage_incident_df)
    hostages_killed_per_incident_ransom_paid_b = ((len(ransom_paid_USD_df[ransom_paid_USD_df['hostage_killed_num'] > 0])) * 100)/len(ransom_paid_USD_df)
    st.markdown('However, there are only ***'+'%2.2f'%hostages_killed_per_incident_ransom_paid_a+'%*** of hostages in total of hostage taken incidents were killed when they ***DID NOT*** pay the ransom.')
    st.markdown('And, there are only ***'+'%2.2f'%hostages_killed_per_incident_ransom_paid_b+'%*** of hostages were killed in total of not-paid-ransom incidents')
    st.markdown('THINK TWICE BEFORE DECIDING PAY RANSOM BECAUSE YOU WILL GET HIGHER CHANGE TO SURVIVED WHEN NOT PAID RANSOM')














