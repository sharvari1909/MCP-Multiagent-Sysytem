from datetime import datetime, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


INVOICE_DIR = Path("invoices")
INVOICE_DIR.mkdir(exist_ok=True)

COMPANY_NAME = "Anvenssa Technologies LLC"
COMPANY_ADDRESS = [
    "Vipin Ramakrishnan",
    "CBD MAKTOUM BRANCH BLDG - F01",
    "Al Khabeesi Deira Dubai",
    "Dubai, United Arab Emirates",
]


def generate_invoice_pdf(invoice):
    invoice_id = invoice["invoice_id"]
    path = INVOICE_DIR / f"{invoice_id}.pdf"

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Helvetica"
    styles["Normal"].fontSize = 9
    styles["Normal"].leading = 12

    story = []
    today = datetime.now()
    due_date = today + timedelta(days=7)

    story.append(_header(styles))
    story.append(Spacer(1, 12))
    story.append(_invoice_meta(invoice_id, today, due_date, styles))
    story.append(Spacer(1, 16))
    story.append(_bill_to(invoice["customer_email"], styles))
    story.append(Spacer(1, 16))
    story.append(_items_table(invoice))
    story.append(Spacer(1, 14))
    story.append(_totals_table(invoice))
    story.append(Spacer(1, 20))
    story.append(_tax_summary(invoice, styles))
    story.append(Spacer(1, 20))
    story.append(_notes_and_terms(styles))

    document.build(story)
    return str(path)


def _header(styles):
    company_lines = "<br/>".join(COMPANY_ADDRESS)
    company = Paragraph(
        f"<b>{COMPANY_NAME}</b><br/>{company_lines}",
        styles["Normal"],
    )
    title = Paragraph(
        '<para alignment="right"><font size="20"><b>TAX INVOICE</b></font></para>',
        styles["Normal"],
    )

    table = Table([[company, title]], colWidths=[105 * mm, 45 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#0f766e")),
    ]))
    return table


def _invoice_meta(invoice_id, today, due_date, styles):
    data = [
        ["Invoice #", invoice_id],
        ["Invoice Date :", today.strftime("%d/%m/%Y")],
        ["Due Date :", due_date.strftime("%d/%m/%Y")],
    ]

    table = Table(data, colWidths=[95 * mm, 55 * mm], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _bill_to(customer_email, styles):
    return Table(
        [[Paragraph("<b>Bill To:</b>", styles["Normal"])], [Paragraph(customer_email, styles["Normal"])]],
        colWidths=[150 * mm],
        style=[
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e2e8f0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ],
    )


def _items_table(invoice):
    header = ["#", "Item Description", "Qty", "Rate", "VAT", "Amount"]
    row = [
        "1",
        invoice["product"],
        f"{invoice['quantity']} Units",
        _money(invoice["unit_price"]),
        "18%",
        _money(invoice["total"]),
    ]

    table = Table([header, row], colWidths=[12 * mm, 62 * mm, 25 * mm, 25 * mm, 18 * mm, 32 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _totals_table(invoice):
    data = [
        ["Sub Total", _money(invoice["subtotal"])],
        ["GST 18%", _money(invoice["gst"])],
        ["TOTAL AED", _money(invoice["total"])],
    ]

    table = Table(data, colWidths=[35 * mm, 35 * mm], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#0f766e")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, 2), (-1, 2), 1, colors.HexColor("#0f766e")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _tax_summary(invoice, styles):
    story = [
        [Paragraph("<b>Tax Summary</b>", styles["Normal"]), "", ""],
        ["Tax Details", "Taxable Amount (AED)", "Tax Amount (AED)"],
        ["GST 18%", _money(invoice["subtotal"]), _money(invoice["gst"])],
        ["Total", _money(invoice["subtotal"]), _money(invoice["gst"])],
    ]

    table = Table(story, colWidths=[58 * mm, 58 * mm, 58 * mm])
    table.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("GRID", (0, 1), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (1, 2), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def _notes_and_terms(styles):
    return Table(
        [
            [Paragraph("<b>Notes</b>", styles["Normal"])],
            [Paragraph("Thank you for your business.", styles["Normal"])],
            [Paragraph("<b>Terms & Conditions</b>", styles["Normal"])],
            [Paragraph("Please make payment within 7 days from the invoice date.", styles["Normal"])],
        ],
        colWidths=[174 * mm],
        style=[
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#e2e8f0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ],
    )


def _money(value):
    return f"{float(value):,.2f}"
