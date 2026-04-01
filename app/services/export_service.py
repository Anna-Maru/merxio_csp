import io
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_xlsx(
    summary: dict,
    top_products: list[dict],
    categories: list[dict],
    dynamics: list[dict],
) -> io.BytesIO:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Сводка", index=False)
        pd.DataFrame(top_products).to_excel(
            writer, sheet_name="Топ товары", index=False
        )
        pd.DataFrame(categories).to_excel(
            writer, sheet_name="По категориям", index=False
        )
        pd.DataFrame(dynamics).to_excel(writer, sheet_name="Динамика", index=False)
    buffer.seek(0)
    return buffer


def export_pdf(
    summary: dict,
    top_products: list[dict],
    categories: list[dict],
) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Аналитический отчёт", styles["Title"]))
    elements.append(Paragraph(f"Дата: {datetime.utcnow():%Y-%m-%d}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Сводка", styles["Heading2"]))
    summary_data = [
        ["Показатель", "Значение"],
        ["Выручка", str(summary["total_revenue"])],
        ["Заказов", str(summary["total_orders"])],
        ["Средний чек", str(summary["avg_check"])],
    ]
    t = Table(summary_data, colWidths=[200, 200])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D9E75")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F1EFE8")],
                ),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Топ-10 товаров", styles["Heading2"]))
    top_data = [["Товар", "Кол-во", "Выручка"]] + [
        [r["product_name"], str(r["total_qty"]), str(r["total_revenue"])]
        for r in top_products
    ]
    t2 = Table(top_data, colWidths=[250, 80, 100])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D9E75")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F1EFE8")],
                ),
            ]
        )
    )
    elements.append(t2)

    doc.build(elements)
    buffer.seek(0)
    return buffer
