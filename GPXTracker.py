from plugins.base_plugin import BasePlugin
from datetime import datetime, timezone
import gpxpy
import os

class Plugin(BasePlugin):
    plugin_name = "gpxtracker"

    async def handle_meshtastic_message(self, packet, formatted_message, longname, meshnet_name):
        """
        Handles Meshtastic messages and updates the GPX file for the corresponding device.
        """

        # Ensure the message is valid and contains the necessary data
        decoded = packet.get("decoded", {})
        position = decoded.get("position", {})
        if not decoded or decoded.get("portnum") != "POSITION_APP" or not position or "precisionBits" not in position:
            return

        # Extract relevant data
        device_id_raw = packet.get("fromId", "") 
        device_id_hex = device_id_raw.lstrip("!") 
        latitude = position.get("latitude")
        longitude = position.get("longitude")
        altitude = position.get("altitude", 0)

        now = datetime.now(tz=timezone.utc)
        track_name = now.strftime("%Y-%m-%d")

        # Log processed data
        self.logger.info(f"Processed data: Latitude={latitude}, Longitude={longitude}, Altitude={altitude}, track_name={track_name}, Device={device_id_hex}")

        # Create directory and GPX file
        gpx_directory = "./data/gpx_data"
        os.makedirs(gpx_directory, exist_ok=True)  # Create directory if it doesn't exist
        gpx_file_path = os.path.join(gpx_directory, f"{device_id_hex}.gpx")

        # Load or create GPX file
        if os.path.exists(gpx_file_path):
            with open(gpx_file_path, "r") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
        else:
            gpx = gpxpy.gpx.GPX()

        # Create or find the track for the current day
        track = next((t for t in gpx.tracks if t.name == track_name), None)
        if not track:
            track = gpxpy.gpx.GPXTrack(name=track_name)
            gpx.tracks.append(track)

        # Create a segment if none exists
        if not track.segments:
            track.segments.append(gpxpy.gpx.GPXTrackSegment())
        segment = track.segments[0]

        # Add a point to the segment
        point = gpxpy.gpx.GPXTrackPoint(latitude, longitude, elevation=altitude, time=now)
        segment.points.append(point)

        # Save the GPX file
        with open(gpx_file_path, "w") as gpx_file:
            gpx_file.write(gpx.to_xml())

        # Confirm data saved
        self.logger.info(f"Data saved in {gpx_file_path} for device {device_id_hex}")

    async def handle_room_message(self, room, event, full_message):
        """Placeholder for Matrix messages (if needed)."""
        return
