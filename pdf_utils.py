from fpdf import FPDF
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile
import os
from datetime import date
from flask import current_app
from fpdf import FPDF
from io import BytesIO
# --- Funkcja pomocnicza: generowanie kodu kreskowego ---
def generate_barcode_file(text):
    options = {
        "write_text": False,     # nie dodawaj tekstu pod kodem
        "font_size": 0,          # nie renderuj tekstu w środku
        "quiet_zone": 1          # opcjonalnie: zmniejsz marginesy
    }
    barcode = Code128(text, writer=ImageWriter())
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    barcode.write(tmp_file, options=options)
    tmp_file.close()
    return tmp_file.name
#----------------generowanie naklejki------------------


def generate_label_pdf(set_name, stone_count, uuid_code):
    pdf = FPDF(format="A4", unit="mm")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    # rozmiar naklejki
    label_width = 60
    label_height = 25
    page_width = 210
    page_height = 297
    x = (page_width - label_width) / 2
    y = (page_height - label_height) / 2

    # tło naklejki
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(x, y, label_width, label_height, style='F')

    # ramka
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(x, y, label_width, label_height)

    # tekst
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(x, y + 6)
    pdf.cell(label_width, 6, f"{set_name} / {stone_count}", align="C")

    pdf.set_xy(x, y + 13)
    pdf.cell(label_width, 6, uuid_code, align="C")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        output = output.encode("latin1")
    return BytesIO(output)


# --- Funkcja główna: generowanie PDF ---
def generate_pdf_bytes(codes, satznummer, diameters, machine_number, stone_type="ND", set_name="", operator=""):
    pdf = FPDF(format="A5", unit="mm")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    # --- Nagłówek ---
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(5, 10)  # start nad lewą tabelą
    pdf.cell(92, 10, "SATZ-KARTE", ln=0, align="C")  # szerokość tabeli = 92 mm
    if set_name:
        pdf.set_xy(98, 10)  # start nad prawą kolumną
        pdf.cell(45, 10, set_name, ln=1, align="C")  # szerokość kolumny = 45 mm
    else:
        pdf.ln(10)
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
        pdf.cell(col_widths[2], 6, "", border=1, align="C", fill=True)
        pdf.cell(col_widths[3], 6, stone_type, border=1, align="C", fill=True)
        pdf.ln()

    # --- Prawa kolumna z polami ---
    right_x = 98
    y = 20
    pdf.set_xy(right_x, y)

    fields = [
        ("Satzkartennummer\nSet card number", satznummer),
        ("Bearbeiter\nOperator", operator),
        ("Maschine\nMaszyna", machine_number if machine_number else ""),
    ]

    for label, value in fields:
        pdf.set_xy(right_x, y)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(45, 5, label, border=1)
        y += 10
        if value:
            pdf.set_xy(right_x, y)
            # pogrubienie dla numeru karty, operatora i maszyny
            if label.startswith("Satzkartennummer") or label.startswith("Bearbeiter") or label.startswith("Maschine"):
                pdf.set_font("Helvetica", "B", 9)
            else:
                pdf.set_font("Helvetica", "", 8)
            pdf.cell(45, 6, value, border=1)
            y += 6

    # --- Logo (jeśli istnieje w static/) ---
    logo_path = os.path.join(current_app.root_path, "static", "logo.jpg")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=15, y=200, w=25)


    # --- Stopka (data wyśrodkowana na dole strony) ---
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(0, 200)  # ustawienie na dole strony
    pdf.cell(148, 5, str(date.today()), align="C")  # szerokość A5 = 148 mm

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
