from urllib.parse import quote


def _maps_search(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


CARE_LINKS_BY_DOMAIN: dict[str, list[dict[str, str]]] = {
    "healthcare": [
        {
            "label": "Find urgent care near me",
            "url": _maps_search("urgent care near me"),
        },
        {
            "label": "Find primary care doctors near me",
            "url": _maps_search("primary care doctor near me"),
        },
        {
            "label": "Find pharmacies near me",
            "url": _maps_search("pharmacy near me"),
        },
        {
            "label": "CDC guidance (general health information)",
            "url": "https://www.cdc.gov/",
        },
    ],
    "legal": [
        {
            "label": "Find attorneys near me",
            "url": _maps_search("attorney near me"),
        },
        {
            "label": "Find legal aid services near me",
            "url": _maps_search("legal aid near me"),
        },
    ],
    "finance": [
        {
            "label": "Find financial advisors near me",
            "url": _maps_search("certified financial planner near me"),
        },
        {
            "label": "Find tax professionals near me",
            "url": _maps_search("tax professional near me"),
        },
    ],
}

DEFAULT_CARE_LINKS = [
    {
        "label": "Search for experts near me",
        "url": _maps_search("professional services near me"),
    },
]


def get_care_links(domain: str, term: str = "") -> list[dict[str, str]]:
    links = [dict(link) for link in CARE_LINKS_BY_DOMAIN.get(domain, DEFAULT_CARE_LINKS)]

    if domain == "healthcare" and term:
        links.insert(
            0,
            {
                "label": f"Search providers for {term}",
                "url": _maps_search(f"{term} specialist near me"),
            },
        )

    return links
