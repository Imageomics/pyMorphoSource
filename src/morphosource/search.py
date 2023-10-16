import os
import requests
from morphosource.fetch import fetch_items, fetch_item
from morphosource.exceptions import ItemNotFound
from morphosource.download import download_media_bundle
from morphosource.config import Endpoints


def _get(obj, name, unlist=True):
    # Extract value from MorphoSource API data, optionally removing extraneous array
    value = obj.get(name)
    if unlist:
        if value:
            return value[0]
        else:
            return None
    return value


class Media(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.media_type = _get(data, "media_type")
        self.visibility = _get(data, "visibility")
        self.data = data

    def download_bundle(self, path, download_config):
        download_media_bundle(media_id=self.id, path=path, download_config=download_config)


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
            facet_key = f"f[{key}][]"
            params[facet_key] = value
    return params


def search_media(query=None, media_type=None, visibility=None, media_tag=None, per_page=None, page=None):
    params = create_facet_dict(
        human_readable_media_type_ssim=media_type, publication_status_ssi=visibility, keyword_ssim=media_tag
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
