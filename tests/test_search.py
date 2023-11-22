import unittest
import requests
from unittest.mock import patch, Mock
from morphosource.search import search_media, get_media, Media, Endpoints, ItemNotFound, \
    get_object, ObjectTypes, search_objects
from morphosource.download import DownloadVisibility
from morphosource.search import Media

MS_MEDIA = [
    {
        'id': ['000390223'],
        'title': ['Dentary Teeth [Mesh] [CT]'],
        'media_type': ['Mesh'],
        "visibility": ["Open Download"],
        "physical_object_id": ["000577960"],
        'file_thumbnail_url': ['/downloads/000390223?file=thumbnail&t=1604144137'],
    },
    {
        'id': ['000390218'],
        'title': ['Maxillary Teeth [Mesh] [CT]'],
        'media_type': ['Mesh'],
        "visibility": ["Restricted Download"],
        "physical_object_id": ["000577960"]
    },
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
MS_SPECIMEN = [{
    'id': ['000577960'],
    'title': ['MCZ:SC:4041'],
    'type': ['Biological Specimen'],
    'taxonomy': ['Lithobates catesbeiana'],
}]
MS_CULTURAL_OBJECT = [{
    'id': ['000545101'],
    'title': ['YPM:ANT:131819 Spindle Whorl'],
    'type': ['Cultural Heritage Object'],
}]


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
            'f.media_type': 'Mesh',
            'f.publication_status': 'Open Download',
            'f.tag': 'pelvis',
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

    @patch("morphosource.search.fetch_items")
    def test_search_biological_specimen(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_SPECIMEN, MS_FACETS, MS_PAGES
        results = search_objects("Fruitadens", object_type=ObjectTypes.BIOLOGICAL_SPECIMEN)
        self.assertEqual(len(results.items), 1)
        self.assertEqual(results.items[0].id, "000577960")
        self.assertEqual(results.items[0].title, "MCZ:SC:4041")
        self.assertEqual(results.items[0].type, ObjectTypes.BIOLOGICAL_SPECIMEN)
        self.assertEqual(results.items[0].data, MS_SPECIMEN[0])
        self.assertEqual(len(results.facets), 1)
        self.assertEqual(results.pages['total_count'], 2)
        expected_params = {'f.object_type': 'Biological Specimen'}
        mock_fetch_items.assert_called_with(
            url=Endpoints.PHYSICAL_OBJECTS, query="Fruitadens", params=expected_params,
            per_page=None, page=None, items_name="physical_objects"
        )

    @patch("morphosource.search.fetch_items")
    def test_biological_specimen_advanced(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_SPECIMEN, MS_FACETS, MS_PAGES
        results = search_objects("Fruita", object_type=ObjectTypes.BIOLOGICAL_SPECIMEN,
                                 taxonomy_gbif="Ornithischia", media_type="Mesh", media_tag="pelvis",
                                 per_page=8, page=2)
        expected_params = {
            'f.object_type': 'Biological Specimen',
            'f.taxonomy_gbif': 'Ornithischia',
            'f.media_type': 'Mesh',
            'f.media_tag': 'pelvis'
        }
        mock_fetch_items.assert_called_with(
            url=Endpoints.PHYSICAL_OBJECTS, query="Fruita", params=expected_params, 
            per_page=8, page=2, items_name="physical_objects"
        )

    @patch("morphosource.search.fetch_items")
    def test_search_artifact(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_CULTURAL_OBJECT, MS_FACETS, MS_PAGES
        results = search_objects("Spindle", object_type=ObjectTypes.CULTURAL_HERITAGE)
        self.assertEqual(len(results.items), 1)
        self.assertEqual(results.items[0].id, "000545101")
        self.assertEqual(results.items[0].title, "YPM:ANT:131819 Spindle Whorl")
        self.assertEqual(results.items[0].type, ObjectTypes.CULTURAL_HERITAGE)
        self.assertEqual(results.items[0].data, MS_CULTURAL_OBJECT[0])
        self.assertEqual(len(results.facets), 1)
        self.assertEqual(results.pages['total_count'], 2)
        expected_params = {'f.object_type': 'Cultural Heritage Object'}
        mock_fetch_items.assert_called_with(
            url=Endpoints.PHYSICAL_OBJECTS, query="Spindle", params=expected_params,
            per_page=None, page=None, items_name="physical_objects"
        )

    @patch("morphosource.search.fetch_items")
    def test_artifact_advanced(self, mock_fetch_items):
        mock_fetch_items.return_value = MS_SPECIMEN, MS_FACETS, MS_PAGES
        results = search_objects("Spindle", object_type=ObjectTypes.CULTURAL_HERITAGE,
                                 media_type="Mesh", media_tag="ceramic", per_page=8, page=2)
        expected_params = {
            'f.object_type': 'Cultural Heritage Object',
            'f.media_type': 'Mesh',
            'f.media_tag': 'ceramic'
        }
        mock_fetch_items.assert_called_with(
            url=Endpoints.PHYSICAL_OBJECTS, query="Spindle", params=expected_params,
            per_page=8, page=2, items_name="physical_objects"
        )

    @patch("morphosource.search.fetch_item")
    def test_get_biological_specimen(self, mock_fetch_item):
        mock_fetch_item.return_value = {"biological_specimen": MS_SPECIMEN[0]}
        obj = get_object(object_id="123")
        self.assertEqual(obj.id, "000577960")
        self.assertEqual(obj.title, "MCZ:SC:4041")
        self.assertEqual(obj.taxonomy, "Lithobates catesbeiana")
        self.assertEqual(obj.type, ObjectTypes.BIOLOGICAL_SPECIMEN)
        self.assertEqual(obj.data, MS_SPECIMEN[0])
        mock_fetch_item.assert_called_with(f"{Endpoints.PHYSICAL_OBJECTS}/123")

    @patch("morphosource.search.fetch_item")
    def test_get_cultural_heritage_object(self, mock_fetch_item):
        mock_fetch_item.return_value = {"cultural_heritage_object": MS_CULTURAL_OBJECT[0]}
        obj = get_object(object_id="123")
        self.assertEqual(obj.id, "000545101")
        self.assertEqual(obj.title, "YPM:ANT:131819 Spindle Whorl")
        self.assertEqual(obj.type, ObjectTypes.CULTURAL_HERITAGE)
        self.assertEqual(obj.taxonomy, None)
        self.assertEqual(obj.data, MS_CULTURAL_OBJECT[0])
        mock_fetch_item.assert_called_with(f"{Endpoints.PHYSICAL_OBJECTS}/123")

    @patch("morphosource.search.fetch_item")
    def test_get_biological_specimen_not_found(self, mock_fetch_item):
        error = requests.exceptions.HTTPError()
        error.response = Mock(status_code=404)
        mock_fetch_item.side_effect = error
        with self.assertRaises(ItemNotFound) as raised_exception:
            obj = get_object(object_id="123")
        self.assertEqual(str(raised_exception.exception), "No object found with id 123")

    @patch("morphosource.search.fetch_item")
    @patch("morphosource.search.search_media")
    def test_physicial_object_get_media_ary(self, mock_search_media, mock_fetch_item):
        mock_fetch_item.return_value = {"biological_specimen": MS_SPECIMEN[0]}
        media1 = Media(MS_MEDIA[0])
        media2 = Media(MS_MEDIA[1])
        mock_search_media.return_value = Mock(items=[media1, media2])
        obj = get_object(object_id="123")

        ary = obj.get_media_ary()
        self.assertEqual(ary, [media1, media2])
        mock_search_media.assert_called_with(query='000577960', visibility=None)

        ary = obj.get_media_ary(visibility=DownloadVisibility.OPEN)
        mock_search_media.assert_called_with(query='000577960', visibility=DownloadVisibility.OPEN)

        ary = obj.get_media_ary(visibility=DownloadVisibility.RESTRICTED)
        mock_search_media.assert_called_with(query='000577960', visibility=DownloadVisibility.RESTRICTED)

    def test_get_website_url(self):
        media = Media(MS_MEDIA[0])
        url = media.get_website_url()
        self.assertEqual(url, "https://www.morphosource.org/concern/media/000390223")

    def test_get_thumbnail_url(self):
        media = Media(MS_MEDIA[0])
        url = media.get_thumbnail_url()
        self.assertEqual(url, "https://www.morphosource.org/downloads/000390223?file=thumbnail&t=1604144137")

        media = Media(MS_MEDIA[1])
        url = media.get_thumbnail_url()
        self.assertEqual(url, None)
