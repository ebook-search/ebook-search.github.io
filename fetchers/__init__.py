from .ilibrary import fetch_ilibrary
from .unglue import fetch_unglue

def fetch(meta, output_path):
    table = {
        "ilibrary": fetch_ilibrary,
        "unglue": fetch_unglue,
    }

    source = meta["source"]
    table[source](meta, output_path)
