import unittest
from unittest.mock import patch, Mock, call
from morphosource.fetch import fetch_items, fetch_item

MS_MEDIA1 = [{'id': ['000390223']}, {'id': ['000390218']}]
MS_MEDIA2 = [{'id': ['000390225']}, {'id': ['000390219']}]
MS_FACETS = [{'name': 'generic_type_sim', 'items': [], 'label': 'Generic Type Sim'}]
MS_PAGES = {"total_pages": 1}
MS_PAGE_RESPONSE = {
    "response": {
        "media": MS_MEDIA1,
        "facets": MS_FACETS,
        "pages": MS_PAGES,
    }
}
MS_TWO_PAGES = {"total_pages": 2}
MS_PAGE_ARRAY = [
    {
        "response": {
            "media": MS_MEDIA1,
            "facets": MS_FACETS,
            "pages": MS_TWO_PAGES,
        }
    },
    {
        "response": {
            "media": MS_MEDIA2,
            "facets": MS_FACETS,
            "pages": MS_TWO_PAGES,
        }
    },
]


class TestFetch(unittest.TestCase):
    @patch("morphosource.fetch.requests")
    def test_fetch_items_one_page(self, mock_requests):
        response = Mock()
        response.json.return_value = MS_PAGE_RESPONSE
        mock_requests.get.return_value = response
        params = {"value": 1}
        items, facets, pages = fetch_items(
            url="someurl", query="salamander", params=params, per_page=4, page=1, items_name="media"
        )
        self.assertEqual(items, MS_MEDIA1)
        self.assertEqual(facets, MS_FACETS)
        self.assertEqual(pages, MS_PAGES)
        params = {'value': 1, 'search_field': 'all_fields', 'q': 'salamander', 'per_page': 4, 'page': 1}
        mock_requests.get.assert_called_with("someurl", params=params)

    @patch("morphosource.fetch.requests")
    def test_fetch_items_one_page_default_per_page(self, mock_requests):
        response = Mock()
        response.json.return_value = MS_PAGE_RESPONSE
        mock_requests.get.return_value = response
        params = {"value": 1}
        items, facets, pages = fetch_items(
            url="someurl", query="salamander", params=params, per_page=None, page=1, items_name="media"
        )
        params = {'value': 1, 'search_field': 'all_fields', 'q': 'salamander', 'per_page': 10, 'page': 1}
        mock_requests.get.assert_called_with("someurl", params=params)

    @patch("morphosource.fetch.requests")
    def test_fetch_items_multiple_pages(self, mock_requests):
        response = Mock()
        pages = {"total_pages": 2}
        response.json.side_effect = MS_PAGE_ARRAY
        mock_requests.get.return_value = response
        params = {"value": 1}
        items, facets, pages = fetch_items(
            url="someurl", query="salamander", params=params, per_page=None, page=None, items_name="media"
        )
        self.assertEqual(items, MS_MEDIA1 + MS_MEDIA2)
        self.assertEqual(facets, MS_FACETS)
        self.assertEqual(pages, pages)
        page1_params = {'value': 1, 'search_field': 'all_fields', 'q': 'salamander', 'per_page': 10, 'page': 1}
        page2_params = {'value': 1, 'search_field': 'all_fields', 'q': 'salamander', 'per_page': 10, 'page': 2}
        mock_requests.get.assert_has_calls(
            [
                call("someurl", params=page1_params),
                call().raise_for_status(),
                call().json(),
                call("someurl", params=page2_params),
                call().raise_for_status(),
                call().json(),
            ]
        )

    @patch("morphosource.fetch.requests")
    def test_fetch_item(self, mock_requests):
        item = {"id": 123}
        response = Mock()
        response.json.return_value = {"response": item}
        mock_requests.get.return_value = response
        params = {"value": 1}
        result = fetch_item(url="someurl", params=params)
        self.assertEqual(result, item)
        mock_requests.get.assert_called_with("someurl", params=params)
