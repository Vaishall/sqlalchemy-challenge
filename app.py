from flask import Flask, jsonify
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
app = Flask(__name__)

@app.route("/")
def home():
	return "Possible routes:<br>/api/v1.0/precipitation<br>/api/v1.0/stations<br>/api/v1.0/tobs<br>/api/v1.0/STARTDATE<br>/api/v1.0/STARTDATE/ENDDATE<br><br>Format dates as YYYY-MM-DD"


@app.route("/api/v1.0/precipitation")
def prcp():
	latest = dt.date.fromisoformat(session.query(Measurement).order_by(desc(Measurement.date)).first().date)
	earliest = latest-dt.timedelta(days=365)
	prcp_data = session.query(Measurement.date, Measurement.prcp).filter(earliest<Measurement.date)
	prcp_df = pd.read_sql(prcp_data.statement, session.bind)
	prcp_df['date']=pd.to_datetime(prcp_df.date)
	prcp_df.set_index('date', inplace=True)
	prcp_df.sort_index(inplace=True)

	#now we convert to dictionary
	prcp_df.index = prcp_df.index.astype('str')
	return jsonify(prcp_df.to_dict())

@app.route("/api/v1.0/stations")
def stations():
	#we query for stations
	stations = session.query(Measurement.station).group_by(Measurement.station)
	stations_df = prcp_df = pd.read_sql(stations.statement, session.bind)
	return jsonify(stations_df.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
	#query for temperature data
	latest = dt.date.fromisoformat(session.query(Measurement).order_by(desc(Measurement.date)).first().date)
	earliest = latest-dt.timedelta(days=365)
	tobs_data = session.query(Measurement.date, Measurement.tobs).filter(earliest<Measurement.date)
	tobs_df = pd.read_sql(tobs_data.statement, session.bind)
	tobs_df['date']=pd.to_datetime(tobs_df.date)
	tobs_df.set_index('date', inplace=True)
	tobs_df.sort_index(inplace=True)

	#now we convert to dictionary
	tobs_df.index = tobs_df.index.astype('str')
	return jsonify(tobs_df.to_dict())

@app.route("/api/v1.0/<start>")
def start_metrics(start):
	date_list = session.query(Measurement.date)
	date_df = pd.read_sql(date_list.statement, session.bind)
	date_dict = date_df.to_dict()
	for date in date_dict["date"].values():
		if date == start:
			return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        		filter(Measurement.date >= start).all())
	return jsonify({"error":"date not found"}),404

@app.route("/api/v1.0/<start>/<end>")
def start_end_metrics(start,end):
	found_start = False
	found_end = False
	if start > end:
		return "Dates in wrong order"
	date_list = session.query(Measurement.date)
	date_df = pd.read_sql(date_list.statement, session.bind)
	date_dict = date_df.to_dict()
	for date in date_dict["date"].values():
		if date == start:
			found_start = True
			if (found_start == True) and (found_end == True):
				return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        			filter(Measurement.date >= start).filter(Measurement.date <= end).all())
		if date == end:
			found_end = True
			if (found_start == True) and (found_end == True):
				return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        			filter(Measurement.date >= start).filter(Measurement.date <= end).all())
	return jsonify({"error":"date not found"}),404


if __name__ == "__main__":
    app.run(debug=True)