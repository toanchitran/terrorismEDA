import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit.proto.Checkbox_pb2 import Checkbox
from data.import_data import load_terrorism_data
import plotly.graph_objects as go

# /Users/Alec/anaconda3/envs/cs_ftmle


def app():
    terrorism_df = load_terrorism_data()
    st.title('INCIDENTS INVOLVING HOSTAGES')
    st.markdown('The following information will provide an overview of terrorist incidents involving hostages and investigate/evaluate risk factors to consider when insuring an individual in an at-risk environment.')
    # terrorism_df = load_terrorism_data()

    st.markdown('## HOSTAGE INCIDENTS AS A PROPORTION OF ALL INCIDENTS')
    st.markdown('A significant portion of terrorist attacks do not involve hostage taking. To add, a significant portion of hostage incidents do not include a demand for ransom.')

    hostage_incident_df = terrorism_df[(terrorism_df['hostage'] == 1) | (terrorism_df['attack_type'] == 4) | (
        terrorism_df['attack_type'] == 5) | (terrorism_df['attack_type'] == 6)].reset_index()
    total_incidents = len(terrorism_df)
    hostage_incidents = len(hostage_incident_df)
    non_hostage_incidents = total_incidents - hostage_incidents
    hostage_incidents_ransom = (
        hostage_incident_df['ransom_demand'] == 1).sum()
    hostage_incidents_non_ransom = hostage_incidents - hostage_incidents_ransom
    ransom_paid = (hostage_incident_df['ransom_paid'] > 0).sum()
    no_ransom_paid = hostage_incidents_ransom - ransom_paid

    fig = go.Figure(go.Sunburst(
        labels=["Total incidents", "no hostage taken", "hostage taken",
                "no ransom demand", "ransom demand", "ransom paid", "no ransom paid"],
        parents=["", "Total incidents", "Total incidents", "hostage taken",
                 "hostage taken", "ransom demand", "ransom demand"],
        values=[total_incidents, non_hostage_incidents, hostage_incidents,
                hostage_incidents_non_ransom, hostage_incidents_ransom, ransom_paid, no_ransom_paid],
        branchvalues="total",
        maxdepth=2,
        insidetextorientation="horizontal"
    ))
    fig.update_layout(
        title='All terrorism incidents broken down by hostage situation',
        title_x=0.5,
        height=650)

    st.plotly_chart(fig)

    st.markdown('## WHICH COUNTRIES TAKE THE MOST HOSTAGES?')
    top_hostage_takers_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] == 4) & (
        hostage_incident_df['year'] > 2007)].groupby('country')['eventid'].count().sort_values(ascending=False).head(20)
    top_hostage_takers_non_fatality = hostage_incident_df.loc[(hostage_incident_df['hostage_outcome'] != 4) & (
        hostage_incident_df['year'] > 2007)].groupby('country')['eventid'].count().sort_values(ascending=False).head(20)
    top_hostage_takers = pd.merge(top_hostage_takers_non_fatality,
                                  top_hostage_takers_fatality, on='country').reset_index().head(10)
    top_hostage_takers = top_hostage_takers.rename(columns={'eventid_x': 'total_non_fatal',
                                                            'eventid_y': 'total_fatal'})
    st.dataframe(top_hostage_takers)

    fig, ax = plt.subplots(figsize=(12, 9))
    top_hostage_takers.plot.bar(x='country', stacked=True, ax=ax)
    ax.set(ylabel='Total hostage incidents')
    ax.set_title(
        'Total attacks involving hostages by country (2007 - 2017)', fontsize=15)
    ax.grid(axis='y')
    ax.tick_params(axis='x', rotation=45)
    ax.set_xlabel('')
    ax.legend(['No fatalities', 'One or more fatalities'], fontsize=12)
    st.pyplot(fig)

    st.markdown('The chances of survival in the countries that take the most captives during terrorist incidents very much depends on which country you are taken in.  However, these charts do not tell us much about which types of hostage are targeted by the groups. Are you more likely to be taken as a local or foreigner?')
    st.markdown(
        '## WHAT ARE YOUR REAL CHANCES OF BEING TAKEN HOSTAGE AS A FOREIGNER?')

    hostage_incident_foreigner_df = hostage_incident_df[(hostage_incident_df['target_nationality'] != hostage_incident_df['country']) & (
        hostage_incident_df['year'] > 2007)].reset_index(drop=True)
    hostage_incident_local_df = hostage_incident_df[(hostage_incident_df['target_nationality'] == hostage_incident_df['country']) & (
        hostage_incident_df['year'] > 2007)].reset_index(drop=True)

    total_foreigner_hostage_incidents = len(hostage_incident_foreigner_df)
    total_local_hostage_incidents = len(hostage_incident_local_df)
    total_local_hostage_incidents_ransom = (
        hostage_incident_local_df['ransom_demand'] == 1).sum()
    total_local_hostage_incidents_no_ransom = total_local_hostage_incidents - \
        total_local_hostage_incidents_ransom
    total_foreigner_hostage_incidents_ransom = (
        hostage_incident_foreigner_df['ransom_demand'] == 1).sum()
    total_foreigner_hostage_incidents_no_ransom = total_foreigner_hostage_incidents - \
        total_foreigner_hostage_incidents_ransom

    fig = go.Figure(go.Sunburst(
        labels=["Hostage incidents (nat. confirmed)", "Local hostages taken", "Foreign hostages taken",
                "Locals ransomed", "Locals not ransomed", "Foreigners ransomed", "Foreigners not ransomed"],
        parents=["", "Hostage incidents (nat. confirmed)", "Hostage incidents (nat. confirmed)", "Local hostages taken",
                 "Local hostages taken", "Foreign hostages taken", "Foreign hostages taken"],
        values=[7837, total_local_hostage_incidents, total_foreigner_hostage_incidents, total_local_hostage_incidents_ransom,
                total_local_hostage_incidents_no_ransom, total_foreigner_hostage_incidents_ransom, total_foreigner_hostage_incidents_no_ransom],
        branchvalues="total",
        maxdepth=2,
        insidetextorientation="horizontal"
    ))

    fig.update_layout(
        title='Hostage incidents: local vs foreign targets',
        title_x=0.5,
        height=650)

    st.plotly_chart(fig)
    st.markdown('Of all hostage incidents, locals are targeted far more frequently than foreigners. However, if a foreigner is taken, the chances of a ransom demand is higher (albeit still low).')

    hostage_incident_foreigner_top_10 = hostage_incident_foreigner_df.groupby(
        'country')['eventid'].count().sort_values(ascending=False).head(10).index
    hostage_incident_foreigner_df_top_10 = hostage_incident_foreigner_df[hostage_incident_foreigner_df['country'].isin(
        hostage_incident_foreigner_top_10)].reset_index(drop=True)
    hostage_incident_foreigner_df_top_10 = hostage_incident_foreigner_df_top_10[
        hostage_incident_foreigner_df_top_10['ransom_demand'] >= 0]

    fig, ax = plt.subplots(figsize=(15, 8))
    sns.countplot(y='country',
                  hue='ransom_demand',
                  data=hostage_incident_foreigner_df_top_10)

    ax.set_title(
        "Top Countries with Hostage Incidents Targeting Foreigners", fontsize=15)
    ax.legend(['No ransom demanded', 'Ransom demanded'], fontsize=12)
    ax.grid(axis='x')
    ax.tick_params(axis='y', rotation=45)
    ax.set_xlabel('')
    st.pyplot(fig)

    st.markdown('Three countries stand out: Syria, Libya and the Philippines. THe former two due to the high total incidents (as well as ransom incidents) and the latter due to the proportionality of ransom to non-ransom totals. We will focus in on these countries.')

    focus = ['Syria', 'Philippines', 'Libya']
    hostage_incident_foreigner_ransom_df = hostage_incident_foreigner_df[hostage_incident_foreigner_df['country'].isin(
        focus)].reset_index(drop=True)
    hostage_incident_foreigner_ransom_df = hostage_incident_foreigner_ransom_df[(hostage_incident_foreigner_ransom_df['hostage_survived_num'] != -99) & (
        hostage_incident_foreigner_ransom_df['hostage_num'] != -99) & (hostage_incident_foreigner_ransom_df['ransom_paid'] != -99) & (hostage_incident_foreigner_ransom_df['ransom_demand_USD'] != -99)]
    hostage_incident_foreigner_ransom_df['hostage_fatalities'] = hostage_incident_foreigner_ransom_df['hostage_num'] - \
        hostage_incident_foreigner_ransom_df['hostage_survived_num']

    philippines_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Philippines'].reset_index(
        drop=True)
    philippines_corr_df = philippines_df[[
        'ransom_demand_USD', 'hostage_fatalities', 'hostage_num']]
    philippines_corr = philippines_corr_df.corr()

    syria_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Syria'].reset_index(
        drop=True)
    syria_df = syria_df[['ransom_demand_USD',
                         'hostage_num', 'hostage_fatalities']]
    syria_corr = syria_df.corr()

    libya_df = hostage_incident_foreigner_ransom_df[hostage_incident_foreigner_ransom_df['country'] == 'Libya'].reset_index(
        drop=True)
    libya_df = libya_df[['ransom_demand_USD',
                         'hostage_num', 'hostage_fatalities']]
    libya_corr = libya_df.corr()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Correlations between ransom and hostages", fontsize=18)

    heatmap_labels = ['Demand (USD)', '# abducted', '# killed']

    sns.heatmap(philippines_corr, linewidths=1, ax=axes[0], square=True, cbar=False, annot=True,
                cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[0].set_title("Philppines", fontsize=13)

    sns.heatmap(syria_corr, linewidths=1, ax=axes[1], square=True, cbar=False, annot=True,
                cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[1].set_title("Syria", fontsize=13)

    sns.heatmap(libya_corr, linewidths=1, ax=axes[2], square=True, cbar=False, annot=True,
                cmap="vlag", center=0, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
    axes[2].set_title("Libya", fontsize=13)

    st.pyplot(fig)

    st.markdown('In the above we can see two interesting observations: in The Philippines, the ransom demand has a strong positive correlation with number of foreign hostages captured, and in Libya the ransom demand is negatively correlated with number of hostages killed.')

    st.markdown(
        '## HOW MUCH RANSOM IS DEMANDED AND PAID?')

    ransom_demand_USD_df = hostage_incident_df[['eventid', 'year', 'target', 'month', 'day', 'attacker', 'hostage_num',
                                                'hostage_hours', 'hostage_days', 'ransom_demand_USD', 'ransom_paid', 'hostage_outcome', 'hostage_survived_num']]
    ransom_demand_USD_df = ransom_demand_USD_df[(
        ransom_demand_USD_df['ransom_demand_USD'] != -99) & (ransom_demand_USD_df['ransom_demand_USD'] > 0)]
    ransom_paid_USD_df = ransom_demand_USD_df.loc[ransom_demand_USD_df['ransom_paid'] > 0]

    fig, ax = plt.subplots(figsize=(15, 10))

    ransom_demand_USD_df.hist(
        column='ransom_demand_USD', bins=20, range=[0, 200000], ax=ax)
    ransom_paid_USD_df.hist(column='ransom_paid', range=[
                            0, 200000], bins=20, ax=ax)

    ax.set_title('Frequency of ransom demand (USD - up to 200k)', size=15)
    ax.set_xlabel('Ransom demand (USD)')
    ax.set_ylabel('Frequency')

    ax.legend(['Ransom amount demanded', 'Ransom amount paid'], fontsize=12)

    st.pyplot(fig)

    st.markdown('Typically, most ransom demands are below USD $75,000. However, the amount actually paid to the abductees is typically lower and occurs less frequently.')

    st.markdown(
        '## DOES PAYING LESS THAN DEMANDED AMOUNT RESULT IN A MORE DANGEROUS INCIDENT?')

    ransom_paid_USD_df['hostage_killed_num'] = ransom_paid_USD_df['hostage_num'] - \
        ransom_paid_USD_df['hostage_survived_num']
    ransom_paid_USD_df['hostage_killed'] = ransom_paid_USD_df['hostage_killed_num'].apply(
        lambda x: 'One or more fatality' if x > 0 else 'No fatalities')

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.scatterplot(x='ransom_demand_USD',
                    y='ransom_paid',
                    hue='hostage_killed',
                    data=ransom_paid_USD_df,
                    legend="full")

    ax.set_title('Ransom requested vs paid (up to 200k)', size=15)
    ax.set_xlabel('Ransom demand USD')
    ax.set_ylabel('Ransom paid USD')
    ax.set_xlim([0, 200000])
    ax.set_ylim([0, 200000])
    ax.grid(axis='both')
    ax.set_aspect('equal', 'box')
    ax.legend(title="")

    st.pyplot(fig)

    st.markdown(
        "## WHAT HAPPENS IF YOU DON'T PAY?")

    ransom_not_paid = hostage_incident_df[(hostage_incident_df['ransom_demand_USD'] > 0) & (hostage_incident_df['ransom_paid'] == 0)]
    ransom_not_paid['hostage_killed_num'] = ransom_not_paid['hostage_num'] - ransom_not_paid['hostage_survived_num']
    hostages_killed_per_incident_ransom_not_paid_a = ((len(ransom_not_paid[ransom_not_paid['hostage_killed_num'] > 0])) * 100)/len(hostage_incident_df)
    hostages_killed_per_incident_ransom_not_paid_b = ((len(ransom_not_paid[ransom_not_paid['hostage_killed_num'] > 0])) * 100)/len(ransom_not_paid)
    st.markdown('There are ***'+'%2.2f'%hostages_killed_per_incident_ransom_not_paid_a+' %*** of the hostages in the total taken hostage incidents were killed even they paid the ransom.')
    st.markdown('And there are ***' + '%2.2f'%hostages_killed_per_incident_ransom_not_paid_b +'%*** of hostages that were killed in all of paid ransom incidents')
    hostages_killed_per_incident_ransom_paid_a = ((len(ransom_paid_USD_df[ransom_paid_USD_df['hostage_killed_num'] > 0])) * 100)/len(hostage_incident_df)
    hostages_killed_per_incident_ransom_paid_b = ((len(ransom_paid_USD_df[ransom_paid_USD_df['hostage_killed_num'] > 0])) * 100)/len(ransom_paid_USD_df)
    st.markdown('However, there are only ***'+'%2.2f'%hostages_killed_per_incident_ransom_paid_a+'%*** of hostages in total of hostage taken incidents were killed when they ***DID NOT*** pay the ransom.')
    st.markdown('And, there are only ***'+'%2.2f'%hostages_killed_per_incident_ransom_paid_b+'%*** of hostages that were killed in all of not-paid-ransom incidents')
    st.markdown('THINK TWICE BEFORE DECIDING PAY RANSOM BECAUSE YOU WILL GET HIGHER CHANGE TO SURVIVED WHEN NOT PAID RANSOM')

    st.markdown(
        "## CAVEAT")
    st.markdown("Ransom data in this dataset was scant (~250 entries contained ransom dollar amounts of a dataset of ~180k rows). This is likely because when ransoms are paid, the payer (whether a government, corp or individual) is unlikely to, or discouraged from, publicising the act as to deter other hostage-takers.")
