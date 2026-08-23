from flask import Blueprint, render_template, request

from services.quran import Quran


main = Blueprint("main", __name__)

quran = Quran()


@main.route("/")
def index():
    surahs = quran.get_surahs()

    return render_template(
        "index.html",
        surahs=surahs
    )


@main.route("/surah/<int:surah_id>")
def surah(surah_id):

    verse_id = request.args.get("verse", type=int)

    if verse_id:
        verses = quran.get_verse_context(
            surah_id,
            verse_id,
            before=3,
            after=3
        )
    else:
        verses = [
            {
                "number": int(number),
                "text": text,
                "selected": False
            }
            for number, text
            in quran.get_surah(surah_id).items()
        ]

    return render_template(
        "index.html",
        surahs=quran.get_surahs(),
        current_surah=surah_id,
        verses=verses,
        selected_verse=verse_id
    )


@main.route("/search")
def search():

    query = request.args.get("q", "").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    search = quran.search(
        query=query,
        page=page,
        per_page=20
    )

    return render_template(
        "search.html",
        query=query,
        results=search["results"],
        page=search["page"],
        pages=search["pages"],
        total=search["total"]
    )
