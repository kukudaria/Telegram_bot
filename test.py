import requests
from geopy.geocoders import Nominatim

loc = 'Tokyo'
geolocator = Nominatim(user_agent="my_request")
location = geolocator.geocode(loc)
#map_request = 'http://static-maps.yandex.ru/1.x/?ll=' + str(location.longitude) + ',' + str(location.latitude) + '&spn=5,5&l=sat'
map_request = 'https://static-maps.yandex.ru/1.x/?l=map&pt=' + str(location.longitude) + ',' + str(location.latitude)
response = requests.get(map_request)

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)



#printing address and coordinates
print(location.address)
print((location.latitude, location.longitude))