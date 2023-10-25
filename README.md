# pyMorphoSource
Python package for interacting with the [MorphoSource](https://www.morphosource.org/) API.

MorphoSource allows searching for media and physical objects. Each physical object is typically associated with one or more media. There are two types of physical objects in MorphoSource: 1) Biological Specimens and 2) Cultural Heritage Objects. Searching physical objects allows some filtering options not available when searching media.

**Table of Contents**

- [Installation](#installation)
- [Setup](#setup)
- [Examples](#examples)

## Installation

```console
pip install git+https://github.com/Imageomics/pyMorphoSource.git@simple-api
```

## Setup
Downloading files using the MorphoSource API requires an API Key.
To create the API Key:
- Visit https://www.morphosource.org/ create an account
- Click Person icon in top right corner
- Click Dashboard 
- Click Profile 
- Click View API Key under Advanced user functions 
- Copy this value so it can be used in the example python code below


## Examples
### Media

#### Search Media
Searching for media can be done with the `search_media()` function.
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

#### Search and Download Open Media
The `publication` parameter for `search` allows filtering for publication(download permissions).
Example values for `publication` are "Open Download" or "Restricted Download".
To download a media file requires an MorphoSource API key.
This example expects the MorphoSource API key to be supplied via an environment variable.

```python
import os
from morphosource import search_media

API_KEY = os.environ["API_KEY"]

results = search_media("Fruitadens", publication="Open Download")
for media in results.items:
    path = f"{media.id}.zip"
    print(f"Downloading {media.id} {media.title} to {path}")
    media.download_bundle(path=path, api_key=API_KEY)
```

Example Output:
```console
Downloading 000390223 Dentary Teeth [Mesh] [CT] to 000390223.zip
Downloading 000390218 Maxillary Teeth [Mesh] [CT] to 000390218.zip
Downloading 000390213 Maxillary Teeth [Mesh] [CT] to 000390213.zip
Downloading 000390208 Dentary Teeth [Mesh] [CT] to 000390208.zip
Downloading 000390204 Maxillary Teeth [Mesh] [CT] to 000390204.zip
```

#### Search Media Advanced
The  `search_media` has some additional parameters to filter the items returned.
- media_type - str - Type of media (eg. "Mesh")
- publication - str - Publication download status (eg. "Open Download" or "Restricted Download")
- media_tag - str - Tag applied to the meda (eg. "femur")
- object_type - Type of physical object (eg. "Biological Specimen" or "Cultural Heritage Object")

By default `search_media` will fetch all items, which can be slow for certain queries.
To fetch a limited set of items pass the `page` and `per_page` parameters. 

query=None, media_type=None, publication=None, media_tag=None, object_type=None, per_page=None, page=None


This example uses many parameters to search for the first 4 media matching the combined filters.  
```python
from morphosource import search_media

results = search_media("Chalcides",  media_type="Mesh", publication="Open Download", media_tag="pelvis", 
                       object_type="Biological Specimen", per_page=4, page=1)
print("Found", results.pages["total_count"], "items")
for media in results.items:
    print(media.id, media.title)

```

Example Output:
```console
Found 78 items
000429026 Pelvis [Mesh] [CT]
000429008 Pelvis [Mesh] [CT]
000428985 Pelvis [Mesh] [CT]
000428965 Pelvis [Mesh] [CT]
```

#### Get Single Media
Using the `get_media()` function details about single media object can be retreived.

In this example we fetch media with id "000429026".
The data parameter contains all fields returned from the MorphoSource API.
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

### Search biological specimens filtering on all fields
This example will print out the first page of specimens matching the query "salamander".

Create and run a python script following contents:
```python
from morphosource import search_biological_specimens

search_results = search_biological_specimens(query="salamander")
for specimen in search_results.specimens:
    print(specimen.id, specimen.title, specimen.taxonomy)
```

Example Output:
```console
000S27400 usnm:amphibians & reptiles:224212 Chiropterotriton ceronorum
000S27399 mvz:amphibian and reptile specimens:200693 Chiropterotriton perotensis
000S27394 mvz:amphibian and reptile specimens:178706 Chiropterotriton melipona
...
```

### Search biological specimens filtering on taxonomy and file type
This example will print out the first page of specimens and their associated media files.

Filters:
- all fields will be filtered by "Puma"
- taxonomy will be filtered to "Carnivora"
- media type will be filter to "Mesh"
```python
from morphosource import search_biological_specimens

search_results = search_biological_specimens(query="Puma", taxonomy="Carnivora", media_type="Mesh")
for specimen in search_results.specimens:
    print(specimen.id, specimen.title)
    for media in specimen.get_media_ary():
        print(" ", media.id, media.title)
```

Example Output:
```console
000571032 LACM:rlb:P23-32433 
  000571035 Skull [Mesh] [StrLight]
0000S3033 ism:ism-mammals:693928
  000010111 Cranium [Mesh] [Etc]
  000010112 Mandible [Mesh] [Etc]
0000S7641 uf:mammals:25908
  000031935 Humerus [Mesh] [CT]
```

### Download media files associated with a biological specimen
This example will find a specimen and download all associated media file zip bundles with visibility 'open'.
To download a media file requires an MorphoSource API key.
This example expects the MorphoSource API key to be supplied via an environment variable.

Create and a python script with the following contents:
```python
import os
from morphosource import search_biological_specimens

API_KEY = os.environ["API_KEY"]

search_results = search_biological_specimens(query="Puma", taxonomy="Carnivora", media_type="Mesh")
specimen = search_results.specimens[0]

print(f"Downloading all media files for {specimen.title}")
for media in specimen.get_media_ary(open_visibility_only=True):
    path = f"{media.id}.zip"
    print(f"Downloading {media.id} to {path}")
    media.download_bundle(path=path, api_key=API_KEY)
```
Next you need to use the MorphoSource API key created following [Create an API Key instructions](#create-an-api-Key).
To set the API_KEY environment variable run the following filling in your API KEY:
```console
export API_KEY=<MorphoSource-API-Key>
```
Then you can run the python script.

Example Output:
```console
Downloading all media files for LACM:rlb:P23-32433 
Downloading 000571035 to 000571035.zip
```

#### Extract MorphoSource zip file
Extracting the contents of the zip
```console
$ unzip 000571035.zip 
Archive:  000571035.zip
Written using ZipTricks 4.7.1
 extracting: Media 000571035 - Skull Mesh StrLight/P23_32433_Puma_concolor_skull-000571035.zip  
 extracting: ms_usage_std_comm_no_rearc_any_3d_yes.pdf  
 extracting: media-manifest-db2744ee-e052-4980-b22a-7e2dd5678806.xlsx  
 extracting: media-manifest-8b681c20-3cdd-4a1d-8586-479176ec9aa2.csv  
```
The `Media 000571035 - Skull Mesh StrLight/P23_32433_Puma_concolor_skull-000571035.zip` file is our media file and the others are metadata.
Sometimes the media file within the bundle is a regular file for example a `.stl` file, but in this case it was a zip file.

Examining the contents of the nested zip file:
```console
$ unzip 'Media 000571035 - Skull Mesh StrLight/P23_32433_Puma_concolor_skull-000571035.zip' 
Archive:  Media 000571035 - Skull Mesh StrLight/P23_32433_Puma_concolor_skull-000571035.zip
  inflating: P23 32433 Puma concolor skull.jpg  
  inflating: P23 32433 Puma concolor skull.mtl  
  inflating: P23 32433 Puma concolor skull.obj
```
