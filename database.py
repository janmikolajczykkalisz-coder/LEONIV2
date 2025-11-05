import sqlite3
import pandas as pd

DB_NAME = "satzkarten.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # tabela historii
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            satznummer TEXT,
            machine TEXT,
            zestaw TEXT,
            data TEXT
        )
    """)

    # tabela szczegółów kamieni
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            satznummer TEXT,
            code TEXT,
            diameter REAL,
            status TEXT DEFAULT 'Nowy',
            FOREIGN KEY (satznummer) REFERENCES history(satznummer)
        )
    """)
    conn.commit()
    conn.close()


def save_history(satznummer, machine, zestaw, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (satznummer, machine, zestaw, data) VALUES (?, ?, ?, ?)",
                   (satznummer, machine, zestaw, data))
    conn.commit()
    conn.close()


def save_details(satznummer, codes, diameters):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for code, dia in zip(codes, diameters):
        cursor.execute("INSERT INTO details (satznummer, code, diameter, status) VALUES (?, ?, ?, ?)",
                       (satznummer, code, dia, "Nowy"))
    conn.commit()
    conn.close()


def get_history(filters=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_details(satznummer=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if satznummer:
        cursor.execute("SELECT satznummer, code, diameter, id, status FROM details WHERE satznummer = ?", (satznummer,))
    else:
        cursor.execute("SELECT satznummer, code, diameter, id, status FROM details")
    rows = cursor.fetchall()
    conn.close()
    return rows

def export_to_excel(filename="export.xlsx"):
    conn = sqlite3.connect("satzkarten.db")
    df = pd.read_sql_query("SELECT * FROM history_with_codes", conn)
    conn.close()

    # zapisz z formatowaniem
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Zestawy")

        # pobierz arkusz Excela
        worksheet = writer.sheets["Zestawy"]

        # automatyczne dopasowanie szerokości kolumn
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = max_length + 2
            worksheet.auto_filter.ref = worksheet.dimensions
