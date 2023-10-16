# pyMorphoSource
Python package for interacting with the [MorphoSource](https://www.morphosource.org/) [API](https://morphosource.stoplight.io/).

**Table of Contents**

- [Installation](#installation)
- [Setup](#setup)
- [Examples](#examples)

## Installation

```console
pip install --upgrade git+https://github.com/Imageomics/pyMorphoSource.git
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
This example searches media checking all all fields for "Fruitadens".
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
The `search_media()` `publication` parameter allows filtering for OPEN or RESTRICTED download media.
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

If you attempt to download restricted media that you have not received permissions for a `RestrictedDownloadError` exception will be raised. Requesting permissions for some media must be done via [MorphoSource](https://www.morphosource.org/).

#### Search Media Advanced
The  `search_media` has some additional parameters to filter the items returned.
- media_type - str - Type of media (eg. "Mesh")
- media_tag - str - Tag applied to the meda (eg. "femur")

This example uses many parameters to search for the first 4 media matching the combined filters.  
```python
from morphosource import search_media

results = search_media("Chalcides",  media_type="Mesh", media_tag="pelvis", per_page=4, page=1)
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
Using the `get_media()` function details about single media object can be retreived.

In this example we fetch media with id "000429026".
The `data` property contains all fields returned from the MorphoSource API.
```python
from morphosource import get_media

media = get_media(media_id="000429026")
print(media.id, media.title)
print(media.data)
```

Example Output;
```console
000429026 Pelvis [Mesh] [CT]
{'id': ['000429026'], 'title': ['Pelvis [Mesh] [CT]'], 'media_type': ['Mesh'], 'modality': ['MicroNanoXRayComputedTomography'], 'device': ['Perkin Elmer Quantum GX2'], ...
```

If the media id isn't found a `morphosource.api.ItemNotFound` exception will be raised.
