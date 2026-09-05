def test_exact_verse_matches_top(tiny_service):
    # Typing the verse with its full orthography (tashkeel + dagger alif)
    # normalizes to an exact match.
    result = tiny_service.search_by_passage("بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ")
    assert result["total"]
    top = result["results"][0]
    assert (top["surah"], top["verse"]) == ("1", "1")
    assert top["score"] == 100


def test_partial_verse_input(tiny_service):
    result = tiny_service.search_by_passage("بسم الله")
    top = result["results"][0]
    assert (top["surah"], top["verse"]) == ("1", "1")
    assert top["score"] > 90


def test_verse_without_diacritics(tiny_service):
    # Dropping tashkeel and writing a plain الرحمن still finds the verse.
    result = tiny_service.search_by_passage("بسم الله الرحمن")
    top = result["results"][0]
    assert (top["surah"], top["verse"]) == ("1", "1")
    assert top["score"] >= 96


def test_minor_typo_still_matches(tiny_service):
    result = tiny_service.search_by_passage("بسم الله الرحمي", threshold=80)
    assert result["total"]
    assert result["results"][0]["verse"] == "1"


def test_nonexistent_passage_returns_nothing(tiny_service):
    result = tiny_service.search_by_passage("صصص عععع وووو", threshold=65)
    assert result["total"] == 0
    assert result["results"] == []


def test_threshold_excludes_lower_scores(tiny_service):
    low = tiny_service.search_by_passage("بسم الله", threshold=65)
    high = tiny_service.search_by_passage("بسم الله", threshold=100)
    assert low["total"] >= high["total"]


def test_result_limit_is_honored(tiny_service):
    result = tiny_service.search_by_passage("بسم الله الرحمن", threshold=60, limit=1)
    assert len(result["results"]) == 1


def test_short_verses_not_falsely_flagged(service):
    """Regression: partial_ratio used to score a short verse (e.g. 40:1 "حم")
    at 100 whenever its text was a substring of the query."""
    result = service.search_by_passage("بسم الله الرحمن", threshold=75)
    assert ("40", "1") not in {(r["surah"], r["verse"]) for r in result["results"]}


def test_original_verse_text_is_returned_untouched(tiny_service):
    result = tiny_service.search_by_passage("بسم الله الرحمن")
    stored = tiny_service.get_verse("1", "1")
    assert result["results"][0]["text"] == stored


def test_basmala_found_on_real_data(service):
    result = service.search_by_passage("بسم الله الرحمن الرحيم", threshold=90)
    assert result["total"]
    assert result["results"][0]["score"] >= 90