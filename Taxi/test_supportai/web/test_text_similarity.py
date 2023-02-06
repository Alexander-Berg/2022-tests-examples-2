import pytest

from supportai.common.antifrod import text_simirality


def test_levenshtein_similarity():
    first_text = ''
    second_text = ''
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(1.0, rel=1e-3)

    first_text = 'hello'
    second_text = ''
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(0.0, rel=1e-3)

    first_text = ''
    second_text = 'hello'
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(0.0, rel=1e-3)

    first_text = 'hello'
    second_text = 'hello'
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(1.0, rel=1e-3)

    first_text = 'yandex plotva-ml'
    second_text = 'yandex supportai'
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(0.5, rel=1e-3)

    first_text = 'yandex plotva-ml-taxi-old'
    second_text = 'yandex supportai-taxi-not-old'
    assert text_simirality.SimilarityMeter.levenshtein_similarity(
        first_text, second_text,
    ) == pytest.approx(0.5862, rel=1e-3)


def test_jaccard_similarity():
    first_text = ''
    second_text = ''
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(1.0, rel=1e-3)

    first_text = 'hello'
    second_text = ''
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(0.0, rel=1e-3)

    first_text = ''
    second_text = 'hello'
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(0.0, rel=1e-3)

    first_text = 'hello'
    second_text = 'hello'
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(1.0, rel=1e-3)

    first_text = 'yandex plotva-ml'
    second_text = 'yandex supportai'
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(1 / 3, rel=1e-3)

    first_text = 'yandex plotva ml taxi old!!!  '
    second_text = 'yandex supportai taxi not really old'
    assert text_simirality.SimilarityMeter.jaccard_similarity(
        first_text, second_text,
    ) == pytest.approx(2 / 9, rel=1e-3)
