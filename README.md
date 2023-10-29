# sqlalchemy-challenge
Using SQLAlchemy to query data then design a Flask API to mimic those queries

by Jason Estrada

The first part of this project was to analyze and explore climate data in Hawaii in Jupyter notebook
- SQLAlchemy was used to connect to a SQLite database (file) and perform queries
- pandas and matplotlib was used to visualize precipitation and temperature data

The second part of this project was to create a climate app (Flask API) to connect to the database, mimic these queries, and display the results in JSON format.
- A simple home page was created to list the available pages (routes)
- Static routes created were for precipitation data, station names, and temperature observations (tobs)
- Dynamic routes were created to show temperature statistics (average, minimum, and maximum) given a user-provided start date or user-provided start/end dates