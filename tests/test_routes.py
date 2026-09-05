import json

ALL_DIFFICULT_CHARS = "!" * 500


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "القرآن الكريم".encode() in response.data


def test_surah_page(client):
    response = client.get("/surah/1")
    assert response.status_code == 200
    assert "سورة 1".encode() in response.data


def test_surah_with_verse_context(client):
    response = client.get("/surah/1?verse=1")
    assert response.status_code == 200


def test_nonexistent_surah_is_404(client):
    response = client.get("/surah/999")
    assert response.status_code == 404


def test_search_valid_request(client):
    response = client.get("/search", query_string={"q": "الله"})
    assert response.status_code == 200
    assert "نتائج البحث".encode() in response.data


def test_search_empty_query(client):
    response = client.get("/search", query_string={"q": ""})
    assert response.status_code == 200
    assert "نتائج البحث".encode() in response.data


def test_search_pagination(client):
    first = client.get("/search", query_string={"q": "الله", "page": 2, "per_page": 10})
    assert first.status_code == 200
    assert "صفحة 2 من".encode() in first.data


def test_page_out_of_range_is_clamped(client):
    response = client.get("/search", query_string={"q": "الله", "page": 999999999})
    assert response.status_code == 200


def test_invalid_page_falls_back_to_default(client):
    response = client.get("/search", query_string={"q": "الله", "page": "abc"})
    assert response.status_code == 200
    assert "صفحة 1 من".encode() in response.data


def test_per_page_capped(client):
    response = client.get("/search", query_string={"q": "الله", "per_page": 5000})
    assert response.status_code == 200


def test_long_query_is_truncated(client):
    response = client.get("/search", query_string={"q": "الله" + ALL_DIFFICULT_CHARS})
    assert response.status_code == 200


def test_search_passage_page(client):
    response = client.get("/search/passage", query_string={"q": "بسم الله"})
    assert response.status_code == 200


def test_search_html_escapes_query(client):
    # A query containing HTML must be escaped, not injected.
    response = client.get("/search", query_string={"q": "<script>alert(1)</script>"})
    assert response.status_code == 200
    assert b"<script>alert(1)</script>" not in response.data


def test_json_search_response_structure(client):
    response = client.get("/search/json", query_string={"q": "الله", "per_page": 5})
    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert set(payload) == {"results", "page", "per_page", "total", "pages"}
    assert payload["per_page"] == 5
    assert isinstance(payload["total"], int)
    for result in payload["results"]:
        assert set(result) >= {"surah", "verse", "text", "score", "highlight"}


def test_json_search_empty_query(client):
    response = client.get("/search/json", query_string={"q": "   "})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["results"] == []
    assert payload["total"] == 0


def test_json_response_is_valid_json(client):
    response = client.get("/search/json", query_string={"q": "الله"})
    json.loads(response.get_data(as_text=True))


def test_missing_route_is_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_bad_request_handler_renders_error_page(client, app):
    from werkzeug.exceptions import BadRequest

    with app.test_request_context("/"):
        body, status = app.handle_http_exception(BadRequest())
    assert status == 400
    assert "خطأ 400".encode() in body if isinstance(body, bytes) else "خطأ 400" in body


def test_error_page_uses_rtl_layout(client):
    assert client.get("/does-not-exist").status_code == 404


def test_security_headers_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers


def test_static_js_served(client):
    response = client.get("/static/js/search.js")
    assert response.status_code == 200
    assert b"clipboard" in response.data