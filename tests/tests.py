#!/usr/bin/env python3

import os
import glob
import random
from pathlib import Path
from string import ascii_lowercase
from shutil import copy, rmtree

import pytest
from faker import Faker

from zambian_names.fetch_names import (
    TODAY,
    fetch_names,
    fetch_names_that_begin_with,
    print_to_file,
    cmd,
)

fake = Faker()

NAMES_LIST = []

ALL_LETTERS = [char for char in ascii_lowercase]
EMPTY_LETTERS = ["q", "r", "x"]
NON_EMPTY_LETTERS = [char for char in ALL_LETTERS if char not in EMPTY_LETTERS]

NON_EMPTY_IDS = [f"letter_{str(char.upper())}" for char in NON_EMPTY_LETTERS]
PRINT_IDS = [f"print_to_file_{str(char.upper())}" for char in NON_EMPTY_LETTERS]
EMPTY_IDS = [f"letter_{str(char.upper())}" for char in EMPTY_LETTERS]

TEST_DIRECTORY = os.path.join(os.getcwd(), "__tests__")


@pytest.fixture
def zambian_names_list(scope="session"):
    the_names = fetch_names()
    return the_names


@pytest.fixture
def prepare_data():
    """Prepare temp directory for testing. Delete afterwards"""
    os.makedirs(TEST_DIRECTORY, exist_ok=True)

    yield  # This is where the testing happens

    # Teardown : discard the data
    # Cleanup
    try:
        rmtree(os.path.join(os.getcwd(), TEST_DIRECTORY))
    except OSError as ex:  # if failed, report it back to the user
        print(f"Error: {ex.filename} - {ex.strerror}.")


@pytest.fixture
def prepare_data_and_sample_file():
    """Prepare temp directory and dummy file for testing. Delete afterwards"""
    os.makedirs(TEST_DIRECTORY, exist_ok=True)
    Path(os.path.join(TEST_DIRECTORY, "zambian_names.md")).touch()

    yield  # This is where the testing happens

    # Teardown : discard the data
    # Cleanup
    try:
        rmtree(os.path.join(os.getcwd(), TEST_DIRECTORY))
    except OSError as ex:  # if failed, report it back to the user
        print(f"Error: {ex.filename} - {ex.strerror}.")


def test_non_empty_lists(zambian_names_list):
    """23 out of 26 letters have names"""
    for letter in NON_EMPTY_LETTERS:
        assert fetch_names_that_begin_with(letter, zambian_names_list)


def test_empty_lists(zambian_names_list):
    """3 out of 26 letters do not have names"""
    for letter in EMPTY_LETTERS:
        assert fetch_names_that_begin_with(letter, zambian_names_list) == []


@pytest.mark.usefixtures("prepare_data")
@pytest.mark.parametrize("letter", NON_EMPTY_LETTERS, ids=PRINT_IDS)
def test_print_to_file(letter):
    """test printing to file"""
    NAMES_LIST.clear()
    for x in range(26):
        NAMES_LIST.append([fake.first_name() for num in list(range(random.randint(25, 88)))])

    print_to_file(NAMES_LIST, os.path.join(TEST_DIRECTORY, "zambian_names.md"))

    # output file shouldn't be empty
    assert os.stat(os.path.join(TEST_DIRECTORY, "zambian_names.md")).st_size > 0

    # output file should have an "h2 heading" corresponding to the `letter`

    with open(os.path.join(TEST_DIRECTORY, "zambian_names.md"), "r") as f_out:
        data = f_out.read()

        assert "## Zambian names beginning with the letter " in data


@pytest.mark.usefixtures("prepare_data_and_sample_file")
def test_cmd_with_existing_file():
    """test program execution"""
    cmd(os.path.join(TEST_DIRECTORY, "zambian_names.md"))

    # existing dummy file should be empty
    assert os.stat(os.path.join(TEST_DIRECTORY, "zambian_names.md")).st_size == 0

    # we should have two files in the TEST_DIRECTORY
    assert len(os.listdir(os.path.join(TEST_DIRECTORY))) == 2

    # we should be writing to a timestamped file
    timestamped_filelist = glob.glob(f"{TEST_DIRECTORY}/*{TODAY.strftime('%Y%m%d')}*")
    assert len(timestamped_filelist) == 1
    with open(timestamped_filelist[0], "r") as f_out:
        assert f_out.read().count("## Zambian names beginning with the letter ") == 23


@pytest.mark.usefixtures("prepare_data")
def test_cmd_without_existing_file():
    """test program execution"""
    cmd(os.path.join(TEST_DIRECTORY, "zambian_names.md"))

    assert len(os.listdir(os.path.join(TEST_DIRECTORY))) == 1

    with open(os.path.join(TEST_DIRECTORY, "zambian_names.md")) as f:
        num_lines = len(f.readlines())

    assert num_lines > 23 * len(NAMES_LIST)
