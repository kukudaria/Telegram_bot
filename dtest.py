from sqlalchemy import *

engine = create_engine("sqlite:///dbfile.sqlite")
connection = engine.connect()
metadata = MetaData()
cities_ = ["Paris","London","Saint Petersburg","Barcelona","Berlin","Madrid",
           "Kyiv","Birmingham","Rome","Manchester","Minsk","Bucharest","Vienna",
           "Hamburg","Warsaw","Budapest","Newcastle","Munich","Belgrade","Milan",
           "Sofia","Prague","Sevilla","Dublin","Copenhagen","Cologne","Amsterdam",
           "Odesa","Rotterdam","Stockholm","Zagreb","Riga","Oslo","Athens","Helsinki",
           "Skopje","Dnipro","Glasgow","Naples","Turin","Marseille","Liverpool","Portsmouth",
           "Valencia","Nottingham","Krakow","Frankfurt","Bristol","Lviv","Bremen","Grenoble",
           "Lodz","Sheffield","Palermo","Zaragoza","Wroclaw","Nantes","Stuttgart","Dusseldorf","Gothenburg"]
cities = Table('cities', metadata,
        Column('city_id', Integer, primary_key=True),
        Column('city', String(16), nullable=False)
    )
for i in range(len(cities_)):
    connection.execute(cities.insert(), {"city_id": i, "city": str(cities_[i])})
