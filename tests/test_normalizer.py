from services.normalizer import Normalizer


def test_tashkeel_removed():
    assert Normalizer().normalize("بِسْمِ") == "بسم"


def test_alif_variants_normalize_to_bare_alif():
    normalizer = Normalizer()
    assert normalizer.normalize("إ") == "ا"
    assert normalizer.normalize("أ") == "ا"
    assert normalizer.normalize("آ") == "ا"
    assert normalizer.normalize("ٱ") == "ا"


def test_dagger_alif_as_alef_by_default():
    assert Normalizer().normalize("مَـٰلِكِ", dagger_as_alef=True) == "مالك"


def test_dagger_alif_removed_when_disabled():
    assert Normalizer().normalize("مَـٰلِكِ", dagger_as_alef=False) == "ملك"


def test_tatweel_removed():
    assert Normalizer().normalize("مـٰ") == "ما"


def test_other_letter_variants():
    normalizer = Normalizer()
    assert normalizer.normalize("ؤ") == "و"
    assert normalizer.normalize("ئ") == "ي"
    assert normalizer.normalize("ى") == "ي"
    assert normalizer.normalize("ة") == "ه"


def test_whitespace_is_collapsed_and_trimmed():
    assert Normalizer().normalize("  أ ب   ج  ") == "ا ب ج"


def test_bidi_controls_removed():
    # LRM (U+200E) and RLM (U+200F), and bidi embedding controls.
    assert Normalizer().normalize("ا\u200eا\u200f") == "اا"
    assert Normalizer().normalize("ا\u202eب\u202c") == "اب"


def test_quranic_marks_removed():
    # Small high hamza / qur'anic annotation range U+0610-U+061A.
    assert Normalizer().normalize("ا\u0610ب") == "اب"
    assert Normalizer().normalize("ا\u06d6ب") == "اب"


def test_full_verse_normalization():
    text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ"
    expected = "بسم الله الرحمان"
    assert Normalizer().normalize(text, dagger_as_alef=True) == expected
    assert Normalizer().normalize(text, dagger_as_alef=False) == "بسم الله الرحمن"


def test_tokenize_drops_punctuation_and_digits():
    assert Normalizer().tokenize("بِسْمِ 123 ٱللَّهِ") == ["بسم", "الله"]


def test_tokenize_keeps_dagger_alif_tokens():
    assert Normalizer().tokenize("ٰا", dagger_as_alef=True) == ["اا"]


def test_query_tokens_deduplicates_preserving_order():
    assert Normalizer().query_tokens("الله الله الرحمن") == ["الله", "الرحمن"]


def test_query_tokens_empty():
    assert Normalizer().query_tokens("   ") == []
    assert Normalizer().query_tokens("") == []