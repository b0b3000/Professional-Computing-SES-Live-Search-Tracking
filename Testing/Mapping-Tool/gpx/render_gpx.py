import gpxpy
import pandas as pd
import folium


# Proof of Concept - adapted from https://towardsdatascience.com/build-interactive-gps-activity-maps-from-gpx-files-using-folium-cf9eebba1fe7
def process_gpx_to_df(file_name):
    gpx = gpxpy.parse(open(file_name)) 
    
    # build dataframe
    track = gpx.tracks[0]
    segment = track.segments[0]

    data = []
    for point_idx, point in enumerate(segment.points):
        data.append([point.longitude, point.latitude, point.elevation, point.time, segment.get_speed(point_idx)])
    columns = ['Longitude', 'Latitude', 'Altitude', 'Time', 'Speed']
    gpx_df = pd.DataFrame(data, columns=columns)
    
    # construct tuples for line
    points = []
    for track in gpx.tracks:
        for segment in track.segments: 
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
    
    return gpx_df, points

df, points = process_gpx_to_df('test.gpx')

# create map
mymap = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=6, tiles=None)
folium.TileLayer('openstreetmap', name='OpenStreet Map').add_to(mymap)

# polyline to the map
folium.PolyLine(points, color='red', weight=4.5, opacity=.5).add_to(mymap)

# save map
mymap.save("map.html")
