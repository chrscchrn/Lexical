import pytest
from lexical.wordnet.wordnet import WordNetHandler

def test_lookup_brazen():
    handler = WordNetHandler()
    results = handler.lookup_v2("brazen")
    # We expect at least one definition for 'brazen'
    assert isinstance(results, list)
    assert results, "No definitions returned for 'brazen'"
    # Check that 'brazen' or its lemma is in the result base words
    found = any('brazen' in str(item).lower() for item in results)
    assert found, f"'brazen' not found in any definition result: {results}"
    print(f"Definitions for 'brazen': {results}")
