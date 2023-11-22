import requests
from requests.exceptions import HTTPError
from morphosource.config import Endpoints
from morphosource.exceptions import RestrictedDownloadError

RESTRICTED_DOWNLOAD_MSG = """You do not have authorization to download this restricted media.
Please visit https://www.morphosource.org and request download permission for media id:"""


class DownloadConfig(object):
    def __init__(self, api_key, use_statement, use_categories=None, use_category_other=None):
        self.api_key = api_key
        self.use_statement = use_statement
        self.use_categories = use_categories
        self.use_category_other = use_category_other
        if not self.use_categories and not self.use_category_other:
            raise ValueError("Either use_categories or use_category_other must have a value.")


class DownloadVisibility(object):
    # In the MorphoSource UI this is called Publication
    OPEN = "Open Download"
    RESTRICTED = "Restricted Download"


def get_download_media_zip_url(media_id, download_config):
    url = f"{Endpoints.DOWNLOAD}/{media_id}"
    data = {"use_statement": download_config.use_statement, "agreements_accepted": True}
    if download_config.use_categories:
        data["use_categories"] = download_config.use_categories
    else:
        data["use_category_other"] = download_config.use_category_other
    headers = {"Authorization": download_config.api_key}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["response"]["media"]["download_url"]
    except HTTPError as err:
        if err.response.status_code == 404:
            raise RestrictedDownloadError(f"{RESTRICTED_DOWNLOAD_MSG} {media_id}")
        raise err


def download_file(url, path, api_key, chunk_size=128):
    headers = {"Authorization": api_key}
    download_response = requests.get(url, headers=headers, stream=True)
    with open(path, 'wb') as fd:
        for chunk in download_response.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def download_media_bundle(media_id, path, download_config):
    download_url = get_download_media_zip_url(media_id=media_id, download_config=download_config)
    download_file(url=download_url, api_key=download_config.api_key, path=path)
