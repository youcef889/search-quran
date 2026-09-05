from flask import Blueprint, abort, current_app, render_template, request

main = Blueprint("main", __name__)


@main.route("/")
def index():
    service = current_app.extensions["quran_search"]
    return render_template(
        "index.html",
        surahs=service.get_surahs(),
    )


@main.route("/surah/<int:surah_id>")
def surah(surah_id: int):
    service = current_app.extensions["quran_search"]

    if not service.get_surah(surah_id):
        abort(404)

    verse_id = request.args.get("verse", type=int)

    if verse_id:
        verses = service.get_verse_context(surah_id, verse_id, before=3, after=3)
    else:
        verses = [
            {"number": int(number), "text": text, "selected": False}
            for number, text in service.get_surah(surah_id).items()
        ]

    return render_template(
        "index.html",
        surahs=service.get_surahs(),
        current_surah=surah_id,
        verses=verses,
        selected_verse=verse_id,
    )