# pyMorphoSource
Python package for interacting with the [MorphoSource](https://www.morphosource.org/) [API](https://morphosource.stoplight.io/).

__NOTE:__ By using this package to download files from MorphoSource you are consenting to the user agreements of those specific files.
See [MorphoSource Terms of Use](https://www.morphosource.org/terms) for more details.

**Table of Contents**

- [Installation](#installation)
- [Setup](#setup)
- [Examples](#examples)

## Installation

```console
pip install --upgrade morphosource
```

## Setup
Downloading files using the MorphoSource API requires an API Key.
To create the API Key:
- Visit https://www.morphosource.org/
- Create an account
- Click Person icon in top right corner
- Click Dashboard
- Click Profile
- Click View API Key under Advanced user functions
- Copy this value so it can be used in the example python code below

## Examples
### Media
#### Search Media
The `search_media()` function allows searching for media in MorphoSource.

This function is the equivalent of searching in the MorphoSource website with "Media" chosen:
![morphosource media search](docs/images/morphosource-media-search.png)

This example searches media checking all fields for "Fruitadens".
```python
from morphosource import search_media

results = search_media("Fruitadens")
print("Found", results.pages["total_count"], "items")
for media in results.items:
    print(media.id, media.title)
```

Example Output:
```console
Found 5 items
000390223 Dentary Teeth [Mesh] [CT]
000390218 Maxillary Teeth [Mesh] [CT]
000390213 Maxillary Teeth [Mesh] [CT]
000390208 Dentary Teeth [Mesh] [CT]
000390204 Maxillary Teeth [Mesh] [CT]
```

By default `search_media()` will fetch all items, which can be slow for certain queries.
To fetch a limited set of items pass the `page` and `per_page` parameters. 

#### Search and Download Open Media
MorphoSource contains some media that has restricted download status. 
The `search_media()` `visibility` parameter allows filtering for OPEN or RESTRICTED download media.
To download a media file requires a MorphoSource API key, a use statement, and use categories.
This example expects the MorphoSource API key to be supplied via an environment variable.

```python
import os
from morphosource import search_media, DownloadConfig, DownloadVisibility

download_config = DownloadConfig(
  api_key=os.environ["API_KEY"],
  use_statement="Downloading this data as part of a research project.",
  use_categories=["Research"]
)

results = search_media("Fruitadens", visibility=DownloadVisibility.OPEN)
for media in results.items:
    path = f"{media.id}.zip"
    print(f"Downloading {media.id} {media.title} to {path}")
    media.download_bundle(path, download_config)
```

Next you need to use the MorphoSource API key created following [Create an API Key instructions](#create-an-api-Key).
To set the API_KEY environment variable run the following filling in your API KEY:
```console
export API_KEY=<MorphoSource-API-Key>
```
Then you can run the python script.

Example Output:
```console
Downloading 000390223 Dentary Teeth [Mesh] [CT] to 000390223.zip
Downloading 000390218 Maxillary Teeth [Mesh] [CT] to 000390218.zip
Downloading 000390213 Maxillary Teeth [Mesh] [CT] to 000390213.zip
Downloading 000390208 Dentary Teeth [Mesh] [CT] to 000390208.zip
Downloading 000390204 Maxillary Teeth [Mesh] [CT] to 000390204.zip
```

If you attempt to download restricted media that you have not received permissions for, a `RestrictedDownloadError` exception will be raised. Requesting permissions for some media must be done via [MorphoSource](https://www.morphosource.org/). Once you have received permission, you can use this package to download the media.

#### Search Media Advanced
The  `search_media` has some additional parameters to filter the items returned.
- media_type - str - Type of media (eg. "Mesh")
- media_tag - str - Tag applied to the meda (eg. "femur")

This example uses many parameters to search for the first 4 media matching the combined filters.  
```python
from morphosource import search_media

results = search_media("X-Ray",  taxonomy_gbif="Chalcides", media_type="Mesh", media_tag="pelvis",
                       per_page=4, page=1)
print("Found", results.pages["total_count"], "items")
for media in results.items:
    print(media.id, media.title)

```

Example Output:
```console
Found 50 items
000427170 Pelvis [Mesh] [CT]
000427163 Pelvis [Mesh] [CT]
000427156 Pelvis [Mesh] [CT]
000427149 Pelvis [Mesh] [CT]
```

#### Get Single Media
The `get_media()` function can be used to retrieve details about a single media object.

In this example we fetch media with id "000425163".
The `data` property contains all fields returned from the MorphoSource API.
The `get_website_url()` method returns a URL to view the media in the MorphoSource website.
The `get_thumbnail_url()` method returns a URL for the media's thumbnail image.
```python
from morphosource import get_media

media = get_media(media_id="000425163")
print(media.id, media.title)
print(media.data)
print(media.get_website_url())
print(media.get_thumbnail_url())
```

Example Output:
```console
000425163 Humerus [Mesh] [CT]
{'id': ['000425163'], 'title': ['Humerus [Mesh] [CT]'], 'media_type': ['Mesh'], 'modality': ['MicroNanoXRayComputedTomography'], 'device': ['Nikon Metrology XT H 225 ST'], ...
https://www.morphosource.org/concern/media/000425163
https://www.morphosource.org/downloads/000425163?file=thumbnail&t=1645803720
```

If the media id isn't found a `morphosource.api.ItemNotFound` exception will be raised.

#### Get Media Metadata
The `Media` object method `get_file_metadata()` can be used to retrieve file metadata for the media object.

In this example we fetch media with id "000425163" and lookup file metadata information. Note that the returned file size is given in bytes.
The `data` property contains all fields returned from the MorphoSource API.
```python
from morphosource import get_media

media = get_media(media_id="000425163")
metadata = media.get_file_metadata()
print("Filename:", metadata.file_name)
print("File size:", metadata.file_size)
print(metadata.data)
```

Example Output:
```console
Filename: Carettochelys_insculpta_KU-herps-158563_Humerus_right.ply
File size: 2875371
{...'point_count': ['64832'], 'face_count': ['131068'], 'has_uv_space': ['False'],...}
```

Some MorphoSource media have no file and thereby have no file metadata. If you attempt to retrieve metadata for such media a `MetadataMissingError` exception will be raised.

### Physical Objects
In MorphoSource a physical object can be associated with multiple media. For example a specific turtle could have different scans of various body parts. The turtle will be represented as a physicial object and each scan will be represented as a media object.
Physical objects have two types [Biological Specimen](https://www.morphosource.org/terms/ms/BiologicalSpecimenObject) and [Cultural Heritage Object](https://www.morphosource.org/terms/ms/CulturalHeritageObject).

#### Search Physical Objects
The `search_objects()` function allows searching biological specimen and/or cultural heritage objects in MorphoSource.

This function is the equivalent of searching in the MorphoSource website with "Objects" chosen:
![morphosource media search](docs/images/morphosource-search-objects.png)

This example searches both physical object types checking all fields for "Fruitadens".
```python
from morphosource import search_objects

results = search_objects("Fruitadens")

for item in results.items:
    print(item.id, item.title, item.type)
```

Example Output:
```console
000390220 LACM:DI:128258 Biological Specimen
000390215 LACM:DI:128258 Biological Specimen
000390210 LACM:DI:128258 Biological Specimen
000390201 LACM:DI:115747 Biological Specimen
```

#### Search Biological Specimens
The `object_type` parameter for `search_objects()` can be used with `ObjectTypes.BIOLOGICAL_SPECIMEN` or `ObjectTypes.CULTURAL_HERITAGE` to filter for a particular object type.

This example searches for biological specimens returning the first 4 physical objects matching the combined filters.
```python
from morphosource import search_objects, ObjectTypes

results = search_objects("U.W,", object_type=ObjectTypes.BIOLOGICAL_SPECIMEN,
                         taxonomy_gbif="Primates", media_type="Mesh",
                         media_tag="Homo naledi", per_page=4, page=1)

for item in results.items:
    print(item.id, item.title)
```

Example Output:
```console
000394512 U.W.110
000394640 U.W.110-11
000394627 U.W.110-10
000394614 U.W.110-9
```

#### Get Physical Object
The `get_object()` function can be used to retrieve details about a single physical object.

In this example we fetch the physical object with id "000394640".
The data property contains all fields returned from the MorphoSource API.

```python
from morphosource import get_object

obj = get_object("000394640")

print(obj.id, obj.title, obj.type)
print(obj.data)
```

Example Output:
```console
000394640 U.W.110-11 Biological Specimen
{'id': ['000394640'], 'title': ['U.W.110-11'], 'organization': ['Centre for the Exploration of the Deep Human Journey'], ...}
```

#### Find Media for a Physical Object
The `get_media_ary()` physical object method returns an array of media associated with the physical object.
By default this includes both open and restricted media.
The `get_media_ary()` `visibility` parameter allows filtering for OPEN or RESTRICTED download media.

```python
from morphosource import get_object, DownloadVisibility

obj = get_object("0000S2086")
for media in obj.get_media_ary(visibility=DownloadVisibility.OPEN):
    print(media.id, media.title)
```

Example Output:
```console
000006433 Femur Proximal [Mesh] [Etc]
000006434 Element Unspecified [Image] [Etc]
```

The zip bundle associated with each media can be downloaded using `media.download_bundle()`.

