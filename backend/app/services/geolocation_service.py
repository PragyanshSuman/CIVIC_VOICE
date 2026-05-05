import math

class GeolocationService:
    """
    Service for handling geospatial calculations and validations.
    """
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate Haversine distance between two points in meters.
        """
        R = 6371e3 # Earth radius in meters
        phi1 = lat1 * math.pi / 180
        phi2 = lat2 * math.pi / 180
        delta_phi = (lat2 - lat1) * math.pi / 180
        delta_lambda = (lon2 - lon1) * math.pi / 180

        a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
        
    @staticmethod
    def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_meters: float) -> bool:
        return GeolocationService.calculate_distance(lat1, lon1, lat2, lon2) <= radius_meters
