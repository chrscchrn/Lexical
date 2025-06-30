import os
from pathlib import Path

from lexical.wordnet import wordnet as W


def find_project_root():
    return Path(__file__).resolve().parent.parent


WORDNET_DATA_DIR = os.path.join(find_project_root(), "lexical", "data")


def test_import_wordnet():
    assert W is not None


def test_response_protocol():
    wordnet_handler = W.WordNetHandler(WORDNET_DATA_DIR)
    ss_types = ["a", "n", "v", "r"]
    for ss_type in ss_types:
        assert ss_type in wordnet_handler._exc
        assert ss_type in wordnet_handler._index
        assert ss_type in wordnet_handler._data

    response = wordnet_handler.call("cat")
    assert response["word"] == "cat"
    assert response["synset_count"] > 0

    assert "n" in response["body"]
    assert "a" in response["body"]
    assert "v" in response["body"]
    assert "r" in response["body"]

    for ss_type in ss_types:
        if len(response["body"][ss_type]) > 0:
            for content in response["body"][ss_type]:
                assert "definition" in content
                assert "examples" in content


def test_data_files_exist():
    data_files = [
        "noun.exc",
        "verb.exc",
        "adj.exc",
        "adv.exc",
        "index.adj",
        "index.noun",
        "index.verb",
        "index.adv",
        "data.adj",
        "data.adv",
        "data.noun",
        "data.verb",
    ]
    for data_file in data_files:
        assert os.path.exists(os.path.join(WORDNET_DATA_DIR, data_file))
