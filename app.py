import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurements = Base.classes.measurement
Stations = Base.classes.station

app = Flask(__name__)

def split(word):
    return [char for char in word]

@app.route("/")
def welcome():
    return (
    f"Welcome to Jacob Avchen's Weather API!<br/>"
    f"Use extensions '/api/v1.0/precipitation', '/api/v1.0/stations', '/api/v1.0/tobs' for info!<br/>"
    f"Or use /api/v1.0/YYYY-mm-dd or /api/v1.0/YYYY-mm-dd/YYYY-mm-dd to receive data about temperatures after the first date or between the two dates!")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = (dt.datetime.strptime(last_date[0], '%Y-%m-%d')-dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= last_year).order_by(Measurements.date.asc())

    session.close()

    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Stations.station, Stations.name).all()

    session.close()

    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["id"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date_a = session.query(Measurements.date).filter(Measurements.station == "USC00519281").order_by(Measurements.date.desc()).first()
    last_year_a = (dt.datetime.strptime(last_date_a[0], '%Y-%m-%d')-dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results = session.query(Measurements.date, Measurements.tobs).\
                      filter(Measurements.date >= last_year_a, Measurements.station == "USC00519281").\
                      order_by(Measurements.date.asc())

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def startonly(start):
    
    startlist = split(start)

    for c in startlist:
        if c == "-":
            startlist.remove("-")

    startlist.insert(4, "-")
    startlist.insert(7, "-")

    startstring = ''.join(map(str, startlist))

    session = Session(engine)

    results = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).\
                      filter(Measurements.date >= startstring)

    start_dict = {"min":results[0][0],
                  "max":results[0][1],
                  "avg":results[0][2]}

    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):

    startlist = split(start)
    endlist = split(end)

    for c in startlist:
        if c == "-":
            startlist.remove("-")

    for c in endlist:
        if c == "-":
            endlist.remove("-")

    startlist.insert(4, "-")
    startlist.insert(7, "-")
    endlist.insert(4, "-")
    endlist.insert(7, "-")

    startstring = ''.join(map(str, startlist))
    endstring = ''.join(map(str, endlist))


    session = Session(engine)

    results = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).\
                      filter(Measurements.date >= startstring).filter(Measurements.date <= endstring)

    startend_dict = {"min":results[0][0],
                  "max":results[0][1],
                  "avg":results[0][2]}

    return jsonify(startend_dict)

if __name__ == '__main__':
    app.run(debug=True)