import unittest
import requests
from unittest.mock import patch, Mock, mock_open
from morphosource.download import download_media_bundle, get_download_media_zip_url, \
    DownloadConfig, Endpoints
from morphosource.exceptions import RestrictedDownloadError


download_config = DownloadConfig(
    api_key="Secret", use_statement="Downloading this data as part of a research project.", use_categories=["Research"]
)


class TestDownload(unittest.TestCase):
    @patch("morphosource.download.requests")
    @patch('builtins.open', new_callable=mock_open)
    def test_download_media_bundle(self, mock_file, mock_requests):
        post_response = Mock()
        mock_requests.post.return_value = post_response
        post_response.json.return_value = {"response": {"media": {"download_url": "someurl"}}}
        get_response = Mock()
        get_response.iter_content.return_value = ["somedata"]
        mock_requests.get.return_value = get_response

        download_media_bundle(media_id="123", path="/tmp/123.zip", download_config=download_config)

        # Check POST used to fetch download URL
        expected_headers = headers = {'Authorization': 'Secret'}
        expected_json = {
            'use_statement': 'Downloading this data as part of a research project.',
            'agreements_accepted': True,
            'use_categories': ['Research'],
        }
        mock_requests.post.assert_called_with(f"{Endpoints.DOWNLOAD}/123", headers=expected_headers, json=expected_json)

        # Check GET used to fetch file contents
        mock_requests.get.assert_called_with('someurl', headers={'Authorization': 'Secret'}, stream=True)

    @patch("morphosource.download.requests")
    @patch('builtins.open', new_callable=mock_open)
    def test_download_media_bundle_restricted(self, mock_file, mock_requests):
        error = requests.exceptions.HTTPError()
        error.response = Mock(status_code=404)
        mock_requests.post.side_effect = error
        with self.assertRaises(RestrictedDownloadError) as raised_exception:
            download_media_bundle(media_id="123", path="/tmp/123.zip", download_config=download_config)
        expected_msg = """You do not have authorization to download this restricted media.
Please visit https://www.morphosource.org and request download permission for media id: 123"""
        self.assertEqual(str(raised_exception.exception), expected_msg)

    @patch("morphosource.download.requests")
    def test_get_download_bundle_url(self, mock_requests):
        post_response = Mock()
        mock_requests.post.return_value = post_response
        post_response.json.return_value = {"response": {"media": {"download_url": "someurl"}}}

        url = get_download_media_zip_url(media_id="1", download_config=download_config)

        self.assertEqual(url, "someurl")
