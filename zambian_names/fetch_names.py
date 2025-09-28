#!/usr/bin/env python3

import os
import pathlib

from datetime import datetime
from string import ascii_lowercase

import grequests  # asynchronous HTTP Requests
from bs4 import BeautifulSoup

TODAY = datetime.now()
LETTERS = {letter: str(index) for index, letter in enumerate(ascii_lowercase, start=0)}


def alphabet_position(letter):
    """determine index of specified letter in the alphabet

    for example, index of letter A is 0; that of C is 2, etc.

    """
    letter = letter.lower()

    numbers = [LETTERS[character] for character in letter if character in LETTERS]

    return int("".join(numbers))


def url_list():
    """create a list of URLs from which to download the names"""
    return [
        f"https://thezambian.com/online/zambian-names-beginning-with-the-letter-{letter}/" for letter in ascii_lowercase
    ]


def exception_handler(request, exception):
    print("Request failed")


def fetch_names():
    """
    fetches names from the url_List
    """

    names_links = [grequests.get(link) for link in url_list()]
    resp = grequests.imap(names_links, exception_handler=exception_handler)

    names_lists = []

    for idx, r in enumerate(resp):
        soup = BeautifulSoup(r.text, "html.parser")
        post = soup.find("section", {"class": "entry"})

        try:
            names = [name.text for name in post.find_next("ol").find_all("li")]
        except AttributeError:
            print(f"there are no names that begin with {ascii_lowercase[idx].upper()}")
            names = []

        names_lists.append(names)

    return names_lists


def fetch_names_that_begin_with(letter, list_of_names):
    """retrieve names that begin with `letter` from `list_of_names`"""
    idx = alphabet_position(letter)
    return list_of_names[idx]


def print_to_file(names_lists, filename):
    """
    print a list of names grouped by letter to file named `filename`
    """
    with open(filename, "a") as output:
        for idx, _list in enumerate(names_lists):
            if _list:  # some lists may be empty (Q, R and X at the time of writing this)
                print(
                    f"## Zambian names beginning with the letter {ascii_lowercase[idx].upper()}\n",
                    file=output,
                )
                # GFM task-list syntax
                output.write("\n".join(str(f"- [ ] {name}") for name in _list))
                print("\n", file=output)


def cmd(filename):
    path = pathlib.Path(filename)
    if path.exists():
        timestamp = TODAY.strftime("%Y%m%d-%H%M%S")
        base, extension = os.path.splitext(filename)
        new_file = f"{base}_{timestamp}{extension}"
    else:
        new_file = filename
    names_lists = fetch_names()
    print_to_file(names_lists, new_file)


if __name__ == "__main__":
    cmd("them_zambian_names.md")
