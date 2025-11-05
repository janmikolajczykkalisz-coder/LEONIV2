from flask import Flask, render_template, request, send_file, redirect
from datetime import datetime
import zoneinfo
import sqlite3
from database import export_to_excel
from flask import send_file

from pdf_utils import generate_pdf_bytes
from database import init_db, save_history
from data import DIAMETERS_SET_1, DIAMETERS_SET_2, DIAMETERS_SET_3, DIAMETERS_BY_SET

app = Flask(__name__)
init_db()

# ------------------- STRONA GŁÓWNA (GENERATOR) -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        satznummer = request.form["satznummer"]
        machine_number = request.form.get("machine_number", "")
        selected_set = request.form.get("diameter_set", "3")

        # wybór zestawu średnic
        if selected_set == "1":
            diameters = DIAMETERS_SET_1
        elif selected_set == "2":
            diameters = DIAMETERS_SET_2
        else:
            diameters = DIAMETERS_SET_3

        # kody z formularza
        codes = [request.form.get(f"code{i}", "") for i in range(len(diameters))]

        # PDF
        pdf_bytes = generate_pdf_bytes(codes, satznummer, diameters, machine_number)

        # DB
        init_db()
        local_time = datetime.now(zoneinfo.ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")
        save_history(satznummer, machine_number, selected_set, local_time)

        conn = sqlite3.connect("satzkarten.db")
        cursor = conn.cursor()
        for code, dia in zip(codes, diameters):
            cursor.execute(
                "INSERT INTO details (satznummer, code, diameter, status) VALUES (?, ?, ?, ?)",
                (satznummer, code, dia, "Nowy")
            )
        conn.commit()
        conn.close()

        return send_file(
            pdf_bytes,
            as_attachment=True,
            download_name=f"Satzkarte_{satznummer}.pdf",
            mimetype="application/pdf"
        )

    return render_template("index.html", diams=DIAMETERS_SET_3)


# ------------------- HISTORIA -------------------
ZESTAWY = {
    "1": "Untersatz",
    "2": "Mittelsatz",
    "3": "Grundsatz"
}

@app.route("/history")
def history():
    satznummer = request.args.get("satznummer", "")
    machine = request.args.get("machine", "")
    zestaw = request.args.get("zestaw", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    code = request.args.get("code", "")
    diameter = request.args.get("diameter", "")

    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()

    # --- historia ---
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
    history_rows = cursor.fetchall()

    # zamiana numerów zestawu na nazwy
    history_rows = [
        (row[0], row[1], row[2], ZESTAWY.get(str(row[3]), row[3]), row[4])
        for row in history_rows
    ]

    # --- szczegóły ---
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
        diameters_by_set=DIAMETERS_BY_SET
    )


# ------------------- USUWANIE CAŁEJ KARTY -------------------
@app.route("/delete/<satznummer>", methods=["POST"])
def delete_card(satznummer):
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM details WHERE satznummer = ?", (satznummer,))
    cursor.execute("DELETE FROM history WHERE satznummer = ?", (satznummer,))
    conn.commit()
    conn.close()
    return redirect("/history")


# ------------------- USUWANIE POJEDYNCZEGO KAMIENIA -------------------
@app.route("/delete_stone/<int:stone_id>", methods=["POST"])
def delete_stone(stone_id):
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM details WHERE id = ?", (stone_id,))
    conn.commit()
    conn.close()
    return redirect("/history")


# ------------------- DODAWANIE NOWEGO KAMIENIA -------------------
@app.route("/add_stone", methods=["POST"])
def add_stone():
    satznummer = request.form.get("satznummer")
    code = request.form.get("code", "")
    diameter = request.form.get("diameter")
    zestaw = request.form.get("zestaw")

    # walidacja: czy średnica należy do wybranego zestawu
    if zestaw not in DIAMETERS_BY_SET or float(diameter) not in DIAMETERS_BY_SET[zestaw]:
        return redirect("/history")

    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO details (satznummer, code, diameter, status) VALUES (?, ?, ?, ?)",
        (satznummer, code, diameter, "Nowy")
    )
    conn.commit()
    conn.close()
    return redirect("/history")


# ------------------- AKTUALIZACJA STATUSU KAMIENIA -------------------
@app.route("/update_status/<int:stone_id>", methods=["POST"])
def update_status(stone_id):
    new_status = request.form.get("status")
    conn = sqlite3.connect("satzkarten.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE details SET status = ? WHERE id = ?", (new_status, stone_id))
    conn.commit()
    conn.close()
    return redirect("/history")
#------------------------EXPORT DO EXCELA------------------------------------------
@app.route("/export")
def export():
    filename = "export.xlsx"
    export_to_excel(filename)
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, ssl_context="adhoc", debug=True)


