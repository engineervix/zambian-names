#!/usr/bin/env python3

import os
import pathlib

from datetime import datetime
from string import ascii_lowercase

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

TODAY = datetime.now()


def fetch_names_that_begin_with(letter):
    """
    fetches names that begin with `letter` from the specified URL
    """

    url = f"https://thezambian.com/online/zambian-names-beginning-with-the-letter-{letter}/"

    try:
        webpage = requests.get(url)
        webpage.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        # print ("Oops: An Unexpected Error Occurred", err)
        raise SystemExit(err)

    soup = BeautifulSoup(webpage.text, "html.parser")
    post = soup.find("section", {"class": "entry"})

    try:
        names = [name.text for name in post.find_next("ol").find_all("li")]
    except AttributeError:
        print(f"there are no names that begin with {letter.upper()}")
        names = []

    return names


def print_to_file(names, letter, filename):
    """
    print a list of `names` that begin with `letter` to file named `filename`
    """
    with open(filename, "a") as output:
        print(
            f"## Zambian names beginning with the letter {letter.upper()}\n", file=output,
        )
        # GFM task-list syntax
        output.write("\n".join(str(f"- [ ] {name}") for name in names))
        print("\n", file=output)


def cmd(filename):
    progress_bar = tqdm(ascii_lowercase)
    path = pathlib.Path(filename)
    if path.exists():
        timestamp = TODAY.strftime("%Y%m%d-%H%M%S")
        base, extension = os.path.splitext(filename)
        new_file = f"{base}_{timestamp}{extension}"
    else:
        new_file = filename
    for letter in progress_bar:
        progress_bar.set_description(f"Fetching {letter.upper()} names")
        names = fetch_names_that_begin_with(letter)
        if names:
            print_to_file(names, letter, new_file)


if __name__ == "__main__":
    cmd("zambian_names.md")
