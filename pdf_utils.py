#------------------ZMIANY W GENEROWANYM PDF------------------------
from fpdf import FPDF
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile
import os
from datetime import date
from flask import current_app


# --- Funkcja pomocnicza: generowanie kodu kreskowego ---
def generate_barcode_file(text):
    barcode = Code128(text, writer=ImageWriter())
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    barcode.write(tmp_file)
    tmp_file.close()
    return tmp_file.name


# --- Funkcja główna: generowanie PDF ---
def generate_pdf_bytes(codes, satznummer, diameters, machine_number):
    pdf = FPDF(format="A5", unit="mm")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    # --- Nagłówek testowy (dla pewności, że PDF nie jest pusty) ---
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "SATZ-KARTE", ln=True, align="C")

    # --- Tabela po lewej ---
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(5, 20)
    col_widths = [28, 28, 18, 18]
    headers = ["Drawing die", "Durchmesser", "Info", "Typ"]

    for i, h in enumerate(headers):
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(col_widths[i], 6, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for i, dia in enumerate(diameters):
        pdf.set_x(5)
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_widths[0], 6, codes[i] if i < len(codes) else "", border=1, fill=True)
        pdf.cell(col_widths[1], 6, f"{dia:.4f}", border=1, align="C", fill=True)
        pdf.cell(col_widths[2], 6, "ND", border=1, align="C", fill=True)
        pdf.cell(col_widths[3], 6, "ND", border=1, align="C", fill=True)
        pdf.ln()

    # --- Prawa kolumna z polami ---
    right_x = 98
    y = 20
    pdf.set_xy(right_x, y)

    fields = [
        ("Satzkartennummer\nSet card number", satznummer),
        ("Grundsatz\nBasic set", ""),
        ("Vorlage\nTemplate", "1"),
        ("Bearbeiter\nOperator", ""),
        ("Maschine\nMachine", machine_number if machine_number else ""),
        ("Laufzeit In\nRuntime In", ""),
        ("Laufzeit Out\nRuntime Out", ""),
        ("Luftroll\nAir roll", ""),
        ("Summe\nTotal", ""),
        ("Materialmenge (kg)\nMaterial weight", "")
    ]

    pdf.set_font("Helvetica", "", 8)
    for label, value in fields:
        pdf.set_xy(right_x, y)
        pdf.multi_cell(45, 5, label, border=1)
        y += 10
        if value:
            pdf.set_xy(right_x, y)
            pdf.cell(45, 6, value, border=1)
            y += 6

    # --- Logo (jeśli istnieje w static/) ---
    logo_path = os.path.join(current_app.root_path, "static", "logo.jpg")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=15, y=200, w=25)

    # --- Stopka ---
    pdf.set_xy(40, 195)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(40, 5, "LEONI Draht GmbH", align="C")
    pdf.set_xy(40, 200)
    pdf.cell(40, 5, str(date.today()), align="C")

    # --- Kod kreskowy ---
    barcode_path = generate_barcode_file(satznummer)
    pdf.image(barcode_path, x=110, y=185, w=35)
    os.remove(barcode_path)

    pdf.set_xy(110, 190)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(35, 5, satznummer, align="C")

    # --- Zwrócenie PDF jako bytes ---
    output = pdf.output(dest="S")
    if isinstance(output, str):
        output = output.encode("latin1")
    pdf_bytes = BytesIO(output)
    return pdf_bytes
