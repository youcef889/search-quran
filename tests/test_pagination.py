def test_pagination_returns_distinct_pages(service):
    page1 = service.search("الله", page=1, per_page=10)
    page2 = service.search("الله", page=2, per_page=10)
    assert page1["total"] == page2["total"]
    assert page1["pages"] == (page1["total"] + 9) // 10
    assert page1["page"] == 1
    assert page2["page"] == 2
    assert len(page1["results"]) == 10
    id1 = {(r["surah"], r["verse"]) for r in page1["results"]}
    id2 = {(r["surah"], r["verse"]) for r in page2["results"]}
    assert not (id1 & id2)


def test_page_beyond_last_is_clamped(service):
    result = service.search("الله", page=999999, per_page=50)
    assert result["page"] == result["pages"]
    assert result["results"]


def test_per_page_respected(service):
    result = service.search("الله", page=1, per_page=7)
    assert len(result["results"]) == 7


def test_highlights_only_apply_to_returned_page(service):
    page1 = service.search("الله", page=1, per_page=5)
    assert all("highlight" in r for r in page1["results"])


def test_zero_per_page_does_not_divide_by_zero(service):
    result = service.search("الله", page=1, per_page=0)
    assert result["per_page"] == 1
    assert len(result["results"]) == 1