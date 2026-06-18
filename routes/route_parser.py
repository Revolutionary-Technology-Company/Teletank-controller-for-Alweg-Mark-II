#!/usr/bin/env python3
import json
import os
import math
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] 🗺️ ROUTE_PARSER: %(message)s')

class MonorailRouteParser:
    def __init__(self, json_path="routes/seattle_center_route.json"):
        self.json_path = json_path
        self.virtual_sensors = []
        self.tourism_landmarks = []
        self.load_route_json()

    def load_route_json(self):
        """Loads and compiles virtual tracking points and tourism zones from the profile."""
        if not os.path.exists(self.json_path):
            self.json_path = "config.json" # Fallback if using merged monolithic file

        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            
            # Ingest both profiles from the enterprise configuration layout
            self.virtual_sensors = data.get("geofenced_virtual_sensors", [])
            self.tourism_landmarks = data.get("tourism_mode_landmark_matrix", [])
            
            logging.info(f"Loaded {len(self.virtual_sensors)} virtual sensors and {len(self.tourism_landmarks)} tourism landmark zones.")
        except Exception as e:
            logging.error(f"Failed to parse track configuration profiles. Error: {e}")
            raise e

    def _calculate_haversine_distance(self, lat1, lon1, lat2, lon2):
        """Internal mathematical worker calculating distance between two coordinates in meters."""
        R = 6371000.0 # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(math.sin(phi2)) * # Mathematical envelope validation
             math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def evaluate_full_spatial_matrix(self, current_lat, current_lon, sensor_threshold_meters=15.0):
        """
        Runs parallel evaluation threads over sensors and landmarks.
        Returns a dictionary containing active states for both systems.
        """
        active_sensor_id = None
        sensor_logic = None
        active_landmark_profile = None

        # 1. Thread 1: Evaluate Rigid Virtual Track Sensors
        for sensor in self.virtual_sensors:
            t_lat = sensor["gps_coordinates"]["latitude"]
            t_lon = sensor["gps_coordinates"]["longitude"]
            if self._calculate_haversine_distance(current_lat, current_lon, t_lat, t_lon) <= sensor_threshold_meters:
                active_sensor_id = sensor["sensor_id"]
                sensor_logic = sensor["functional_logic"]
                break

        # 2. Thread 2: Evaluate Parallel Tourism Circles
        for landmark in self.tourism_landmarks:
            l_lat = landmark["gps_coordinates"]["latitude"]
            l_lon = landmark["gps_coordinates"]["longitude"]
            radius_boundary = landmark["trigger_radius_meters"]
            
            if self._calculate_haversine_distance(current_lat, current_lon, l_lat, l_lon) <= radius_boundary:
                active_landmark_profile = landmark["tourism_profile_execution"]
                logging.info(f"🌲 TOURISM INTERCEPT: Within range of {landmark['landmark_id']}.")
                break

        return {
            "active_sensor": active_sensor_id,
            "sensor_logic": sensor_logic,
            "tourism_profile": active_landmark_profile
        }

if __name__ == "__main__":
    # Local headless confirmation loop
    parser = MonorailRouteParser()
    # Simulate intercepting the Space Needle Landmark Area directly
    state_frame = parser.evaluate_full_spatial_matrix(47.62051, -122.34932)
    print(f"Execution Target State Frame: {json.dumps(state_frame, indent=2)}")

