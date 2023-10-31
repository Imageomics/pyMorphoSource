# Fetches multiple pages of results from a MorphoSource API
import requests

DEFAULT_PER_PAGE = 10
PER_PAGE_PARAM = "per_page"
PAGE_PARAM = "page"
QUERY_PARAM = "q"
SEARCH_FIELD_PARAM = "search_field"
SEARCH_ALL_FIELDS_VALUE = "all_fields"


def fetch_one_page(url, params, per_page, page):
    request_params = params.copy()
    if not per_page:
        per_page = DEFAULT_PER_PAGE
    request_params.update({PER_PAGE_PARAM: per_page, PAGE_PARAM: page})
    response = requests.get(url, params=request_params)
    response.raise_for_status()
    return response.json()['response']


def fetch_item(url, params={}):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['response']


def fetch_all_pages(url, params, per_page, items_name):
    page = 1
    items = []
    facets = []
    pages = []
    while True:
        data = fetch_one_page(url, params, per_page=per_page, page=page)
        items.extend(data[items_name])
        facets = data['facets']
        pages = data['pages']
        total_pages = data['pages'].get('total_pages')
        if total_pages <= page:
            break
        page += 1
    return items, facets, pages


def fetch_items(url, query, params, per_page, page, items_name):
    if query:
        params[SEARCH_FIELD_PARAM] = SEARCH_ALL_FIELDS_VALUE
        params[QUERY_PARAM] = query
    if page:
        data = fetch_one_page(url, params, per_page, page)
        return data[items_name], data['facets'], data['pages']
    else:
        return fetch_all_pages(url, params, per_page, items_name)
