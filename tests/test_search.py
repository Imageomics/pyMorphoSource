import unittest
import requests
from unittest.mock import patch, Mock
from morphosource.search import search_media, get_media, Endpoints, ItemNotFound
from morphosource.download import DownloadVisibility

MS_MEDIA = [
    {
        'id': ['000390223'],
        'title': ['Dentary Teeth [Mesh] [CT]'],
        'media_type': ['Mesh'],
        "visibility": ["Open Download"],
    },
    {'id': ['000390218'], 'title': ['Maxillary Teeth [Mesh] [CT]'], 'media_type': ['Mesh']},
]
MS_FACETS = [{'name': 'generic_type_sim', 'items': [], 'label': 'Generic Type Sim'}]
MS_PAGES = {
    'current_page': 1,
    'next_page': None,
    'prev_page': None,
    'total_pages': 1,
    'limit_value': 10,
    'offset_value': 0,
    'total_count': 2,
    'first_page?': True,
    'last_page?': True,
}


class TestSearch(unittest.TestCase):
    @patch("morphosource.search.fetch_items")
    def test_search_media(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_MEDIA, MS_FACETS, MS_PAGES
        results = search_media("Fruitadens")
        self.assertEqual(len(results.items), 2)
        self.assertEqual(results.items[0].id, "000390223")
        self.assertEqual(results.items[0].title, "Dentary Teeth [Mesh] [CT]")
        self.assertEqual(results.items[0].media_type, "Mesh")
        self.assertEqual(results.items[0].visibility, "Open Download")
        self.assertEqual(results.items[0].data, MS_MEDIA[0])
        self.assertEqual(len(results.facets), 1)
        self.assertEqual(results.pages['total_count'], 2)
        mock_fetch_items.assert_called_with(
            url=Endpoints.MEDIA, query="Fruitadens", params={}, per_page=None, page=None, items_name="media"
        )

    @patch("morphosource.search.fetch_items")
    def test_search_media_advanced(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_MEDIA, MS_FACETS, MS_PAGES
        results = search_media(
            "Fruitadens", media_type="Mesh", visibility=DownloadVisibility.OPEN, media_tag="pelvis", per_page=8, page=2
        )
        expected_params = {
            'f[human_readable_media_type_ssim][]': 'Mesh',
            'f[publication_status_ssi][]': 'Open Download',
            'f[keyword_ssim][]': 'pelvis',
        }
        mock_fetch_items.assert_called_with(
            url=Endpoints.MEDIA, query="Fruitadens", params=expected_params, per_page=8, page=2, items_name="media"
        )

    @patch("morphosource.search.fetch_item")
    def test_get_media(self, mock_fetch_item):
        mock_fetch_item.return_value = {"media": MS_MEDIA[0]}
        media = get_media(media_id="123")
        self.assertEqual(media.id, "000390223")
        self.assertEqual(media.title, "Dentary Teeth [Mesh] [CT]")
        self.assertEqual(media.media_type, "Mesh")
        self.assertEqual(media.visibility, "Open Download")
        self.assertEqual(media.data, MS_MEDIA[0])
        mock_fetch_item.assert_called_with(f"{Endpoints.MEDIA}/123")

    @patch("morphosource.search.fetch_item")
    def test_get_media_not_found(self, mock_fetch_item):
        error = requests.exceptions.HTTPError()
        error.response = Mock(status_code=404)
        mock_fetch_item.side_effect = error
        with self.assertRaises(ItemNotFound) as raised_exception:
            media = get_media(media_id="123")
        self.assertEqual(str(raised_exception.exception), "No media found with id 123")
