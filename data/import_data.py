import pandas as pd
import numpy as np
import streamlit as st
import os

# DATA_URL = ('https://media.githubusercontent.com/media/toanchitran/CoderSchool_ML_IZU/master/terrorism.csv')

read_and_cache_csv = st.cache(pd.read_csv)
# data_path =  os.path.join(os.getcwd(), "data")
@st.cache(suppress_st_warning=True)
def load_terrorism_data(year=None):
    drop_col = ['approxdate', 'specificity','vicinity','location', 'region', 'country', 'doubtterr', 'alternative', 'alternative_txt', 'attacktype1','attacktype2', 'attacktype2_txt','attacktype3', 'attacktype3_txt'
    ,'targtype1', 'targsubtype1', 'targtype2', 'targtype2_txt', 'targsubtype2', 'targsubtype2_txt', 'natlty1', 'corp2', 'target2', 'natlty2', 'natlty2_txt', 'targtype3', 'targtype3_txt', 'targsubtype3', 'targsubtype3_txt', 'corp3', 'target3', 'natlty3', 'natlty3_txt'
    ,'gsubname', 'gname2', 'gsubname2', 'gname3', 'gsubname3', 'guncertain2', 'guncertain3', 'claimmode', 'claim2', 'claimmode2', 'claimmode2_txt', 'claim3', 'claimmode3', 'claimmode3_txt','compclaim', 'weaptype1', 'weapsubtype1', 'weaptype2', 'weaptype2_txt', 'weapsubtype2', 'weapsubtype2_txt','weaptype3', 'weaptype3_txt', 'weapsubtype3', 'weapsubtype3_txt','weaptype4', 'weaptype4_txt', 'weapsubtype4', 'weapsubtype4_txt', 'weapdetail', 'divert', 'kidhijcountry', 'ransomamtus', 'ransompaidus', 'ransomnote', 'addnotes', 'scite1', 'scite2', 'scite3'
    ,'INT_LOG', 'INT_IDEO', 'INT_MISC', 'related', 'dbsource']
    DATA_URL = ('terrorism.csv')
    terrorism_df = read_and_cache_csv(DATA_URL, nrows=200000, encoding='ISO-8859-1').drop(columns=drop_col)
    terrorism_df.rename(columns = {'iyear':'year',
                               'imonth':'month',
                               'iday':'day',
                               'country_txt':'country',
                               'region_txt':'region',
                               'resolution':'resolution_date',
                               'provstate':'province',
                               'multiple':'multiple_incident',
                               'success':'successful_attack',
                               'attacktype1_txt':'attack_type',
                               'targtype1_txt':'target_type',
                               'targsubtype1_txt':'target_subtype',
                               'corp1':'target_entity',
                               'target1':'target',
                               'natlty1_txt':'target_nationality',
                               'gname':'attacker',
                               'guncertain1':'attacker_uncertain',
                               'individual':'lone_wolf',
                               'nperps':'attacker_num',
                               'nperpcap':'captured_num',
                               'weaptype1_txt':'weapon_type',
                               'weapsubtype1_txt':'weapon_subtype',
                               'nkill':'fatality_num',
                               'nkillus':'US_fatality_num',
                               'nkillter':'attacker_fatality_num',
                               'nwound':'wounded_num',
                               'nwoundus':'US_wounded_num',
                               'nwoundte':'attacker_wounded_num',
                               'property':'property_damage',
                               'propextent':'property_damage_ext',
                               'propvalue':'property_damage_USD',
                               'ishostkid':'hostage',
                               'nhostkid':'hostage_num',
                               'nhostkidus':'US_hostage_num',
                               'nhours':'hostage_hours',
                               'ndays':'hostage_days',
                               'ransom':'ransom_demand',
                               'ransomamt':'ransom_demand_USD',
                               'ransompaid':'ransom_paid',
                               'hostkidoutcome':'hostage_outcome',
                               'hostkidoutcome_txt':'hostage_outcome_txt',
                               'nreleased':'hostage_survived_num',
                               'INT_ANY':'international_attack'
                               }, inplace = True)
    terrorism_df['day'] = terrorism_df['day'].apply(lambda x: np.random.randint(1,32) if x == 0 else x)
    terrorism_df['month'] = terrorism_df['month'].apply(lambda x: np.random.randint(1,13) if x == 0 else x)

    terrorism_df['date'] = pd.to_datetime(terrorism_df[['year','month', 'day' ]], errors= 'coerce') #created a new column as merging year-month-day.
    terrorism_df['date'] = pd.to_datetime(terrorism_df['date']) 
    terrorism_df['day_of_week'] = terrorism_df['date'].dt.day_name() #a new columns as day of week.

    if year == None:
        return terrorism_df
    else:
        return terrorism_df[terrorism_df['year'] >= year]