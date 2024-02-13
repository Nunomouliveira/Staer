import folium
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Airplane.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class AircraftInfo(db.Model):
    __tablename__ = 'AircraftInfo'
    id = db.Column(db.Integer, primary_key=True)
    icao24 = db.Column(db.String(24))
    callsign = db.Column(db.String(64))
    origin_country = db.Column(db.String(64))
    time_position = db.Column(db.Integer)
    last_contact = db.Column(db.Integer)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    on_ground = db.Column(db.Integer)
    velocity = db.Column(db.Float)
    true_track = db.Column(db.Float)
    vertical_rate = db.Column(db.Float)
    sensors = db.Column(db.String(255))
    baro_altitude = db.Column(db.Float)
    squawk = db.Column(db.String(8))
    spi = db.Column(db.Integer)
    position_source = db.Column(db.Integer)

def create_database():
    db.create_all()

def query_aircraft_data(selected_country, min_velocity):
    query = AircraftInfo.query
    if selected_country:
        query = query.filter_by(origin_country=selected_country)
    if min_velocity is not None:
        query = query.filter(AircraftInfo.velocity >= min_velocity)

    return query.all()

@app.before_request
def before_request():
    create_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_country = request.form.get('country') if request.method == 'POST' else None
    min_velocity = float(request.form.get('velocity')) if request.form.get('velocity') else None

    m = folium.Map(location=[0, 0], zoom_start=2)

    aircraft_data = query_aircraft_data(selected_country, min_velocity)

    for aircraft in aircraft_data:
        if aircraft.latitude is not None and aircraft.longitude is not None:
            popup_text = f"Call Sign: {aircraft.callsign}<br>Origin Country: {aircraft.origin_country}<br>Velocity: {aircraft.velocity}"
            folium.Marker([aircraft.latitude, aircraft.longitude], popup=popup_text).add_to(m)

    return render_template('index.html', map=m._repr_html_())

if __name__ == '__main__':
    app.run(debug=True)
