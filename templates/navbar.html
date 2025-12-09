from flask import (
    Flask, render_template, request, send_file, redirect,
    make_response, url_for, flash
)
from datetime import datetime
import zoneinfo
import sqlite3
import uuid
from io import BytesIO

from database import export_to_excel_transposed, init_db, save_history
from pdf_utils import generate_pdf_bytes, generate_label_pdf
from data import DIAMETERS_SET_1, DIAMETERS_SET_2, DIAMETERS_SET_3, DIAMETERS_BY_SET

app = Flask(__name__)
app.secret_key = "zmien_na_bezpieczny_secret"

# init DB (idempotent)
init_db()

TRANSLATIONS = {
    "pl": {
        "title": "Generator SATZ-KARTE",
        "satz_label": "Numer karty setu :",
        "operator_label": "Operator:",
        "select_set_label": "Wybierz zestaw średnic:",
        "machine_label": "Numer maszyny:",
        "stone_type_label": "Typ kamienia:",
        "col_code": "Kod kamienia",
        "col_diameter": "Średnica (mm)",
        "col_action": "Akcja",
        "add_stone": "Dodaj kamień",
        "generate_pdf": "Generuj etykietę PDF",
        "generate_label": "Generuj Naklejkę",
        "history_link": "📜 Zobacz historię zapisanych kart",
        "lang_toggle_title": "Przełącz język PL/DE"
    },
    "de": {
        "title": "Satzkarte Generator",
        "satz_label": "Satzkartennummer:",
        "operator_label": "Bearbeiter:",
        "select_set_label": "Wählen Sie den Durchmessersatz:",
        "machine_label": "Maschinennummer:",
        "stone_type_label": "Steintyp:",
        "col_code": "Steincode",
        "col_diameter": "Durchmesser (mm)",
        "col_action": "Aktion",
        "add_stone": "Stein hinzufügen",
        "generate_pdf": "PDF erstellen",
        "generate_label": "Etikett erstellen",
        "history_link": "📜 Gespeicherte Karten ansehen",
        "lang_toggle_title": "Sprache umschalten PL/DE"
    }
}

def get_lang():
    lang = request.cookies.get("lang")
    return lang if lang in ("pl", "de") else "pl"

@app.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    if lang_code not in ("pl", "de"):
        lang_code = "pl"
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie("lang", lang_code, max_age=60*60*24*365)
    return resp

ZESTAWY = {"1": "Untersatz", "2": "Mittelsatz", "3": "Grundsatz"}

def generate_unique_satznummer():
    return str(uuid.uuid4())[:8]

@app.route("/", methods=["GET", "POST"])
def index():
    lang = get_lang()
    t = TRANSLATIONS[lang]

    if request.method == "POST":
        satznummer = request.form.get("satznummer") or generate_unique_satznummer()
        machine_number = request.form.get("machine_number", "")
        selected_set = request.form.get("diameter_set", "3")
        stone_type = request.form.get("stone_type", "ND")
        operator = request.form.get("operator", "")

        codes = []
        diameters = []
        i = 0
        while True:
            code = request.form.get(f"code{i}")
            diameter = request.form.get(f"diameter{i}")
            if code is None and diameter is None:
                break
            if code:
                codes.append(code.strip())
            if diameter:
                try:
                    diameters.append(float(diameter))
                except (ValueError, TypeError):
                    diameters.append(0.0)
            else:
                diameters.append(0.0)
            i += 1

        set_name = ZESTAWY.get(selected_set, "")

        # PDF pozostaje w domyślnym języku generowania (np. niemieckim)
        pdf_bytes = generate_pdf_bytes(
            codes=codes,
            satznummer=satznummer,
            diameters=diameters,
            machine_number=machine_number,
            stone_count=len([c for c in codes if c]),
            stone_type=stone_type,
            set_name=set_name,
            operator=operator,
        )

        try:
            local_time = datetime.now(zoneinfo.ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")
            save_history(satznummer, machine_number, selected_set, local_time)
        except Exception:
            pass

        try:
            conn = sqlite3.connect("satzkarten.db")
            cursor = conn.cursor()
            for code, dia in zip(codes, diameters):
                cursor.execute(
                    "INSERT INTO details (satznummer, code, diameter, status) VALUES (?, ?, ?, ?)",
                    (satznummer, code, dia, "Nowy")
                )
            conn.commit()
            conn.close()
        except Exception:
            pass

        if isinstance(pdf_bytes, BytesIO):
            pdf_bytes.seek(0)
            return send_file(pdf_bytes, as_attachment=True, download_name=f"Satzkarte_{satznummer}.pdf", mimetype="application/pdf")
        else:
            return send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=f"Satzkarte_{satznummer}.pdf", mimetype="application/pdf")

    generated_satznummer = generate_unique_satznummer()
    return render_template(
        "index.html",
        diams=DIAMETERS_SET_3,
        generated_satznummer=generated_satznummer,
        lang=lang,
        t=t,
        set1=DIAMETERS_SET_1,
        set2=DIAMETERS_SET_2,
        set3=DIAMETERS_SET_3
    )

@app.route("/history")
def history():
    lang = get_lang()
    t = TRANSLATIONS[lang]

    satznummer = request.args.get("satznummer", "")
    machine = request.args.get("machine", "")
    zestaw = request.args.get("zestaw", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    code = request.args.get("code", "")
    diameter = request.args.get("diameter", "")

    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()

    query_h = "SELECT * FROM history WHERE 1=1"
    params_h = []
    if satznummer:
        query_h += " AND satznummer LIKE ?"
        params_h.append(f"%{satznummer}%")
    if machine:
        query_h += " AND machine LIKE ?"
        params_h.append(f"%{machine}%")
    if zestaw:
        query_h += " AND zestaw = ?"
        params_h.append(zestaw)
    if date_from:
        query_h += " AND date(data) >= date(?)"
        params_h.append(date_from)
    if date_to:
        query_h += " AND date(data) <= date(?)"
        params_h.append(date_to)

    query_h += " ORDER BY id DESC"
    cursor.execute(query_h, params_h)
    raw_history = cursor.fetchall()

    history_rows = [
        {
            "id": row[0],
            "satznummer": row[1],
            "machine": row[2],
            "zestaw_num": str(row[3]),
            "zestaw_name": ZESTAWY.get(str(row[3]), row[3]),
            "data": row[4]
        }
        for row in raw_history
    ]

    query_d = """
        SELECT d.satznummer, d.code, d.diameter, d.id, d.status
        FROM details d
        JOIN history h ON d.satznummer = h.satznummer
        WHERE 1=1
    """
    params_d = []
    if satznummer:
        query_d += " AND d.satznummer LIKE ?"
        params_d.append(f"%{satznummer}%")
    if machine:
        query_d += " AND h.machine LIKE ?"
        params_d.append(f"%{machine}%")
    if zestaw:
        query_d += " AND h.zestaw = ?"
        params_d.append(zestaw)
    if date_from:
        query_d += " AND date(h.data) >= date(?)"
        params_d.append(date_from)
    if date_to:
        query_d += " AND date(h.data) <= date(?)"
        params_d.append(date_to)
    if code:
        query_d += " AND d.code LIKE ?"
        params_d.append(f"%{code}%")
    if diameter:
        query_d += " AND d.diameter = ?"
        params_d.append(diameter)

    query_d += " ORDER BY d.id DESC"
    cursor.execute(query_d, params_d)
    details_rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=history_rows,
        details=details_rows,
        filters={
            "satznummer": satznummer, "machine": machine,
            "zestaw": zestaw, "date_from": date_from, "date_to": date_to,
            "code": code, "diameter": diameter
        },
        diameters_by_set=DIAMETERS_BY_SET,
        lang=lang,
        t=t
    )

@app.route("/export_card/<satznummer>")
def export_card(satznummer):
    excel_bytes = export_to_excel_transposed(satznummer=satznummer)
    excel_bytes.seek(0)
    return send_file(
        excel_bytes,
        as_attachment=True,
        download_name=f"export_karta_{satznummer}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download_pdf/<satznummer>")
def download_pdf(satznummer):
    lang = get_lang()
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    cursor.execute("SELECT machine, zestaw, data FROM history WHERE satznummer = ?", (satznummer,))
    history_row = cursor.fetchone()
    if not history_row:
        conn.close()
        return "Nie znaleziono karty", 404

    machine, zestaw, _ = history_row
    cursor.execute("SELECT code, diameter FROM details WHERE satznummer = ?", (satznummer,))
    details = cursor.fetchall()
    conn.close()

    codes = [row[0] for row in details]
    diameters = [row[1] for row in details]
    set_name = ZESTAWY.get(str(zestaw), "")
    pdf_bytes = generate_pdf_bytes(
        codes=codes,
        satznummer=satznummer,
        diameters=diameters,
        machine_number=machine,
        stone_count=len(codes),
        stone_type="ND",
        set_name=set_name,
        operator="",

    )
    if isinstance(pdf_bytes, BytesIO):
        pdf_bytes.seek(0)
        return send_file(pdf_bytes, as_attachment=True, download_name=f"Satzkarte_{satznummer}.pdf", mimetype="application/pdf")
    else:
        return send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=f"Satzkarte_{satznummer}.pdf", mimetype="application/pdf")
@app.route("/delete/<satznummer>", methods=["POST"])
def delete_card(satznummer):
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    # usuń szczegóły powiązane z kartą
    cursor.execute("DELETE FROM details WHERE satznummer = ?", (satznummer,))
    # usuń wpis w historii
    cursor.execute("DELETE FROM history WHERE satznummer = ?", (satznummer,))
    conn.commit()
    conn.close()
    # po usunięciu wróć do strony historii
    return redirect(url_for("history"))
@app.route("/delete_stone/<int:stone_id>", methods=["POST"])
def delete_stone(stone_id):
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    # usuń kamień po jego ID
    cursor.execute("DELETE FROM details WHERE id = ?", (stone_id,))
    conn.commit()
    conn.close()
    # po usunięciu wróć do historii
    return redirect(url_for("history"))

@app.route("/generate_label_direct", methods=["POST"])
def generate_label_direct():
    satznummer = request.form.get("satznummer") or generate_unique_satznummer()
    selected_set = request.form.get("diameter_set", "3")
    set_name = ZESTAWY.get(selected_set, "Zestaw")
    stone_count = len([k for k in request.form.keys() if k.startswith("code")])
    pdf_bytes = generate_label_pdf(set_name=set_name, stone_count=stone_count, uuid_code=satznummer)
    if isinstance(pdf_bytes, BytesIO):
        pdf_bytes.seek(0)
        return send_file(pdf_bytes, as_attachment=True, download_name=f"naklejka_{satznummer}.pdf", mimetype="application/pdf")
    else:
        return send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=f"naklejka_{satznummer}.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
