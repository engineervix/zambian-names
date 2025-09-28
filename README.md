# Zambian Names

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

[![python3](https://img.shields.io/badge/python-3.12%20%7C%203.13-brightgreen.svg)](https://python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## What is this about?

The purpose of this project is to have a comprehensive collection of Zambian names that can be used in a variety of contexts. The project was born as a result of seeking to contribute to [`joke2k`](https://github.com/joke2k/)'s **Faker** by creating an [`en_ZM`](https://www.localeplanet.com/icu/en-ZM/index.html) locale so that _Faker_ can be used to generate Zambian specific data, such as names, addresses, etc.

When I did a quick [Google search](https://www.google.com/search?q=Zambian+Names) on May 19<sup>th</sup>, 2020, I found that [thezambian.com](https://thezambian.com/online/zambian-names/) had a more comprehensive list of names, which were arranged in alphabetical order. However, these names had no indication of

1. whether they were first names or last names (or both)
2. gender

I decided to create this project in an attempt to resolve the above two issues, which I perceive to be important factors in the **Faker** package.

## First Step

The first thing to do is fetch the names from `thezambian.com`! The python script [`fetch_names.py`](./fetch_names.py) does exactly this. It uses [requests](https://github.com/psf/requests) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to achieve this. The fetched names are saved in the file [`zambian_names.md`](./zambian_names.md).

## Categorizing names by gender and first/last name

TODO

## Development

- clone the repo
- in your python 3.13 virtual environment, install the dependencies

```bash
pip install -r requirements.txt
```

- Install the required browsers

```bash
playwright install
```

- Run the script to fetch names

```bash
python zambian_names/fetch_names.py
```

---
