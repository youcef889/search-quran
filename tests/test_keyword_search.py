def test_single_word_query(tiny_service):
    result = tiny_service.search("الله")
    assert result["total"] == 1
    assert (result["results"][0]["surah"], result["results"][0]["verse"]) == ("1", "1")


def test_multi_word_and_query(tiny_service):
    result = tiny_service.search("الله الرحمن")
    assert result["total"] == 1
    assert (result["results"][0]["surah"], result["results"][0]["verse"]) == ("1", "1")


def test_word_order_is_irrelevant(tiny_service):
    forward = tiny_service.search("الله الرحمن")
    reversed_ = tiny_service.search("الرحمن الله")
    assert forward["total"] == reversed_["total"] == 1
    forward_ids = {(r["surah"], r["verse"]) for r in forward["results"]}
    reversed_ids = {(r["surah"], r["verse"]) for r in reversed_["results"]}
    assert forward_ids == reversed_ids


def test_query_words_need_not_be_adjacent(tiny_service):
    # "الحمد" and "رب" appear in 1:2 with another word between them.
    result = tiny_service.search("الحمد رب")
    assert result["total"] == 1
    assert (result["results"][0]["surah"], result["results"][0]["verse"]) == ("1", "2")


def test_nonexistent_word_returns_nothing(tiny_service):
    assert tiny_service.search("كلمةغيرموجودة")["total"] == 0


def test_empty_query_returns_nothing(tiny_service):
    result = tiny_service.search("   ")
    assert result["total"] == 0
    assert result["page"] == 1
    assert result["pages"] == 0
    assert result["results"] == []


def test_duplicate_query_words_deduplicated(tiny_service):
    single = tiny_service.search("الله")
    duplicate = tiny_service.search("الله الله الله")
    assert duplicate["total"] == single["total"]
    assert [r["verse"] for r in duplicate["results"]] == [r["verse"] for r in single["results"]]


def test_override_hamzated_word_matches(tiny_service):
    # إِيَّاكَ normalizes to اياك, so a plain query matches.
    result = tiny_service.search("اياك")
    assert result["total"] == 1
    assert (result["results"][0]["surah"], result["results"][0]["verse"]) == ("2", "1")


def test_dagger_alif_word_searchable(tiny_service):
    # مَـٰلِكِ -> مالك under the dagger-as-alif variant.
    result = tiny_service.search("مالك")
    assert result["total"] == 1
    assert (result["results"][0]["surah"], result["results"][0]["verse"]) == ("1", "3")


def test_exact_phrase_ranks_first(service):
    # "الله احد" — verses containing the exact phrase (112:1) tie for the
    # top score, and must rank above verses that merely contain both words.
    result = service.search("الله احد", per_page=12)
    assert result["total"] > 3
    scores = [r["score"] for r in result["results"]]
    assert scores[0] == scores[1]
    assert scores[1] > scores[2]
    assert scores == sorted(scores, reverse=True)
    assert (result["results"][1]["surah"], result["results"][1]["verse"]) == ("112", "1")


def test_deterministic_ordering(tiny_service):
    result = tiny_service.search("الله")
    scores = [r["score"] for r in result["results"]]
    assert scores == sorted(scores, reverse=True)


def test_results_are_sorted_by_surah_verse_on_tie(service):
    result = service.search("الله", per_page=100)
    expected_key = lambda r: (-r["score"], int(r["surah"]), int(r["verse"]))
    keys = [expected_key(r) for r in result["results"]]
    assert keys == sorted(keys)