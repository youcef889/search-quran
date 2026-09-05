TEXT = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ"


def _segments(highlight):
    return [(s["match"], s["text"]) for s in highlight["segments"]]


def test_single_word_highlight(tiny_service):
    highlight = tiny_service._highlight_words(TEXT, ["الله"])
    segments = _segments(highlight)
    assert (False, "بِسْمِ ") in segments
    assert (True, "ٱللَّه") in segments
    assert (False, "ِ ٱلرَّحْمَـٰنِ") in segments


def test_multiple_words_highlight(tiny_service):
    highlight = tiny_service._highlight_words(TEXT, ["الله", "الرحمن"])
    matches = [text for match, text in _segments(highlight) if match]
    assert "ٱللَّه" in matches
    assert "ٱلرَّحْمَـٰن" in matches


def test_overlapping_ranges_are_merged(tiny_service):
    # "الرحمن" is found through both dagger-alif variants; ranges merge into
    # a single matched segment.
    highlight = tiny_service._highlight_words(TEXT, ["الرحمن"])
    matches = [text for match, text in _segments(highlight) if match]
    assert matches == ["ٱلرَّحْمَـٰن"]


def test_dagger_alif_variants_are_highlighted(tiny_service):
    for word in ("الرحمن", "الرحمان"):
        highlight = tiny_service._highlight_words(TEXT, [word])
        assert any(match for match, _ in _segments(highlight))


def test_original_text_reconstruction_is_lossless(tiny_service):
    for words in (["الله"], ["الله", "الرحمن"], []):
        highlight = tiny_service._highlight_words(TEXT, words)
        reconstructed = "".join(seg["text"] for seg in highlight["segments"])
        assert reconstructed == TEXT


def test_quranic_marks_and_tashkeel_preserved(tiny_service):
    highlight = tiny_service._highlight_words(TEXT, ["الله"])
    reconstructed = "".join(seg["text"] for seg in highlight["segments"])
    assert "ٱ" in reconstructed
    assert "ٰ" in reconstructed
    assert "ـ" in reconstructed


def test_no_highlight_inside_another_word(tiny_service):
    # "دين" must not match the trailing part of "الدين".
    text = "مَـٰلِكِ يَوْمِ ٱلدِّينِ"
    highlight = tiny_service._highlight_words(text, ["دين"])
    assert not any(match for match, _ in _segments(highlight))


def test_partial_word_does_not_highlight_inside_word(tiny_service):
    # "رحمن" is a subword of "الرحمن" and must not be highlighted.
    highlight = tiny_service._highlight_words(TEXT, ["رحمن"])
    assert not any(match for match, _ in _segments(highlight))


def test_highlight_structure_keys_present(tiny_service):
    highlight = tiny_service._highlight_words(TEXT, ["الله"])
    assert set(highlight) == {"before", "match", "after", "segments"}