import os
import requests
from morphosource.fetch import fetch_items, fetch_item
from morphosource.exceptions import ItemNotFound
from morphosource.download import download_media_bundle, get_download_media_zip_url, DownloadVisibility
from morphosource.config import Endpoints, WEBSITE_URL


def _get(obj, name, unlist=True):
    # Extract value from MorphoSource API data, optionally removing extraneous array
    value = obj.get(name)
    if unlist:
        if value:
            return value[0]
        else:
            return None
    return value


class ObjectTypes(object):
    BIOLOGICAL_SPECIMEN = "Biological Specimen"
    CULTURAL_HERITAGE = "Cultural Heritage Object"


class Media(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.media_type = _get(data, "media_type")
        self.visibility = _get(data, "visibility")
        self.physical_object_id = _get(data, "physical_object_id")
        self.data = data

    def download_bundle(self, path, download_config):
        download_media_bundle(media_id=self.id, path=path, download_config=download_config)

    def get_download_bundle_url(self, download_config):
        return get_download_media_zip_url(media_id=self.id, download_config=download_config)

    def get_website_url(self):
        return f"{WEBSITE_URL}/concern/media/{self.id}"

    def get_thumbnail_url(self):
        file_thumbnail_url = _get(self.data, 'file_thumbnail_url')
        if file_thumbnail_url:
            return f"{WEBSITE_URL}{file_thumbnail_url}"
        return None


class PhysicalObject(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.type = _get(data, "type")
        self.taxonomy = _get(data, "taxonomy")
        self.data = data

    def get_media_ary(self, visibility=None):
        results = []
        media_search_results = search_media(query=self.id, visibility=visibility)
        for media in media_search_results.items:
            if self.id == media.physical_object_id:
                results.append(media)
            else:
                results.append(media)
        return results


class SearchResults(object):
    def __init__(self, items, facets, pages):
        self.items = items
        self.facets = facets
        self.pages = pages


def create_facet_dict(**kwargs):
    # Apply MorphoSource facet formatting to the key for each keyword parameter.
    # Skip items with empty values.
    params = {}
    for key, value in kwargs.items():
        if value:
            facet_key = f"f.{key}"
            params[facet_key] = value
    return params


def search_media(query=None, media_type=None, taxonomy_gbif=None, visibility=None, media_tag=None, per_page=None, page=None):
    params = create_facet_dict(
        media_type=media_type, taxonomy_gbif=taxonomy_gbif, publication_status=visibility, tag=media_tag
    )
    raw_items, facets, pages = fetch_items(
        url=Endpoints.MEDIA, query=query, params=params, per_page=per_page, page=page, items_name="media"
    )
    media_items = [Media(item) for item in raw_items]
    return SearchResults(media_items, facets, pages)


def get_media(media_id):
    try:
        url = f"{Endpoints.MEDIA}/{media_id}"
        data = fetch_item(url)["media"]
        return Media(data=data)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise ItemNotFound(f"No media found with id {media_id}")
        raise err


def search_objects(
    query=None, object_type=None, taxonomy_gbif=None, media_type=None, media_tag=None, per_page=None, page=None
):
    params = create_facet_dict(
        object_type=object_type,
        taxonomy_gbif=taxonomy_gbif,
        media_type=media_type,
        media_tag=media_tag
    )
    raw_items, facets, pages = fetch_items(
        url=Endpoints.PHYSICAL_OBJECTS,
        query=query,
        params=params,
        per_page=per_page,
        page=page,
        items_name="physical_objects",
    )
    objects = [PhysicalObject(item) for item in raw_items]
    return SearchResults(objects, facets, pages)


def get_object(object_id):
    try:
        url = f"{Endpoints.PHYSICAL_OBJECTS}/{object_id}"
        outer_data = fetch_item(url)
        if "biological_specimen" in outer_data:
            data = outer_data["biological_specimen"]
        elif "cultural_heritage_object" in outer_data:
            data = outer_data["cultural_heritage_object"]
        else:
            raise ValueError(f"Received unknown physical object: {outer_data.keys()}")
        return PhysicalObject(data=data)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise ItemNotFound(f"No object found with id {object_id}")
        raise err
