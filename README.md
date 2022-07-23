# Training Project: combining Flask with DataTables and plotly

This is a training project that explores how you can combine Python's Flask web framework with Python's Matplotlib and plotly libraries. This makes it possible to display fixed charts and interactive charts on websites. The application also integrates jQuery's DataTables plug-in to generate an interactive table.

The content of Wikipedia's *Timeline of programming languages* was used as an example data set:
https://en.wikipedia.org/wiki/Timeline_of_programming_languages

![from_wiki_to_flask](https://github.com/staehlo/flask_test_project/blob/main/graphic_for_readme_from_wiki_to_flask.jpg)

The finalized application can be viewed at [rahace.pythonanywhere.com](http://rahace.pythonanywhere.com/).


## Technologies

Necessary python libraries for running the app locally:

* Flask==1.1.2
* matplotlib==3.5.1
* pandas==1.2.4
* plotly==5.9.0
* SQLAlchemy==1.4.15

Used during the creation:

* sqlacodegen 2.3.0
* SQLite 3.34.1

Built-in libraries:  
(Files are in the relevant subfolders so that you can run the app without internet access)

* DataTables 1.12.1
* jQuery 1.8.16
* plotly javascript file 1.58.5


## How to download and run it
(Absolute beginner's guide)

You need to have git, python, and pip already installed.

1\. Open a Linux terminal or Windows command line shell and go to a folder where you wish to download the application to.


2\. Install the necessary python libraries listed above if you should not have them yet. For example, if you're missing Flask, you can enter:  
`pip install flask`

3\. Clone the repository to your computer by entering in your Linux terminal or Windows command line:  
`git clone https://github.com/staehlo/flask_test_project`  


4\. Change the working directory to the *flask_test_project* folder by typing:  
`cd flask_test_project`

5\. Run the app by typing:  
on Linux:
```
your_name@[your_path/flask_test_project]$export FLASK_APP=programming_languages.myflaskapp
your_name@[your_path/flask_test_project]$export FLASK_ENV=development
your_name@[your_path/flask_test_project]$flask run
```

on Windows:
```
C:[your_path\flask_test_project]>set flask_app=programming_languages.myflaskapp
C:[your_path\flask_test_project]>set flask_env=development
C:[your_path\flask_test_project]>flask run
```

N.B. The *flask_env=development* part will run the app in development mode so that you can see error messages if anything goes wrong. You can skip this command if you don't want that.

6\. Open a web browser and type in the address bar:  
`http://localhost:5000/`

You should see the app now.


## A word about the development of the app

### Data retrieval
The content of all the tables from Wikipedia's *Timeline of programming languages* was collected by simple copy & pasting to Excel. This was done in June 2022. Any later editing of Wikipedia's article will not show up in the application.

### Data clean-up and rearrangement
The Wikipedia article contained various naming inconsistencies between the *predecessor(s)* and the *Name* columns. Some developers and companies appeared also in different spelling variants or with different details. These inconsistencies were solved by manually going through all the entries.
Next, a unique identifier was assigned to each programming language. These identifiers are based on the language names but do not contain any non-alphanumeric characters or any spaces. For example, *C++* was converted to *C_plus_plus*.

### Data base design
After carefully reviewing the relationships between the different data points, an entity-relationship model was designed. The *succession*, *team*, and *affiliation* tables are necessary to resolve many-to-many relationships. The *developer* and the *company* tables are only required to make sure that the *team* and the *affiliation* tables name the developers and companies consistently.
![entity_relationship_diagram](https://github.com/staehlo/flask_test_project/blob/main/graphic_for_readme_Entity_Relationship_Diagram.jpg)
*SQLite 3.34.1* was used to implement the model and to fill the tables.
*Sqlacodegen 2.3.0* was then used to create a *models.py* file with object-relational mapping classes for the database tables.

### Application design
*Python 3.9.5* and the *Flask 1.1.2* library were used to create the web application. The websites are rendered based on the html files in the template folder. The *SQLAlchemy 1.4.15* library connects the application script to the SQLite database file via the *models.py* file. *Pandas 1.2.4* is used to handle the data in the form of DataFrame objects and to automatically create an html table. The html table is rendered into an interactive table by jQuery's *DataTables 1.12.1* plug-in. *Matplotlib 3.5.1* is used to generate the non-interactive charts. The plots are saved to the static folder of the application before they are served to the website. *Plotly 5.9.0* is used to create an interactive plot in the python script. The chart is transmitted to the website via a JSON object which is then rendered by *Plotly javascript 1.58.5*.
