import os
import requests
import morphosource.facetnames as facetnames
from morphosource.fetch import fetch_items, fetch_item

API_URL = os.environ.get("MORPHOSOURCE_API_URL", "https://www.morphosource.org/api")
PHYSICAL_OBJECTS_ENDPOINT = f"{API_URL}/physical-objects"
MEDIA_ENDPOINT = f"{API_URL}/media"

BIOLOGICAL_SPECIMENT_TYPE = "Biological Specimen"
CULTURAL_HERITAGE_OBJECT = "Cultural Heritage Object"

DEFAULT_DOWNLOAD_USE_STATEMENT = "Downloading this data as part of a research project."
DEFAULT_USE_CATEGORIES = ["Research"]
RESTRICTED_DOWNLOAD_MSG = """You do not have authorization to download this restricted media. 
Please visit https://www.morphosource.org and request download permission for media id:"""


def _get(obj, name, unlist=True):
    # Extract value from MorphoSource API data, optionally removing extraneous array
    value = obj.get(name)
    if unlist:
        if value:
            return value[0]
        else:
            return None
    return value


class RestrictedDownloadError(Exception):
    pass


class ItemNotFound(Exception):
    pass


class Media(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.media_type = _get(data, "media_type")
        self.visibility = _get(data, "visibility")
        self.physical_object_id = _get(data, "physical_object_id")
        self.data = data

    def download_bundle(
        self,
        path,
        api_key,
        use_statement=DEFAULT_DOWNLOAD_USE_STATEMENT,
        use_categories=DEFAULT_USE_CATEGORIES,
        use_category_other=None,
    ):
        download_url = get_download_media_zip_url(
            media_id=self.id,
            api_key=api_key,
            use_statement=use_statement,
            use_categories=use_categories,
            use_category_other=use_category_other,
        )
        with open(path, 'wb') as fd:
            download_file(url=download_url, fd=fd, api_key=api_key)


class MediaSearchResults(object):
    def __init__(self, items, facets, pages):
        self.items = [Media(item) for item in items]
        self.facets = facets
        self.pages = pages


class PhysicalObject(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.taxonomy = _get(data, "taxonomy")
        self.data = data

    def get_media_ary(self, open_visibility_only=False):
        results = []
        media_search_results = search_media(query=self.id)
        for media in media_search_results.items:
            if self.id == media.physical_object_id:
                if open_visibility_only:
                    if media.visibility == "open":
                        results.append(media)
                else:
                    results.append(media)
        return results


class PhysicalObjectSearchResults(object):
    def __init__(self, items, facets, pages):
        self.items = [PhysicalObject(item) for item in items]
        self.facets = facets
        self.pages = pages


def search_media(
    query=None, media_type=None, publication=None, media_tag=None, object_type=None, per_page=None, page=None
):
    params = {}
    if media_type:
        params[facetnames.MEDIA_TYPE] = media_type
    if publication:
        params[facetnames.MEDIA_PUBLICATION] = publication
    if media_tag:
        params[facetnames.MEDIA_TAG] = media_tag        
    if object_type:
        params[facetnames.MEDIA_OBJECT_TYPE] = object_type
    items, facets, pages = fetch_items(
        url=MEDIA_ENDPOINT, query=query, params=params, per_page=per_page, page=page, items_name="media"
    )
    return MediaSearchResults(items, facets, pages)


def get_media(media_id):
    try:
        url = f"{API_URL}/media/{media_id}"
        data = fetch_item(url)["media"]
        return Media(data=data)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise ItemNotFound(f"No media found with id {media_id}")
        raise err


def get_download_media_zip_url(media_id, api_key, use_statement, use_categories, use_category_other):
    url = f"{API_URL}/download/{media_id}"
    data = {"use_statement": use_statement, "agreements_accepted": True}
    if use_categories:
        data["use_categories"] = use_categories
    else:
        data["use_category_other"] = use_category_other
    headers = {"Authorization": api_key}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["response"]["media"]["download_url"][0]
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise RestrictedDownloadError(f"{RESTRICTED_DOWNLOAD_MSG} {media_id}")
        raise err


def download_file(url, fd, api_key):
    headers = {"Authorization": api_key}
    download_response = requests.get(url, headers=headers, stream=True)
    for chunk in download_response.iter_content(chunk_size=128):
        fd.write(chunk)


def search_objects(
    query=None, object_type=None, taxonomy=None, media_type=None, media_tag=None, per_page=None, page=None
):
    params = {}
    if object_type:
        params[facetnames.OBJECT_TYPE] = object_type
    if taxonomy:
        params[facetnames.OBJECT_TAXONOMY_GBIF] = taxonomy
    if media_type:
        params[facetnames.OBJECT_MEDIA_TYPE] = media_type
    if media_tag:
        params[facetnames.OBJECT_MEDIA_TAG] = media_tag

    items, facets, pages = fetch_items(
        url=PHYSICAL_OBJECTS_ENDPOINT,
        query=query,
        params=params,
        per_page=per_page,
        page=page,
        items_name="physical_objects",
    )
    return PhysicalObjectSearchResults(items, facets, pages)


def search_biological_specimens(query=None, taxonomy=None, media_type=None, media_tag=None, per_page=None, page=None):
    return search_objects(
        query=query,
        object_type=BIOLOGICAL_SPECIMENT_TYPE,
        taxonomy=taxonomy,
        media_type=media_type,
        media_tag=media_tag,
        per_page=per_page,
        page=page,
    )


def search_cultural_heritage_objects(query=None, media_type=None, media_tag=None, per_page=None, page=None):
    return search_objects(
        query=query,
        object_type=CULTURAL_HERITAGE_OBJECT,
        media_type=media_type,
        media_tag=media_tag,
        per_page=per_page,
        page=page,
    )


def get_object(object_id):
    try:
        url = f"{PHYSICAL_OBJECTS_ENDPOINT}/{object_id}"
        data = fetch_item(url)
        return PhysicalObject(data=data)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            raise ItemNotFound(f"No physical object found with id {object_id}")
        raise err