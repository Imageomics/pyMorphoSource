import os
import requests
import tempfile
import zipfile

API_URL = os.environ.get("MORPHOSOURCE_API_URL", "https://www.morphosource.org/api")

FACET_TYPE = f"f[human_readable_type_sim][]" # Type
BIOLOGICAL_SPECIMENT_TYPE = "Biological Specimen"

TAXONOMY_TYPE = f"f[external_taxonomy_ssim][]" # Taxonomy (GBIF)
MEDIA_TYPE = f"f[public_media_type_ssim][]" # Media Tag

QUERY_PARAM = "q"
SEARCH_FIELD_PARAM = "search_field"
SEARCH_ALL_FIELDS_VALUE = "all_fields"

PER_PAGE_PARAM = "per_page"
PAGE_PARAM = "page"

DEFAULT_DOWNLOAD_USE_STATEMENT = "Downloading this data as part of a research project."
DEFAULT_USE_CATEGORIES = ["Research"]


def _get(obj, name, unlist=True):
    value = obj.get(name)
    if unlist:
        if value:
            return value[0]
        else:
            return None
    return value


class BiologicalSpecimen(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.taxonomy = _get(data, "taxonomy")
        self.data = data

    def get_media_ary(self, open_visibility_only=False):
        results = []
        media_response = search_media(query=self.id)
        for media_dict in media_response['media']:
            if self.id in media_dict["physical_object_id"]:
                media = Media(media_dict)
                if open_visibility_only:
                    if media.visibility == "open":
                        results.append(media)
                else:
                    results.append(media)
        return results


class Media(object):
    def __init__(self, data):
        self.id = _get(data, "id")
        self.title = _get(data, "title")
        self.media_type = _get(data, "media_type")
        self.visibility = _get(data, "visibility")
        self.data = data

    def download_bundle(self, path, api_key, use_statement=DEFAULT_DOWNLOAD_USE_STATEMENT,
                 use_categories=DEFAULT_USE_CATEGORIES, use_category_other=None):
        download_url = get_download_media_zip_url(
            media_id=self.id, api_key=api_key,use_statement=use_statement,
            use_categories=use_categories, use_category_other=use_category_other)
        with open(path, 'wb') as fd:
            download_file(url=download_url, fd=fd, api_key=api_key)


class SpecimenSearchResults(object):
    def __init__(self, data):
        self.specimens = [BiologicalSpecimen(obj) for obj in data['physical_objects']]
        self.facets = data['facets']
        self.pages = data['pages']


def search_biological_specimens(query=None, taxonomy=None, media_type=None, per_page=None, page=None):
    url = f"{API_URL}/physical-objects"
    params = {
        FACET_TYPE: BIOLOGICAL_SPECIMENT_TYPE
    }
    if query:
        params[SEARCH_FIELD_PARAM] = SEARCH_ALL_FIELDS_VALUE
        params[QUERY_PARAM] = query
    if taxonomy:
        params[TAXONOMY_TYPE] = taxonomy
    if media_type:
        params[MEDIA_TYPE] = media_type
    if per_page:
        params[PER_PAGE_PARAM] = per_page
    if page:
        params[PAGE_PARAM] = page

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['response']
    return SpecimenSearchResults(data)


def get_media(id):
    url = f"{API_URL}/media/{id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def search_media(query):
    url = f"{API_URL}/media"
    params = {
        SEARCH_FIELD_PARAM: SEARCH_ALL_FIELDS_VALUE,
        QUERY_PARAM: query
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["response"]


def get_download_media_zip_url(media_id, api_key, use_statement, use_categories, use_category_other):
    url = f"{API_URL}/download/{media_id}"
    data = {
        "use_statement" :use_statement,
        "agreements_accepted": True
    }
    if use_categories:
        data["use_categories"] = use_categories
    else:
        data["use_category_other"] = use_category_other
    headers = {
        "Authorization": api_key
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["response"]["media"]["download_url"][0]


def download_file(url, fd, api_key):
    headers = {
        "Authorization": api_key
    }
    download_response = requests.get(url, headers=headers, stream=True)
    for chunk in download_response.iter_content(chunk_size=128):
        fd.write(chunk)
