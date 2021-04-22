from sqlalchemy import *

engine = create_engine("sqlite:///dbfile.sqlite")
connection = engine.connect()
metadata = MetaData()
cities_ = ["Paris", "London", "Saint Petersburg", "Barcelona", "Berlin", "Madrid",
           "Kyiv", "Birmingham", "Rome", "Manchester", "Minsk", "Bucharest", "Vienna",
           "Hamburg", "Warsaw", "Budapest", "Newcastle", "Munich", "Belgrade", "Milan",
           "Sofia", "Prague", "Sevilla", "Dublin", "Copenhagen", "Cologne", "Amsterdam",
           "Odesa", "Rotterdam", "Stockholm", "Zagreb", "Riga", "Oslo", "Athens", "Helsinki",
           "Skopje", "Dnipro", "Glasgow", "Naples", "Turin", "Marseille", "Liverpool", "Portsmouth",
           "Valencia", "Nottingham", "Krakow", "Frankfurt", "Bristol", "Lviv", "Bremen", "Grenoble",
           "Lodz", "Sheffield", "Palermo", "Zaragoza", "Wroclaw", "Nantes", "Stuttgart", "Dusseldorf", "Gothenburg"]
statistics = Table('statistics', metadata,
                Column('user_id', Integer, primary_key=True),
                Column('right_answers', Integer),
                Column('wrong_answers', Integer)
                  )

statistics.create(engine)