# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end_date><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Precipitation data for the last year in the database"""
    # Query all precipitation
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    recent_date_first = recent_date.first()
    recent_date_first
    most_recent_date = dt.datetime.strptime(recent_date_first[0], '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=366)

    results = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    precip_year = []
    for (date, prcp) in results:
        precip_dict = {
            date: prcp,
        }
        precip_year.append(precip_dict)

    return jsonify(precip_year)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Turning all station data into jsonified form"""
    # Query all stations
    station_data = session.query(Station.station)
    station_data_list = []
    for station in station_data:
        station_data_list.append(station.station)

    session.close()

 

    return jsonify(station_data_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature obersvations of th emost-active station for the previous year of data"""
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).\
        filter(Measurement.station == 'USC00519281').all()

    date = date[0][0]
    active_station = dt.datetime.strptime(date, '%Y-%m-%d')
    one_year_ago = active_station - dt.timedelta(days=366)

# Get Data
    temp_data = session.query(Measurement.tobs).\
    filter(Measurement.date >= one_year_ago).\
    filter(Measurement.station == 'USC00519281').\
    all()
    
    session.close()

    temp_data_list = [temp[0] for temp in temp_data]
 
    return jsonify(temp_data_list)

@app.route("/api/v1.0/<start>/")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations for the specified date range.
    Return a JSON list of minimum, average, and maximum temperature observations."""

    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start date format."})


    # Query for the specified date range
    temperature_data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()

    session.close()

   
    tmin, tavg, tmax = temperature_data[0]
    result_dict = {
        "start_date": start_date.strftime('%Y-%m-%d'),
            "Min": tmin,
            "Avg": tavg,
            "Max": tmax
    }
    return jsonify(result_dict)

@app.route("/api/v1.0/<start>/<end_date>")
def end(start, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations for the specified date range.
    Return a JSON list of minimum, average, and maximum temperature observations."""

    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start date format."})


    try:
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid end date format."})


    # Query for the specified date range
    temperature_data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

   
    tmin, tavg, tmax = temperature_data[0]
    result_dict = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
            "Min": tmin,
            "Avg": tavg,
            "Max": tmax
    }

    return jsonify(result_dict)




if __name__ == '__main__':
    app.run(debug=True)
