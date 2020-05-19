# Zambian Names

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

---