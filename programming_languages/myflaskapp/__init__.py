"""Main file of the Flask application

You can launch it by copying the entire 'programming_languages' folder to a
directory of your choice. Then, you have to make sure that you have all
required python libraries installed.

On a Windows system, you can then open a command line and go to the directory
that contains the 'programming_languages' folder. Enter the following commands:
C:[your_path]>set flask_app=programming_languages.myflaskapp
C:[your_path]>set flask_env=development
C:[your_path]>flask run

On a Linux system, you can then open a bash terminal and go to the directory
that contains the 'programming_languages' folder. Enter the following commands:
your_name@[your_path]$export FLASK_APP=programming_languages.myflaskapp
your_name@[your_path]$export FLASK_ENV=development
your_name@[your_path]$flask run
"""

# %% Import all necessary moduls
# ------------------------------

# Flask main app
from flask import Flask, render_template, request

# further modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import quote_plus
import json
import plotly
import plotly.express as px

# only for development: set working directory so that absolute imports work
if __name__ == "__main__":
    import os
    mydir = "***insert dir that contains the 'programming_languages' folder***"
    os.chdir(mydir)

# absolute import of self defined module (see corresponding *.py file)
from programming_languages.myflaskapp.models import (Language,
                                                     Succession,
                                                     Team,
                                                     Affiliation)

# %% Setup Flask app
# ------------------

app = Flask(__name__)

# Flask configuration
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# This configuration makes sure that the browser does not store static files
# such as the plot images or the javascripts in the cache.
# It is not necessary here as the plots always display the same data from a
# database where no data manipulations are taking place.
# However, preventing browser caching made the app development easier.


# %% Database engine & session creation
# -------------------------------------
# based on: https://hackersandslackers.com/implement-sqlalchemy-orm
# and: https://docs.sqlalchemy.org/en/14/core/engines.html#sqlite

# The connect_args argument is necessary to avoid the following error message
# when running Flask: "ProgrammingError: SQLite objects created in a thread can
# only be used in that same thread"
# see: https://stackoverflow.com/a/54740505/11826257

engine = create_engine('sqlite:///programming_languages/myflaskapp/data.db',
                       connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
dbsession = Session()


# %% Fetch and rearrange the data from the database

# fetch language ids, names and years from the 'language' table
res = dbsession.query(Language).order_by(Language.name).all()
Language_lang_ids = []
Language_names = []
Language_years = []
for row in res:
    Language_lang_ids.append(row.lang_id)
    Language_names.append(row.name)
    Language_years.append(row.year)
dict_Language = {"lang_id": Language_lang_ids,
                 "Name": Language_names,
                 "Year": Language_years}
df_Language = pd.DataFrame(dict_Language)

# fetch developer names from the 'team' table and create dataframe with strings
# of semicolon-separated developers for each language
res = dbsession.query(Team).all()
Team_lang_ids = []
Team_developers = []
for row in res:
    Team_lang_ids.append(row.lang_id)
    Team_developers.append(row.developer)
unique_Team_lang_ids = list(set(Team_lang_ids))
list_of_developers = []
for Team_lang_id in unique_Team_lang_ids:
    mylist = []
    for i in range(len(Team_lang_ids)):
        if Team_lang_id == Team_lang_ids[i]:
            mylist.append(Team_developers[i])
    list_of_developers.append('; '.join(mylist))
dict_Teams = {"lang_id": unique_Team_lang_ids,
              "Developers": list_of_developers}
df_Teams = pd.DataFrame(dict_Teams)

# fetch companies from the 'affiliation' table and create dataframe with
# strings of semicolon-separated companies for each language
res = dbsession.query(Affiliation).all()
Affiliation_lang_ids = []
Affiliation_companies = []
for row in res:
    Affiliation_lang_ids.append(row.lang_id)
    Affiliation_companies.append(row.company)
unique_Affiliation_lang_ids = list(set(Affiliation_lang_ids))
list_of_companies = []
for Affiliation_lang_id in unique_Affiliation_lang_ids:
    mylist = []
    for i in range(len(Affiliation_lang_ids)):
        if Affiliation_lang_id == Affiliation_lang_ids[i]:
            mylist.append(Affiliation_companies[i])
    list_of_companies.append('; '.join(mylist))
dict_Affiliation = {"lang_id": unique_Affiliation_lang_ids,
                    "Companies": list_of_companies}
df_Affiliation = pd.DataFrame(dict_Affiliation)

# fetch all from the 'succession' table
res = dbsession.query(Succession).all()
predecessor_ids = []
successor_ids = []
for row in res:
    predecessor_ids.append(row.predecessor)
    successor_ids.append(row.successor)

# create corresponding list of names for predecessor_ids
predecessor_names = []
for predecessor_id in predecessor_ids:
    for i in range(len(Language_lang_ids)):
        if predecessor_id == Language_lang_ids[i]:
            predecessor_names.append(Language_names[i])

# create corresponding list of names for successor_ids
successor_names = []
for successor_id in successor_ids:
    for i in range(len(Language_lang_ids)):
        if successor_id == Language_lang_ids[i]:
            successor_names.append(Language_names[i])

# create dataframe with strings of semicolon-separated successors
unique_predecessor_ids = list(set(predecessor_ids))
list_of_successors = []
for predecessor_id in unique_predecessor_ids:
    mylist = []
    for i in range(len(predecessor_ids)):
        if predecessor_id == predecessor_ids[i]:
            mylist.append(successor_names[i])
    list_of_successors.append(';'.join(mylist))
dict_successor = {"lang_id": unique_predecessor_ids,
                  "Successors": list_of_successors}
df_successor = pd.DataFrame(dict_successor)

# create dataframe with strings of semicolon-separated predecessors
unique_successor_ids = list(set(successor_ids))
list_of_predecessors = []
for successor_id in unique_successor_ids:
    mylist = []
    for i in range(len(successor_ids)):
        if successor_id == successor_ids[i]:
            mylist.append(predecessor_names[i])
    list_of_predecessors.append(';'.join(mylist))
dict_predecessor = {"lang_id": unique_successor_ids,
                    "Predecessors": list_of_predecessors}
df_predecessor = pd.DataFrame(dict_predecessor)

# combine all data frames
df_final = pd.merge(df_Language, df_Teams, how='left')
df_final = pd.merge(df_final, df_Affiliation, how='left')
df_final = pd.merge(df_final, df_predecessor, how='left')
df_final = pd.merge(df_final, df_successor, how='left')
# rename "name" column for better display on the web page
df_final.rename(columns={'Name': 'Language'}, inplace=True)


# %% Define the 'routes' (i.e. websites)
# --------------------------------------

# About page = serves also as the main landing page
@app.route('/')
@app.route('/about')
def about():
    """Create About page with some background information on the app."""
    return render_template('/about.html')


# Page with overview table of all programming languages
@app.route('/table')
def table():
    """Create page with a table showing all programming languages in the DB."""
    df = df_final[["Year", "Language", "Developers", "Companies",
                   "Predecessors", "Successors"]]
    df = df.sort_values(["Year", "Language"])
    return render_template('/table.html',
                           tables=[df.to_html(classes=("display dataTable"),
                                              index=False,
                                              na_rep="-",
                                              table_id="mytable")])


# Page with relationships between programming languages
@app.route('/relationships', methods=['GET', 'POST'])
def relationships():
    """Create page showing the relationship between programming languages."""

    # set default values (will be displayed if nothing is selected)
    language_name = "-"
    year = "-"
    developers = "-"
    companies = "-"
    predecessors = "-"
    successors = "-"

    # if page is called with a URL parameter:
    if "language" in request.args:
        selected_language = request.args.get('language')
        print("language is now: " + selected_language)
#        selected_language = unquote_plus(selected_language)
        selected_upper = selected_language.upper()
        Language_upper = [name.upper() for name in Language_names]

        if selected_upper in Language_upper:
            i = Language_upper.index(selected_upper)
            language_name = Language_names[i]
            year = Language_years[i]
            developers = df_final["Developers"].tolist()[i]
            companies = df_final["Companies"].tolist()[i]
            predecessors = df_final["Predecessors"].tolist()[i]
            successors = df_final["Successors"].tolist()[i]

            # show dash if there are now developers:
            if not isinstance(developers, str):
                developers = "-"

            # show dash if there are now companies:
            if not isinstance(companies, str):
                companies = "-"

            # create links for predecessor languages
            # make sure there is at least one element in predecessors:
            if isinstance(predecessors, str):
                # URL encode names so that they are equal to GET Method strings
                # Flask will automatically URL decode the URL parameter
                predecessors = predecessors.split(";")
                predecessor_urls = [quote_plus(name) for name in predecessors]
                predecessor_links = []
                for i in range(len(predecessors)):
                    predecessor_links.\
                        append("<a href=\"/relationships?language=" +
                               predecessor_urls[i] +
                               "\">" +
                               predecessors[i] + "</a>")
                predecessors = ", ".join(predecessor_links)
            else:
                predecessors = "-"

            # create links for successor languages
            # make sure there is at least one element in successors:
            if isinstance(successors, str):
                successors = successors.split(";")
                # URL encode names so that they are equal to GET Method strings
                # Flask will automatically URL decode the URL parameter
                successor_urls = [quote_plus(name) for name in successors]
                successor_links = []
                for i in range(len(successors)):
                    successor_links.\
                        append("<a href=\"/relationships?language=" +
                               successor_urls[i] +
                               "\">" +
                               successors[i] + "</a>")
                successors = ", ".join(successor_links)
            else:
                successors = "-"

        else:
            language_name = ('<span style="color:red">"' + selected_language +
                             '" does not exist in the database.</span>')

    return render_template('/relationships.html',
                           Language_names=Language_names,
                           language_name=language_name,
                           year=year,
                           developers=developers,
                           companies=companies,
                           predecessors=predecessors,
                           successors=successors)


# Page with charts
@app.route('/charts')
def charts():
    """Create page with interactive and static charts."""

    # plot 1: new languages per year (starting 1945)
    # the first plot will be implemented as an interactive plotly graph
    # see: https://plotly.com/python/
    # preparing the data
    df = df_final[df_final["Year"] >= 1945]
    new_languages_per_year = df["Year"].value_counts()
    # sort it so that the order corresponds to the order of years in the df
    new_languages_per_year = new_languages_per_year.sort_index()
    years = list(new_languages_per_year.index)
    number_of_new_languages = new_languages_per_year.values

    mydict = {"years": years,
              "new languages per year": number_of_new_languages,
              "token_error_y": [0] * len(years)}
    df_for_plotly = pd.DataFrame(mydict)

    # creating the plot
    fig = px.scatter(data_frame=df_for_plotly,
                     x="years",
                     y="new languages per year",
                     error_y="token_error_y",
                     error_y_minus="new languages per year",
                     custom_data=["years", "new languages per year"])
    # "custom_data" was added to suppress the error_y_minus in the hover label
    # Based on: https://stackoverflow.com/a/63185950/11826257
    fig.update_traces(
        hovertemplate="<br>".join([
            "Years: %{x}",
            "New Languages: %{customdata[1]}"
            ]))
    fig.update_layout(title="Frequency of language creations over the years")
    fig.update_layout(autosize=False, width=850, height=400)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # plot 2: most prolific developers
    # preparing the data
    unique_developers = list(set(Team_developers))
    number_of_developed_languages = []
    for developer in unique_developers:
        number_of_developed_languages.append(Team_developers.count(developer))
    # introduce newlines to developer names for better visualization
    unique_developers = ([dev.replace(' ', '\n') for dev in unique_developers])
    mydict = {"developer": unique_developers,
              "number_of_lang": number_of_developed_languages}
    df = pd.DataFrame(mydict)
    df = df.sort_values(by=['number_of_lang', 'developer'],
                        ascending=[False, True])
    df = df[df['number_of_lang'] >= 4]

    # creating the plot
    plt.style.use('seaborn-darkgrid')
    plt.bar(df['developer'],
            height=df['number_of_lang'],
            width=0.25,
            color="#99ceff",
            )
    plt.xticks(df['developer'])
    plt.ylabel('number of languages')
    plt.title('Most prolific developers')
    plt.savefig("programming_languages/myflaskapp/static/plots/developers.svg")
    plt.clf()

    # plot 3: most supportive companies
    # preparing the data
    unique_companies = list(set(Affiliation_companies))
    number_of_developed_languages = []
    for company in unique_companies:
        number_of_developed_languages.append(Affiliation_companies.
                                             count(company))
    mydict = {"company": unique_companies,
              "number_of_lang": number_of_developed_languages}
    df = pd.DataFrame(mydict)
    df = df.sort_values(by=['number_of_lang', 'company'],
                        ascending=[False, True])
    df = df[df['number_of_lang'] >= 4]
    # shorten one long name for better visualization
    df["company"].replace('Borland Software Corporation', 'Borland',
                          inplace=True)

    # creating the plot
    plt.bar(df['company'],
            height=df['number_of_lang'],
            width=0.25,
            color="#99ceff",
            )
    plt.xticks(df['company'], rotation=45)
    plt.ylabel('number of languages')
    plt.title('Most supportive companies')
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.savefig("programming_languages/myflaskapp/static/plots/companies.svg")
    plt.clf()

    # plot 4: most influencial languages
    # preparing the data
    unique_predecessors = list(set(predecessor_names))
    number_of_successor_languages = []
    for predecessor in unique_predecessors:
        number_of_successor_languages.append(predecessor_names.
                                             count(predecessor))
    mydict = {"predecessor": unique_predecessors,
              "number_of_lang": number_of_successor_languages}
    df = pd.DataFrame(mydict)
    df = df.sort_values(by=['number_of_lang', 'predecessor'],
                        ascending=[False, True])
    df = df[df['number_of_lang'] >= 10]
    # cutting the names at the first space or dash for better graphic display
    names = df['predecessor'].tolist()
    names = [name.split(" ")[0] for name in names]
    names = [name.split("-")[0] for name in names]

    # creating the plot
    plt.bar(names,
            height=df['number_of_lang'],
            width=0.25,
            color="#99ceff",
            )
    plt.xticks(names, rotation=45)
    plt.ylabel('number of languages')
    plt.title('Most influential languages')
    plt.savefig("programming_languages/myflaskapp/static/plots/" +
                "influencers.svg")
    plt.clf()

    # plot 5: languages with highest number of cited influences
    # preparing the data
    unique_successors = list(set(successor_names))
    number_of_predecessor_languages = []
    for successor in unique_successors:
        number_of_predecessor_languages.append(successor_names.
                                               count(successor))
    mydict = {"successor": unique_successors,
              "number_of_lang": number_of_predecessor_languages}
    df = pd.DataFrame(mydict)
    df = df.sort_values(by=['number_of_lang', 'successor'],
                        ascending=[False, True])
    df = df[df['number_of_lang'] >= 5]

    # creating the plot
    plt.bar(df["successor"],
            height=df['number_of_lang'],
            width=0.25,
            color="#99ceff",
            )
    plt.xticks(df["successor"], rotation=45)
    plt.ylabel('number of languages')
    plt.title('Languages with highest numbers of influencers')
    plt.savefig("programming_languages/myflaskapp/static/plots/followers.svg")
    plt.clf()

    return render_template('/charts.html',
                           graphJSON=graphJSON)
