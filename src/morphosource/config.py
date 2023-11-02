import os

API_URL = os.environ.get("MORPHOSOURCE_API_URL", "https://www.morphosource.org/api")


class Endpoints(object):
    MEDIA = f"{API_URL}/media"
    DOWNLOAD = f"{API_URL}/download"
    PHYSICAL_OBJECTS = f"{API_URL}/physical-objects"
