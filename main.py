from flask import Flask,render_template,request
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from datetime import datetime
import requests

class Base(DeclarativeBase):
    pass
class day(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True)
    date_epoch = Column(Integer)
    city = Column(String)
    temp_min = Column(Float)
    temp_avg = Column(Float)
    temp_max = Column(Float)
    total_prep = Column(Float)
    sunrise_hour = Column(String)
    sunset_hour = Column(String)
    def __init__(self, json_day, city):
        self.date = datetime.fromtimestamp(json_day["date_epoch"])
        self.date_epoch = json_day["date_epoch"]
        self.city = city
        self.day = str(self.date.day)
        self.month = self.date.strftime('%b')
        json_day_temp = json_day["day"]
        self.temp_avg = json_day_temp["avgtemp_c"]
        self.temp_max = json_day_temp["maxtemp_c"]
        self.temp_min = json_day_temp["mintemp_c"]
        self.icon = "https:" + json_day_temp["condition"]["icon"]
        self.total_prep = json_day_temp["totalprecip_mm"]
        self.sunrise_hour = json_day["astro"]["sunrise"]
        self.sunset_hour = json_day["astro"]["sunset"]



PORT = "5000"
app = Flask(__name__)

#weather API key big secret
API = "58e464e707f242468b5224624242702"

engine = create_engine('sqlite:///weather.db')
if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)

@app.route("/weather",methods=["GET"])
def weather_get():
    return render_template("weather.html")


@app.route("/weather",methods=["POST"])
def weather_post():
    CITY = request.form["city"]
    url = "http://api.weatherapi.com/v1/forecast.json?key="+API+"&q="+CITY+"&days=3&aqi=no&alerts=no"
    req = requests.get(url)
    if req.status_code != 200:
        return render_template("error.html")
    day_list = []
    req_json = req.json()
    for i in req_json["forecast"]["forecastday"]:
        day_list.append(day(i, req_json["location"]["name"]))
    region = req_json["location"]["name"] + ", " + req_json["location"]["country"]
    Session = sessionmaker(bind=engine)
    session = Session()
    for x in day_list:
        exists = session.query(day).filter_by(date_epoch=x.date_epoch, city=x.city).first()
        if exists is None:
            session.add(x)
        else:
            exists = x
    session.commit()
    return render_template("table.html", forecast = day_list, location = region)



@app.route("/",methods=["GET"])
def index():
    return render_template("index.html", showdata=True)



@app.route("/database",methods=["GET"])
def databases():
    return render_template("database.html")



@app.route("/database",methods=["POST"])
def database_post():
    conn = sqlite3.connect('tests.db')
    cor = conn.cursor()
    exists = cor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons';").fetchone()
    if exists is None:
        setup()
    if request.form["action"] == "Generate report 1":
        data = cor.execute("select p.id,count(v.chosen_person),GROUP_CONCAT(v.quality),p.locatie from persons p left join votes v on p.id = v.chosen_person group by p.id order by p.locatie;").fetchall()
    elif request.form["action"] == "Generate report 2":
    #select p.locatie,count(v.chosen_person) from persons p left join votes v on p.id = v.chosen_person and v.valid=1 group by p.locatie;
    #with validation 
        data = cor.execute("select p.locatie,count(v.chosen_person) from persons p left join votes v on p.id = v.chosen_person group by p.locatie;").fetchall()
    conn.close()
    return render_template("reports.html", data = data)


def setup():
    conn = sqlite3.connect('tests.db')
    cor = conn.cursor()
    cor.execute("CREATE TABLE persons (ID VARCHAR(20) PRIMARY KEY,Status VARCHAR(10),First_Name VARCHAR(50),Last_Name VARCHAR(50),Email_Address VARCHAR(100),Locatie VARCHAR(50));")
    cor.execute("CREATE TABLE Votes (ID INT PRIMARY KEY,voting_date DATETIME,chosen_person VARCHAR(20),voter INT,message VARCHAR(100),valid BIT,quality VARCHAR(20));")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('00108901', 'Active', 'Person', 'One', 'person.one@gfk.com', 'Germany');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('00108941', 'Active', 'Person', 'Two', 'person.two@gfk.com', 'France');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('00199990', 'Inactive', 'Person', 'Three', 'person.three@gfk.com', 'Brazil');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('01100003', 'Active', 'Person', 'Four', 'person.four@gfk.com', 'Hong Kong');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('03400110', 'Active', 'Person', 'Five', 'person.five@gfk.com', 'Germany');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('03400360', 'Active', 'Person', 'Six', 'person.six@gfk.com', 'France');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('03402059', 'Inactive', 'Person', 'Seven', 'person.seven@gfk.com', 'Brazil');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('03400565', 'Active', 'Person', 'Eight', 'person.eight@gfk.com', 'Hong Kong');")
    cor.execute("INSERT INTO persons (ID, Status, First_Name, Last_Name, Email_Address, Locatie)VALUES ('03400436', 'Active', 'Person', 'Nine', 'person.nine@gfk.com', 'Hong Kong');")
    cor.execute("INSERT INTO Votes (ID, Voting_date, chosen_person, voter, message, valid, quality)VALUES (253, '2022-10-29 11:54:15', '03400110', 1, 'Vote 1', 1, 'entrepreneur');")
    cor.execute("INSERT INTO Votes (ID, Voting_date, chosen_person, voter, message, valid, quality)VALUES (254, '2022-10-29 11:55:22', '03400360', 1, 'Vote 2', 0, 'entrepreneur');")
    cor.execute("INSERT INTO Votes (ID, Voting_date, chosen_person, voter, message, valid, quality)VALUES (255, '2022-10-29 11:56:53', '03402059', 1, 'Vote 3', 1, 'partner');")
    cor.execute("INSERT INTO Votes (ID, Voting_date, chosen_person, voter, message, valid, quality)VALUES (256, '2022-10-29 11:58:23', '03400565', 1, 'Vote 4', 1, 'developer');")
    cor.execute("INSERT INTO Votes (ID, Voting_date, chosen_person, voter, message, valid, quality)VALUES (257, '2022-10-29 12:13:00', '03400436', 1, 'Vote 5', 1, 'developer');")
    conn.commit()
    conn.close()

@app.errorhandler(404)
def page_not_found(e):
    return render_template("info.html")

if __name__ == "__main__":
    app.run(debug=True, port = PORT)
