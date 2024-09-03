import gpxpy
import gpxpy.gpx
import json
import os
from xml.etree.ElementTree import Element
from datetime import datetime

TRACKER_NAME = "test"

# append GPX file if it already exists, else make a new GPX file
gpx_file = f'{TRACKER_NAME}.gpx'
if os.path.exists(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)
else:
    gpx = gpxpy.gpx.GPX()

# create a new GPX track if it doesn't exist
if not gpx.tracks:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
else:
    gpx_track = gpx.tracks[0]

# create GPX segment
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# load JSON data
with open(f'{TRACKER_NAME}.json', 'r') as f:
    data = json.load(f)

# iterate through each point in the JSON
for point_key, point in data.items():
    # convert time string to datetime object
    time = datetime.fromisoformat(point['time'].replace('Z', '+00:00'))

    gpx_point = gpxpy.gpx.GPXTrackPoint(
        time=time,
        latitude=point['lat'],
        longitude=point['long']
    )

    # create extensions for telemetry data
    telemetry_data = Element('TelemetryData')
    for key, value in point['telemetry'].items():
        data_element = Element(key)
        data_element.text = str(value)
        telemetry_data.append(data_element)
    
    # append telemetry data to the point's extensions
    gpx_point.extensions.append(telemetry_data)

    # append the point to the GPX segment
    gpx_segment.points.append(gpx_point)

# write the updated GPX data back to the file
with open(gpx_file, 'w') as f:
    f.write(gpx.to_xml())
