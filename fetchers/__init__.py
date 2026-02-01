from .ilibrary import fetch_ilibrary
from .unglue import fetch_unglue
from .utils import MetaSource

def fetch(meta, output_path):
    table = {
        MetaSource.ILIBRARY: fetch_ilibrary,
        MetaSource.UNGLUE:   fetch_unglue,
    }

    source = meta.source
    table[source](meta, output_path)
