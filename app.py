import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"<h2>Welcome to my climate analysis page for Hawaii!</h2>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Last 12 months of precipitation data</a><br/>"
        f"<a href='/api/v1.0/stations'>List of station names</a><br/>"
        f"<a href='/api/v1.0/tobs'>Last 12 months of temperature data from the most active station</a><br/>"
        f"Temperature statistics (min, max, average):<br/>"
        f"<ul><li><a href='/api/v1.0/08232016'>Based on start date</a> (format MMDDYYYY) to most recent</li><br/>"
        f"<li><a href='/api/v1.0/08232016/08232017'>Based on start and end dates</a> (format MMDDYYYY/MMDDYYYY; start/end)</li></ul><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Design a query to retrieve the last 12 months of precipitation data and display the JSON representation of results (dictionary)."""
     
    # Starting from the most recent data point in the database. 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()
    # Calculate the date one year from the last date in data set.
    first_date = str(dt.date.fromisoformat(last_date[0][0])-dt.timedelta(days=365))

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= first_date).\
        order_by(Measurement.date).all()
    
    session.close()

    # Create list of dictionaries from the results using 'date' as the key and 'prcp' as the value
    prcp_year_data = {date:prcp for date, prcp in results}

    return jsonify(prcp_year_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations
    results = session.query(Station.station).order_by(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(stations=all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Query the dates and temperature observations of the most-active station for the previous year of data"""

    # Query the most active station in current dataset (USC00519281)
    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Latest date of temperature observation for most active station
    last_date = session.query(Measurement.date).\
        filter(Measurement.station == most_active).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date
    first_date = str(dt.date.fromisoformat(last_date[0])-dt.timedelta(days=365))
    
    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.tobs).\
    filter(Measurement.station==most_active, Measurement.date >= first_date).\
    order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples to normal list
    tobs_year_data = list(np.ravel(results))

    return jsonify(temps=tobs_year_data)

@app.route("/api/v1.0/<start>")
def q_start(start):
    # Convert string start date MMDDYYYY to ISO format
    obj_date = dt.datetime.strptime(start, '%m%d%Y')
    start_date = dt.date.isoformat(obj_date)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range"""
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    temp_stats = {'tmin':results[0][0],'tmax':results[0][1],'tavg':round(results[0][2],2)}
    
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def q_start_end(start, end):
    # Convert string dates MMDDYYYY to ISO format
    obj_sdate = dt.datetime.strptime(start, '%m%d%Y')
    obj_edate = dt.datetime.strptime(end, '%m%d%Y')
    start_date = dt.date.isoformat(obj_sdate)
    end_date = dt.date.isoformat(obj_edate)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range"""
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()
    
    temp_stats = {'tmin':results[0][0],'tmax':results[0][1],'tavg':round(results[0][2],2)}
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
