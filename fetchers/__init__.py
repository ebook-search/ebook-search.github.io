from .ilibrary import fetch_ilibrary

def fetch(meta, output_path):
    table = {
        "ilibrary": fetch_ilibrary,
    }

    source = meta["source"]
    table[source](meta, output_path)
