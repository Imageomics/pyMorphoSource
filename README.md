# pyMorphoSource
Python package for interacting with the MorphoSource API.

-----

**Table of Contents**

- [Installation](#installation)
- [Setup](#setup)
- [Examples](#examples)
- [API](#api)
- [License](#license)

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

MS_API_KEY = os.environ["API_KEY"]

search_results = search_biological_specimens(query="Puma", taxonomy="Carnivora", media_type="Mesh")
specimen = search_results.specimens[0]

print(f"Downloading all media files for {specimen.title}")
for media in specimen.get_media_ary(open_visibility_only=True):
    path = f"{media.id}.zip"
    print(f"Downloading {media.id} to {path}")
    media.download_bundle(path=path, api_key=MS_API_KEY)
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

## API
### search_biological_specimens
Function retrieves one page of physicial objects of type 'Biological Specimen' filtered using the supplied parameters.

__search_biological_specimens__(query, taxonomy, media_type, per_page, page) -> *SpecimenSearchResults*

> Returns an object that contains a list of BiologicalSpecimen objects, a list of facets, and paging information.
    
Parameters:
- __query__ - str that filters on all physicial object fields - optional
- __taxonomy__ - str parameter to filter based on Taxonomy (GBIF) - example value `Carnivora` - optional
- __media_type__ - str parameter to filter based on Media Type - example value `Mesh` - optional
- __per_page__ - int how many items are returned in each page - optional (default is 10)
- __page__ - int page number to fetch - optional (default is 1)

### SpecimenSearchResults
Object represents one page of biological specimen search results.

Properties:
- __specimens__ - list of BiologicalSpecimen objects
- __pages__ - dictionary of paging information - Example value `{'current_page': 1, 'next_page': 2, 'prev_page': None, 'total_pages': 163, 'limit_value': 10, 'offset_value': 0, 'total_count': 1624, 'first_page?': True, 'last_page?': False}`
- __facets__ - list of dictionaries where each dictionary is a field that can be filtered via the MorphoSource UI

### BiologicalSpecimen
Object represents a single biological specimen.

Properties:
- __id__ - str unique id for this physical object
- __title__ - str specimen title
- __taxonomy__ - str Taxonomy (GBIF)
- __data__ - dictionary of all values associated with the specimen

Methods:
#### get_media_ary
>  Returns the list of media associated with a specimen.
__get_media_ary__(open_visibility_only) -> *[Media]*
Parameters:
- __open_visibility_only__ - boolean to only return media with 'open' visibility - optional (default is False)

### Media
Object represents a file downloadable from MorphoSource.
To download the visibilty property must be 'open' or the user has received permissions to download.

Properties:
- __id__ - str unique id for this media object
- __title__ - str media title
- __media_type__ - str type of media
- __visibility__ - str either 'open' or 'restricted_download'
- __data__ - dictionary of all values associated with the media

Methods:
#### download_bundle
Download the zip bundle to the specified __path__. The bundle includes the media file and several metadata files.

__download_bundle__(path, api_key, use_statement, use_categories, use_category_other)

Parameters:
- __path__ - path for where to save the zip file - required
- __api_key__ - MorphoSource Api Key (See [Setup](#setup)) - required
- __use_statement__ - Description of the reason for downloading - optional (default is `Downloading this data as part of a research project.`)
- __use_categories__ - Cateogories of use - optional (default is ["Research"])
- __use_category_other__ - Text description of use category - optional (default is None)

## License

`morphosource` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
