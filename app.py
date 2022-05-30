import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 30}) # changing the font size
import seaborn as sns
import plotly.figure_factory as ff

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df, region_df)
st.sidebar.title('Olympics analysis')
st.sidebar.image('https://upload.wikimedia.org/wikipedia/commons/5/5c/Olympic_rings_without_rims.svg')

user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# st.dataframe(df)

if user_menu == 'Medal Tally' :
    st.sidebar.header('Medal Tally')
    country, years = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Select Year', years)
    selected_country = st.sidebar.selectbox('Select Country', country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall' :
        st.title('Overall Tally')
    elif selected_year == 'Overall' and selected_country != 'Overall' :
        st.title('{} Tally'.format(selected_country))
    elif selected_year != 'Overall' and selected_country == 'Overall' :
        st.title('Overall Performance in {} Olympics'.format(selected_year))
    else :
        st.title('{} Performance in {} Olympics'.format(selected_country, selected_year))

    st.table(medal_tally)

if user_menu == 'Overall Analysis' :
    editions = df['Year'].unique().shape[0]
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]


    st.title('Top Stats')
    col1, col2, col3 = st.columns(3)
    with col1 :
        st.header('Editions')
        st.title(editions)
    with col2 :
        st.header('Hosts')
        st.title(cities)
    with col3 :
        st.header('Sports')
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1 :
        st.header('Events')
        st.title(events)
    with col2 :
        st.header('Athletes')
        st.title(athletes)
    with col3 :
        st.header('Nations')
        st.title(nations)


    nations_over_time = helper.participating_nations_over_time(df, 'region')
    fig1 = px.line(nations_over_time, x='Edition', y='region')
    st.title('Participating nations over the years')
    st.plotly_chart(fig1)

    events_over_time = helper.participating_nations_over_time(df, 'Event')
    fig2 = px.line(events_over_time, x='Edition', y='Event')
    st.title('Number of Events over the years')
    st.plotly_chart(fig2)

    athletes_over_time = helper.participating_nations_over_time(df, 'Name')
    fig3 = px.line(athletes_over_time, x='Edition', y='Name', labels={'Name' : 'Number of Athletes'})
    st.title('Number of Athletes over the years')
    st.plotly_chart(fig3)

    st.title('Number of Events over time(Every Sport)')
    fig,ax = plt.subplots(figsize=(40, 40))
    events_over_time = df.drop_duplicates(['Year', 'Event', 'Sport'])
    table = events_over_time.pivot_table(columns='Year', index='Sport', values='Event', aggfunc='count').fillna(
        0).astype(int)
    ax = sns.heatmap(table, annot=True, cmap='Blues')
    st.pyplot(fig)

    st.title('Most Successful Athletes')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    tab = helper.most_successful(df, selected_sport)
    st.table(tab)

if user_menu == 'Country-wise Analysis' :

    country_list = df['region'].dropna().unique()
    country_list.sort()
    selected_country = st.selectbox('Select a Country', country_list)
    yearwise_df = helper.yearwise_medal_tally(df, selected_country)
    fig1 = px.line(yearwise_df, x='Year', y='Medal')
    st.title('Medals won by {} over the years'.format(selected_country))
    st.plotly_chart(fig1)

    pt=helper.country_event_heatmap(df, selected_country)
    st.title('Heatmap of Medals won by {} over the years'.format(selected_country))
    fig, ax = plt.subplots(figsize=(40, 40))
    ax = sns.heatmap(pt, annot=True, cmap='Blues')
    st.pyplot(fig)

    st.title('Top athletes from {}'.format(selected_country))
    ath_country_top = helper.most_successful_from_country(df, selected_country)
    st.table(ath_country_top)

if user_menu == 'Athlete-wise Analysis' :
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=800, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    st.title('Sport-wise Age Distribution')
    selected_medal = st.selectbox('Select Medal Type', ['Gold', 'Silver', 'Bronze'])
    x = []
    name = []
    famous_sports = ['Athletics', 'Gymnastics', 'Swimming', 'Shooting', 'Cycling', 'Fencing',
       'Rowing', 'Wrestling', 'Football', 'Sailing', 'Equestrianism',
       'Canoeing', 'Boxing', 'Hockey', 'Basketball', 'Weightlifting',
       'Water Polo', 'Judo', 'Handball', 'Volleyball']

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == selected_medal]['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=800, height=600)
    st.plotly_chart(fig)


    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)

    st.title('Height Vs Weight')
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots(figsize=(15, 10))
    plt.rcParams.update({'font.size': 10})
    ax = sns.scatterplot(temp_df['Weight'], temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60)
    st.pyplot(fig)

    st.title('Men Vs Women Participation over the Years') # title
    final = helper.men_vs_women(df, selected_sport)

    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=800, height=600)
    st.plotly_chart(fig)