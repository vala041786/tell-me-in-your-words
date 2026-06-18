from backend.services.care_navigation import get_care_links


def test_healthcare_care_links_include_maps_search():
    links = get_care_links("healthcare", "Shingles")

    assert links[0]["label"] == "Search providers for Shingles"
    assert "google.com/maps/search" in links[0]["url"]
    assert any("urgent care" in link["label"].lower() for link in links)


def test_legal_care_links_include_attorney_search():
    links = get_care_links("legal")

    assert any("attorney" in link["label"].lower() for link in links)
    assert all(link["url"].startswith("https://") for link in links)
