#!/usr/bin/env python3

import asyncio
import os
import pathlib
from datetime import datetime
from string import ascii_lowercase

from playwright.async_api import Browser, Page, TimeoutError, async_playwright

TODAY = datetime.now()
# Concurrency limit: How many browsers to run at once.
CONCURRENCY_LIMIT = 5
SELECTOR = ".nv-content-wrap.entry-content ol li"


def url_list() -> list[str]:
    """Create a list of URLs from which to download the names."""
    return [
        f"https://thezambian.com/online/zambian-names-beginning-with-the-letter-{letter}/" for letter in ascii_lowercase
    ]


async def extract_names_from_page(page: Page) -> list[str]:
    """
    Extract Zambian names from the page using Playwright selectors.
    """
    names = []
    name_elements = await page.query_selector_all(SELECTOR)
    if name_elements:
        for element in name_elements:
            name_text = await element.inner_text()
            if name_text.strip():
                names.append(name_text.strip())
    return names


async def scrape_url(
    browser: Browser, url: str, letter: str, semaphore: asyncio.Semaphore, test_timeout: int | None = None
) -> tuple[str, list[str]]:
    """
    Scrapes a single URL, respecting the semaphore to limit concurrency.
    """
    # This will wait until a "slot" is free in the semaphore
    async with semaphore:
        context = await browser.new_context()
        page = await context.new_page()
        print(f"Starting fetch for letter '{letter}'...")

        names = []
        try:
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")

            # Use a shorter timeout for tests if provided
            timeout = test_timeout if test_timeout is not None else 30000
            await page.wait_for_selector(SELECTOR, timeout=timeout)

            names = await extract_names_from_page(page)

            if names:
                print(f"\tFound {len(names)} names for letter '{letter}'.")
            else:
                print(f"\tContent loaded, but no names found for letter '{letter}'.")

        except TimeoutError:
            # Save a screenshot on failure for debugging
            screenshot_path = f"error_page_{letter}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Timed out for letter '{letter}'. See '{screenshot_path}' for details.")
            return letter, []
        except Exception as e:
            print(f"An error occurred for letter '{letter}': {e}")
            return letter, []
        finally:
            await context.close()

        return letter, names


async def fetch_names() -> list[list[str]]:
    """
    Fetches names from all URLs, using a semaphore to limit parallelism.
    """
    # Create the semaphore to control concurrency
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks = []
        urls = url_list()
        for i, url in enumerate(urls):
            letter = ascii_lowercase[i].upper()
            # Pass the semaphore to each task
            tasks.append(scrape_url(browser, url, letter, semaphore))

        results = await asyncio.gather(*tasks)

        await browser.close()

    return [names for letter, names in results]


def print_to_file(names_lists: list[list[str]], filename: str):
    """
    Print a list of names grouped by letter to the specified file.
    """
    with open(filename, "w") as output:
        print("# Zambian Names\n", file=output)
        for idx, name_list in enumerate(names_lists):
            if name_list:  # some lists may be empty (Q, R and X at the time of writing this)
                letter = ascii_lowercase[idx].upper()
                print(
                    f"## Zambian names beginning with the letter {letter}\n",
                    file=output,
                )
                # GFM task-list syntax
                output.write("\n".join(f"- [ ] {name}" for name in name_list))
                print("\n", file=output)


async def main(filename: str):
    """
    Main async command function to fetch names and save them to a file.
    """
    path = pathlib.Path(filename)
    if path.exists():
        timestamp = TODAY.strftime("%Y%m%d-%H%M%S")
        base, extension = os.path.splitext(filename)
        new_file = f"{base}_{timestamp}{extension}"
        print(f"File '{filename}' exists. Saving to new file: '{new_file}'")
    else:
        new_file = filename

    names_lists = await fetch_names()
    if any(names_lists):
        print_to_file(names_lists, new_file)
        print(f"\nSuccessfully saved names to '{new_file}'")
    else:
        print("\nNo names were scraped. The output file was not created.")


if __name__ == "__main__":
    asyncio.run(main("zambian_names.md"))
