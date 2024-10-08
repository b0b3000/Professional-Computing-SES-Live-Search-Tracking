import gpxpy
import pandas as pd
import xml.etree.ElementTree as ET
import folium

def process_gpx_to_df(file_name):
    gpx = gpxpy.parse(open(file_name))
    # parse the raw XML to access extensions
    # (not ideal, but gpxpy doesn't seem to support parsing extensions)
    tree = ET.parse(file_name)
    root = tree.getroot()
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}

    # build dataframe
    track = gpx.tracks[0]
    segment = track.segments[0]

    data = []
    base_columns = ['Longitude', 'Latitude', 'Time']
    telemetry_columns = set()

    for point_idx, point in enumerate(segment.points):
        # basic fields
        row_data = [point.longitude, point.latitude, point.time]
        
        # handle telemetry fields
        telemetry_data = {}
        trkpt = root.findall('.//default:trkpt', ns)[point_idx]
        extensions = trkpt.find('default:extensions', ns)
        if extensions is not None:
            telemetry = extensions.find('default:TelemetryData', ns)
            if telemetry is not None:
                for elem in telemetry:
                    telemetry_data[elem.tag.split('}')[-1]] = elem.text
                    telemetry_columns.add(elem.tag.split('}')[-1])

        # ensure all telemetry columns are present in the row (even if None)
        row_data.extend([telemetry_data.get(col, None) for col in telemetry_columns])
        data.append(row_data)

    # combine base columns with telemetry columns
    columns = base_columns + list(telemetry_columns)
    
    # create dataframe
    gpx_df = pd.DataFrame(data, columns=columns)
    
    # construct tuples for line
    points = [(point.latitude, point.longitude) for point in segment.points]
    
    return gpx_df, points

def add_points_to_map(gpx_df, map_object):
    for idx, row in gpx_df.iterrows():
        # create data string to display on hover
        tooltip_text = f"Lat: {row['Latitude']:.6f}, Lon: {row['Longitude']:.6f}, Time: {row['Time']}"
        telemetry_data = row.drop(['Longitude', 'Latitude', 'Time']).dropna()
        if not telemetry_data.empty:
            telemetry_info = ', '.join([f"{col}: {val}" for col, val in telemetry_data.items()])
            tooltip_text += f", {telemetry_info}"
        
        # add circlemarker with a tooltip
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=5,
            color='blue',
            fill=True,
            fill_opacity=0.6,
            tooltip=tooltip_text
        ).add_to(map_object)

df, points = process_gpx_to_df('test.gpx')

# create map
mymap = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=6, tiles=None)
folium.TileLayer('openstreetmap', name='OpenStreet Map').add_to(mymap)

# add the interactive points
add_points_to_map(df, mymap)

# polyline to the map
folium.PolyLine(points, color='red', weight=4.5, opacity=.5).add_to(mymap)

# save map
mymap.save("map.html")
