# Import the dependencies

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify, request, render_template
import datetime as dt
import numpy as np
from flask import Flask, jsonify
import pandas as pd
import os

# Database Setup

engine = create_engine(
    "sqlite:///Resources/hawaii.sqlite",
    connect_args={"check_same_thread": False},
    echo=True,
)

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# List all the flask Routes
#################################################
@app.route("/")
def Welcome():
    return (
        f"<h1><center>Welcome to the Climate App for Honululu!</center></h1>"
        f"<div align = center>"
        f'<img src="https://www.touristsecrets.com/wp-content/uploads/2019/05/feature-1-1160x653.jpg" width=1200 height=200 alt= "Honululu">'
        f"</div>"
        f"<h3>If you've decided to treat yourself with a holiday vacation in Honolulu,"
        f" Hawaii then this App will help with your trip planning"
        f"<br/>"
        f" This app will provide you with climate analysis in the area</h3>"
        f"<br/>"
        f"All the routes are listed below:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation (To list prior year rain totals from all stations)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/precipitation _black> Click here for Precipitaion info</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/stations (To list the Stations Info)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/stations _black> Click here for Stations details</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/tobs (To list prior year temperatures from all stations)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/tobs _black> Click here for Temperature details</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/start (When given the start date, calculates the min/avg/max temperature for all dates greater than and equal to the start date)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/start _black> Click here and enter start date in fomrat YYYY-MM-DD</a>"
        f"<br/>"
        f"<b>Please replace start in url with the start_date you want to enter</b>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/start/end (When given the start and the end date (YYYY-MM-DD), calculate the min/avg/max temperature for dates between the start and end date inclusive)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/start/end _black> Click here and enter start and end date in format YYYY-MM-DD</a>"
        f"<br/>"
        f"<b>Please replace start_date/end_date in the url in format yyyy-mm-dd/yyyy-mm-dd</b>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
    )


#########################################################################################
# Route #1(/api/v1.0/precipitation)
#########################################################################################


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return a list of precipitaion for prior year
    #    # Query for the dates and precipitation observations from the last year.
    #    # Convert the query results to a Dictionary and return the json representation of the dictionary.
    max_date = (
        session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    )
    max_date = max_date[0]

    last_year = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_date = (
        session.query(Measurements.date, Measurements.prcp)
        .filter(Measurements.date >= last_year)
        .all()
    )
    # Convert list of tuples into normal list
    precipitation_dict = dict(precipitation_date)

    return jsonify(precipitation_dict)


@app.route("/rainfall")
def rainfall():
    max_date = (
        session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    )
    max_date = max_date[0]

    last_year = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_date = (
        session.query(Measurements.date, Measurements.prcp)
        .filter(Measurements.date >= last_year)
        .all()
    )
    # Convert list of tuples into a dictionary
    precipitation_dict = dict(precipitation_date)

    # return render_template("rainfall.html", target=precipitation_dict)
    return jsonify(precipitation_dict)


#########################################################################################
# Route #2(/api/v1.0/stations)
#########################################################################################
@app.route("/api/v1.0/stations")
def get_stations():
    active_stations = session.query(Stations.station, Stations.name).all()
    # active_stations = session.query(Measurements.station, func.count(Measurements.station)).group_by(Measurements.station).order_by(func.count(Measurements.station).desc()).all()
    active_stations_list = [(i, j) for i, j in active_stations]
    stations_dict = dict(active_stations_list)
    return jsonify(stations_dict)
    # return render_template("station.html", target=stations_dict)


#########################################################################################
# Route #3(/api/v1.0/tobs)
#########################################################################################


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    #    * Query for the dates and temperature observations from the last year.
    #           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    #           * Return the json representation of your dictionary.
    max_date = (
        session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    )
    max_date = max_date[0]
    last_year = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = (
        session.query(Measurements.date, Measurements.tobs, Measurements.station)
        .filter(Measurements.date >= last_year)
        .order_by(Measurements.date)
        .all()
    )

    # Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        row["station"] = result[2]
        temperature_totals.append(row)
    return jsonify(temperature_totals)


#########################################################################################
# Route #2(/api/v1.0/start)
#########################################################################################


@app.route("/api/v1.0/<start>")
def temp_stats_start_date(start):

    results = (
        session.query(
            func.min(Measurements.tobs).label("min"),
            func.avg(Measurements.tobs).label("avg"),
            func.max(Measurements.tobs).label("max"),
        )
        .filter(Measurements.date >= start)
        .group_by(Measurements.date)
        .all()
    )

    stats_data = []

    for r in results:
        stats_dict = {}
        # start_stats_dict['Start Date'] = start
        stats_dict["Min Temp"] = r.min
        stats_dict["Avg Temp"] = r.max
        stats_dict["Max Temp"] = r.avg
        stats_data.append(stats_dict)

    return jsonify(stats_data)


#########################################################################################
# Route #2(/api/v1.0/start/end)
#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end_date(start, end):

    results = (
        session.query(
            Measurements.date,
            func.min(Measurements.tobs).label("min"),
            func.avg(Measurements.tobs).label("avg"),
            func.max(Measurements.tobs).label("max"),
        )
        .filter(Measurements.date >= start)
        .filter(Measurements.date <= end)
        .group_by(Measurements.date)
        .all()
    )

    start_end_stats_data = []
    for r in results:
        start_end_stats_dict = {}
        start_end_stats_dict["Start Date"] = start
        start_end_stats_dict["End Date"] = end
        start_end_stats_dict["Date"] = r.date
        start_end_stats_dict["Min Temp"] = r.min
        start_end_stats_dict["Avg Temp"] = r.avg
        start_end_stats_dict["Max Temp"] = r.max
        start_end_stats_data.append(start_end_stats_dict)

    return jsonify(start_end_stats_data)


#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)
