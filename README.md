# Russian literature -> ebooks

EBook generator from scraped public domain works.
Tested on Linux only, might work in other OSes.

### Sources

- [ilibrary.ru](https://ilibrary.ru)

### Requirements

- all from `requirements.txt`
- pandoc

### Installation

```console
python -m venv venv
(install pandoc)
source venv/bin/activate
python generate_db.py # (update db every update)
```

### Usage

```console
source venv/bin/activate
python main.py
```
