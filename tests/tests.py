import asyncio
import os
from pathlib import Path
from shutil import rmtree
from string import ascii_lowercase

import pytest
from faker import Faker
from playwright.async_api import async_playwright

from zambian_names.fetch_names import (
    TODAY,
    extract_names_from_page,
    fetch_names,
    main,
    print_to_file,
    scrape_url,
    url_list,
)

fake = Faker()

# --- Constants ---
TEST_DIRECTORY = Path(__file__).parent / "__tests__"
MOCK_HTML_PATH = Path(__file__).parent / "test.html"
EMPTY_HTML_PATH = Path(__file__).parent / "empty.html"


# --- Fixtures ---
@pytest.fixture
def zambian_names_list() -> list[list[str]]:
    """MOCKED DATA FIXTURE for testing high-level file-writing logic."""
    names_data = []
    for letter in ascii_lowercase:
        if letter in ["q", "r", "x"]:
            names_data.append([])
        else:
            names_data.append([fake.first_name() for _ in range(10)])
    return names_data


@pytest.fixture
def temp_test_dir():
    """
    Creates a temp directory, changes into it, yields, then cleans up.
    """
    TEST_DIRECTORY.mkdir(exist_ok=True)
    cwd = Path.cwd()
    os.chdir(TEST_DIRECTORY)
    yield TEST_DIRECTORY
    os.chdir(cwd)
    rmtree(TEST_DIRECTORY)


# --- Unit Tests for Helper Functions ---


def test_url_list():
    """Tests that the URL list is generated correctly."""
    urls = url_list()
    assert len(urls) == 26
    assert urls[0].endswith("-a/")


@pytest.mark.asyncio
async def test_extract_names_from_page_with_mock_html():
    """Tests the core scraping logic of extract_names_from_page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(MOCK_HTML_PATH.resolve().as_uri())
        names = await extract_names_from_page(page)
        await browser.close()
        assert names == ["Towela", "Twaambo", "Temwani"]


@pytest.mark.asyncio
async def test_extract_names_from_page_no_names():
    """Tests extract_names_from_page when no names are on the page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{EMPTY_HTML_PATH}")
        names = await extract_names_from_page(page)
        await browser.close()
        assert names == []


# --- Integration Tests for Scraping Functions ---


@pytest.mark.asyncio
async def test_scrape_url_success():
    """Tests the SUCCESS path of scrape_url with a local HTML file."""
    semaphore = asyncio.Semaphore(1)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        letter, names = await scrape_url(browser, f"file://{MOCK_HTML_PATH}", "T", semaphore)
        await browser.close()
    assert letter == "T"
    assert names == ["Towela", "Twaambo", "Temwani"]


@pytest.mark.asyncio
async def test_scrape_url_timeout_and_screenshot(temp_test_dir):
    """
    Tests the TIMEOUT path of scrape_url and asserts screenshot exists.
    """
    fail_html_path = temp_test_dir / "fail.html"
    fail_html_path.write_text("<html><body><p>No names here</p></body></html>")

    semaphore = asyncio.Semaphore(1)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Use a very short timeout for testing the timeout logic
        letter, names = await scrape_url(browser, f"file://{fail_html_path}", "F", semaphore, test_timeout=10)
        await browser.close()

    assert letter == "F"
    assert names == []
    assert Path("error_page_F.png").exists()


@pytest.mark.asyncio
async def test_scrape_url_empty_list_found(temp_test_dir):
    """NEW: Covers the case where the list element exists but is empty."""
    semaphore = asyncio.Semaphore(1)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Use a very short timeout for testing the timeout logic
        letter, names = await scrape_url(browser, f"file://{EMPTY_HTML_PATH}", "E", semaphore, test_timeout=10)
        await browser.close()
    assert letter == "E"
    assert names == []
    # The screenshot should be created because of the timeout
    assert Path("error_page_E.png").exists()


@pytest.mark.asyncio
async def test_scrape_url_general_exception(mocker):
    """Tests that scrape_url handles generic exceptions gracefully."""
    semaphore = asyncio.Semaphore(1)
    mocker.patch(
        "zambian_names.fetch_names.extract_names_from_page",
        side_effect=Exception("Test error"),
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        letter, names = await scrape_url(browser, f"file://{MOCK_HTML_PATH}", "E", semaphore)
        await browser.close()

    assert letter == "E"
    assert names == []


@pytest.mark.asyncio
async def test_fetch_names_orchestration(mocker):
    """
    Tests the orchestration logic of fetch_names.
    """

    # Configure the mock to return a value that can be unpacked.
    async def mock_scrape_effect(browser, url, letter, semaphore, test_timeout=None):
        return (letter, [f"fake_name_for_{letter}"])

    mock_scrape = mocker.patch("zambian_names.fetch_names.scrape_url", side_effect=mock_scrape_effect)

    result_lists = await fetch_names()

    assert mock_scrape.call_count == 26
    assert len(result_lists) == 26
    assert result_lists[0][0] == "fake_name_for_A"


# --- Tests for `main` function (File I/O) ---


def test_print_to_file(temp_test_dir, zambian_names_list):
    """
    Tests the file-writing logic of print_to_file with mocked data.
    """
    filename = "test_output.md"
    print_to_file(zambian_names_list, filename)

    assert Path(filename).exists()
    assert Path(filename).stat().st_size > 0

    content = Path(filename).read_text()

    assert content.count("## Zambian names beginning with the letter ") == 23


@pytest.mark.asyncio
async def test_main_no_names_found(temp_test_dir, mocker, capsys):
    output_file = Path.cwd() / "zambian_names.md"
    mocker.patch("zambian_names.fetch_names.fetch_names", return_value=[[] for _ in range(26)])
    await main(str(output_file))
    captured = capsys.readouterr()
    assert "No names were scraped" in captured.out
    assert not output_file.exists()


@pytest.mark.asyncio
async def test_main_with_existing_file(temp_test_dir, mocker, zambian_names_list):
    existing_file = Path.cwd() / "zambian_names.md"
    existing_file.touch()
    mocker.patch("zambian_names.fetch_names.fetch_names", return_value=zambian_names_list)
    await main(str(existing_file))
    assert len(list(Path.cwd().iterdir())) == 2
    timestamped_files = list(Path.cwd().glob(f"*{TODAY.strftime('%Y%m%d')}*"))
    assert len(timestamped_files) == 1


@pytest.mark.asyncio
async def test_main_without_existing_file(temp_test_dir, mocker, zambian_names_list):
    output_file = Path.cwd() / "zambian_names.md"
    mocker.patch("zambian_names.fetch_names.fetch_names", return_value=zambian_names_list)
    await main(str(output_file))
    assert len(list(Path.cwd().iterdir())) == 1
    assert output_file.exists()


@pytest.mark.asyncio
async def test_main_function_no_names_scraped(mocker, temp_test_dir, capsys):
    """
    Tests that the main function handles the case where no names are scraped
    and doesn't create an output file.
    """
    mocker.patch("zambian_names.fetch_names.fetch_names", return_value=[[] for _ in range(26)])
    output_file = "no_names.md"

    await main(output_file)

    captured = capsys.readouterr()
    assert "No names were scraped" in captured.out
    assert not Path(output_file).exists()


@pytest.mark.asyncio
async def test_main_function_file_exists(zambian_names_list, temp_test_dir, capsys, mocker):
    """
    Tests that the main function creates a new timestamped file if the
    target file already exists.
    """
    # Mock fetch_names to return our test data
    mocker.patch("zambian_names.fetch_names.fetch_names", return_value=zambian_names_list)

    original_filename = "existing_names.md"
    Path(original_filename).write_text("This file already exists.")

    await main(original_filename)

    captured = capsys.readouterr()
    assert f"File '{original_filename}' exists." in captured.out

    # Check that a new file with a timestamp was created
    files = list(Path(".").glob("existing_names_*.md"))
    assert len(files) == 1
    new_file = files[0]
    assert new_file.exists()
    assert TODAY.strftime("%Y%m%d") in new_file.name

    # Verify the content of the new file
    content = new_file.read_text()
    assert "## Zambian names beginning with the letter A" in content
    assert "## Zambian names beginning with the letter Z" in content
    assert "## Zambian names beginning with the letter Q" not in content
