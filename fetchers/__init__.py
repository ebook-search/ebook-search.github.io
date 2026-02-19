from fetchers.core import (
    get_soup,
    make_book,
    Meta,
    MetaSource,
    FetchResult,
    Database,
    truncate_filename,
)
from fetchers.ilibrary import fetch_ilibrary
from fetchers.unglue import fetch_unglue
from fetchers.standardebooks import fetch_standardebooks

def fetch(meta, output_path):
    table = {
        MetaSource.ILIBRARY: fetch_ilibrary,
        MetaSource.UNGLUE:   fetch_unglue,
        MetaSource.STANDARDEBOOKS: fetch_standardebooks,
    }

    source = meta.source
    return table[source](meta, output_path)
