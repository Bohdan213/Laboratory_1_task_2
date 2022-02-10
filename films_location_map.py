"""
Module for finding 10 nearest places with films locations
"""

import argparse
import folium
import math
import sys
from geopy.geocoders import ArcGIS, Nominatim

arcgis = ArcGIS(timeout=100)
nominatim = Nominatim(timeout=100, user_agent='http')
geocoders = [arcgis, nominatim]

greatest_studios = [
    ('20th Century Studios', (34.0536909, -118.242766)),
    ('Columbia Pictures', (34.0646909, -118.242866)),
    ('DreamWorks Animation', (34.1469416, -118.2478471)),
    ('Paramount Pictures Studios', (34.083583, -118.32188153846154)),
    ('Sony Pictures', (34.0211224, -118.396466)),
    ('Warner Bros. Pictures', (34.0980031, -118.329523)),
    ('EuropaCorp', (48.935773, 2.3580232)),
    ('Pixar', (37.8314089, -122.2865266)),
    ('Alexander Dovzhenko National Film Studio', (50.4500336, 30.5241361)),
    ('Odessa Film Studio', (46.4873195, 30.7392776))
]

def read_file(need_year: int, path: str):
    """
    function for reading dataset
    """
    flag = False
    films_set = set()
    with open(path, 'r') as file:
        for line in file:
            if flag and line[0] != '-':
                line = line[:-1]
                film_name = line.split('(')[0].strip(' ').strip('"').strip('#').strip('/')
                year = line.split('(')[1][:4]
                location = line.split(')')[1].strip('\t')
                location = location.split('(')[0].strip('\t')
                if '}' in line:
                    location = line.split('}')[1].strip('\t')
                    location = location.split('(')[0].strip('\t')
                try:
                    if need_year == int(year):
                        films_set.add((location, film_name))
                except:
                    1
            else:
                if line[0] == '=':
                    flag = True
    return films_set


def parse_args():
    """
    Parser optional and positional arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('year', help='film year')
    parser.add_argument('lat', help='coordinate 1')
    parser.add_argument('lon', help='coordinate 2')
    parser.add_argument('path', help='path to dataset')
    return parser.parse_args()


def length(lat_1, lon_1, lat_2, lon_2):
    """
    function for counting length between 2 places
    """
    answer = (2 * 6371 * math.asin(math.sqrt(
        math.sin((lat_2 - lat_1) / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin((lon_1 - lon_2) / 2) ** 2))))
    return answer


def geocode(adress):
    try:
        i = 0
        while i < len(geocoders):
            location = geocoders[i].geocode(adress)
            if location is not None:
                return location.latitude, location.longitude
            else:
                i += 1
    except:
        return [None, None]


def main():
    try:
        args = parse_args()
    except:
        raise SystemExit(f"Usage={sys.argv[0]} <argument> <argument> <argument> <argument>")

    films_set = read_file(int(args.year), args.path)
    nearest_places = []
    "Finding the 10 nearest film's "
    for film in films_set:
        try:
            coord = geocode(film[0])
            if coord[0] is not None:
                if len(nearest_places) < 10:
                    nearest_places.append(
                        (length(coord[0], coord[1], float(args.lat), float(args.lon)), film[1], coord))
                    if len(nearest_places) == 10:
                        nearest_places.sort(key=lambda x: x[0])
                else:
                    ln = length(coord[0], coord[1], float(args.lat), float(args.lon))
                    if nearest_places[9][0] > ln:
                        for i in range(len(nearest_places)):
                            if nearest_places[i][0] > ln:
                                nearest_places.remove(nearest_places[9])
                                nearest_places.insert(i, (ln, film[1], coord))
                                break
        except Exception:
            None
    map = folium.Map(tiles="Stamen Terrain")
    films_location_fg = folium.FeatureGroup(name="Films map")
    for i in nearest_places:
        films_location_fg.add_child(folium.Marker(location=[i[2][0], i[2][1]],
                                   popup=i[1],
                                   icon=folium.Icon(color='green')))

    map.add_child(films_location_fg)
    films_company_fg = folium.FeatureGroup(name='The greatest films studios')
    for i in greatest_studios:
        films_company_fg.add_child(folium.Marker(location=[i[1][0], i[1][1]],
                                         popup=i[0],
                                         icon=folium.Icon(color="red")))
    map.add_child(films_company_fg)
    map.add_child(folium.LayerControl())
    map.save('Films_map.html')

if __name__ == '__main__':
    main()
