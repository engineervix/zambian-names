#!/usr/bin/env python3

from string import ascii_lowercase
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

progress_bar = tqdm(ascii_lowercase)
for letter in progress_bar:
    progress_bar.set_description(f"Fetching {letter.upper()} names")
    url = f"https://thezambian.com/online/zambian-names-beginning-with-the-letter-{letter}/"
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    post = soup.find("section", {"class": "entry"})
    try:
        names = [name.text for name in post.find_next("ol").find_all("li")]
    except AttributeError:
        names = []

    with open("zambian_names.md", "a") as output:
        if names:
            print(f"## Zambian names beginning with the letter {letter.upper()}\n", file=output)
            output.write("\n".join(str(name) for name in names))
            print(f"\n", file=output)
