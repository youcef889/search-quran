from flask import Blueprint, current_app, jsonify, render_template, request

search = Blueprint("search", __name__)


def _query_param() -> str:
    value = request.args.get("q", "").strip()
    return value[: current_app.config["MAX_QUERY_LENGTH"]]


def _int_param(name: str, default: int, minimum: int = 1, maximum: int | None = None) -> int:
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default
    value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


@search.route("/search")
def search_page():
    query = _query_param()
    page = _int_param("page", current_app.config["DEFAULT_PAGE"], 1, current_app.config["MAX_PAGE"])
    per_page = _int_param("per_page", current_app.config["DEFAULT_PER_PAGE"], 1, current_app.config["MAX_PER_PAGE"])

    service = current_app.extensions["quran_search"]
    result = service.search(query=query, page=page, per_page=per_page)

    return render_template(
        "search.html",
        query=query,
        results=result["results"],
        page=result["page"],
        pages=result["pages"],
        total=result["total"],
    )


@search.route("/search/json")
def search_json():
    """JSON variant of the keyword search, for programmatic clients.

    Returns the exact same result structure produced by the search service.
    """
    query = _query_param()
    page = _int_param("page", current_app.config["DEFAULT_PAGE"], 1, current_app.config["MAX_PAGE"])
    per_page = _int_param("per_page", current_app.config["DEFAULT_PER_PAGE"], 1, current_app.config["MAX_PER_PAGE"])

    service = current_app.extensions["quran_search"]
    result = service.search(query=query, page=page, per_page=per_page)

    return jsonify(result)


@search.route("/search/passage")
def search_passage_page():
    query = _query_param()
    threshold = _int_param(
        "threshold",
        current_app.config["DEFAULT_THRESHOLD"],
        current_app.config["MIN_THRESHOLD"],
        current_app.config["MAX_THRESHOLD"],
    )
    limit = _int_param(
        "limit",
        current_app.config["DEFAULT_PASSAGE_LIMIT"],
        1,
        current_app.config["MAX_PASSAGE_LIMIT"],
    )

    service = current_app.extensions["quran_search"]
    result = service.search_by_passage(query=query, threshold=threshold, limit=limit)

    return render_template(
        "search_passage.html",
        query=query,
        results=result["results"],
        total=result["total"],
    )