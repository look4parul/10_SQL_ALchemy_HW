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
        f"<head>"
        f"<title>Climate Anlaysis App for Honululu</title>"
        f"</head>"
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
        f"/api/v1.0/precipitation (To list prior year rain totals)<br/>"
        f"<a href= http://127.0.0.1:5000/precipitation target = _blank> Click here for Precipitaion info</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/stations (To list the Stations Info)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/stations target = _blank> Click here for Stations details</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/tobs (To list prior year temperature observations from all stations)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/tobs target = _blank> Click here for Temperature details</a>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/start (When given the start date, calculates the min/avg/max temperature for all dates greater than and equal to the start date)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/start target = _blank> Click here and enter start date</a>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/start/end (When given the start and the end date (YYYY-MM-DD), calculate the min/avg/max temperature for dates between the start and end date inclusive)<br/>"
        f"<a href= http://127.0.0.1:5000/api/v1.0/start/end target = _blank> Click here and enter start and end date</a>"
        # f"<b>Please replace start_date/end_date in the url in format yyyy-mm-dd/yyyy-mm-dd for your trip dates</b>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
        f"<br/>"
    )


#############################################################################################
# Route #1(/api/v1.0/precipitation)
# Design a query to retrieve the last 12 months of precipitation data
#############################################################################################


@app.route("/precipitation")
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

    return render_template("rainfall.html", target=precipitation_date)


#########################################################################################
# Route #2(/api/v1.0/stations)
# Return a list of stations from the dataset.
#########################################################################################
@app.route("/api/v1.0/stations")
def get_stations():
    active_stations = session.query(Stations.station, Stations.name).all()
    active_stations_list = [(i, j) for i, j in active_stations]
    return render_template("station.html", target=active_stations_list)


#########################################################################################
# Route #3(/api/v1.0/tobs)
# Query for the dates and temperature observations from a year from the last data point.
# Return a list of Temperature Observations (tobs) for the previous year
#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Return a list of temperatures for prior year
    # Query for the dates and temperature observations from the last year.

    max_date = (
        session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    )
    max_date = max_date[0]
    last_year = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    temperature = (
        session.query(Measurements.date, Measurements.tobs, Measurements.station)
        .filter(Measurements.date >= last_year)
        .order_by(Measurements.date)
        .all()
    )
    return render_template("tobs.html", target=temperature)


#########################################################################################
# Route #4(/api/v1.0/<start>)
# Return a list of the minimum temperature, the average temperature, and the max temperature
#  for all dates greater than and equal to the given start date.
#########################################################################################


@app.route("/api/v1.0/<start>")
def temp_stats_start_date(start):

    if start == "start":
        return render_template("input.html")

    results = (
        session.query(
            func.min(Measurements.tobs).label("min"),
            func.avg(Measurements.tobs).label("avg"),
            func.max(Measurements.tobs).label("max"),
            Measurements.date,
        )
        .filter(Measurements.date >= start)
        .group_by(Measurements.date)
        .all()
    )

    returnHTML = "<html><body><h4>Temp Details for all the dates including start date</h4><table border='1'><thead><th>Date</th><th>Min</th><th>Max</th><th>Avg</th></thead><tbody>"

    for r in results:
        returnHTML += "<tr>"
        returnHTML += "<td>" + r.date + "</td>"
        returnHTML += "<td>" + str(r.min) + "</td>"
        returnHTML += "<td>" + str(r.max) + "</td>"
        returnHTML += "<td>" + str(r.avg) + "</td>"

        returnHTML += "</tr>"

    returnHTML = returnHTML + "</tbody></table></body></html>"
    return returnHTML


#########################################################################################
# Route #5(/api/v1.0/<start>/<end>)
# Return a list of the minimum temperature, the average temperature, and the max temperature
#  for dates between the given start and end date inclusive.
#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end_date(start, end):

    if start == "start" or end == "end":
        return render_template("input.html")

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

    returnHTML = "<html><body><h4>Temp Details for all the dates from start date to end date</h4><table border='1'><thead><th>Date</th><th>Min</th><th>Max</th><th>Avg</th></thead><tbody>"

    for r in results:
        returnHTML += "<tr>"
        returnHTML += "<td>" + r.date + "</td>"
        returnHTML += "<td>" + str(r.min) + "</td>"
        returnHTML += "<td>" + str(r.max) + "</td>"
        returnHTML += "<td>" + str(r.avg) + "</td>"

        returnHTML += "</tr>"

    returnHTML = returnHTML + "</tbody></table></body></html>"
    return returnHTML


#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)
