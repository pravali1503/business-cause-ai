
from io import BytesIO

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


def generate_investigation_pdf(
    dataset_name,
    metric,
    previous_period,
    current_period,
    period_result,
    contribution_df,
    dimension_column
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2457A6"),
        fontSize=20,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#2457A6"),
        spaceBefore=14,
        spaceAfter=8
    )

    story = []

    story.append(
        Paragraph(
            "RootCause AI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Business Root-Cause and Contribution Investigation Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 15))

    # DATASET INFORMATION

    story.append(
        Paragraph(
            "1. Dataset Information",
            heading_style
        )
    )

    dataset_table = [
        ["Field", "Details"],
        ["Dataset Name", str(dataset_name)],
        ["Business Metric", str(metric)],
        ["Previous Period", str(previous_period)],
        ["Current Period", str(current_period)]
    ]

    table = Table(
        dataset_table,
        colWidths=[150, 330]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2457A6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(table)

    story.append(Spacer(1, 15))

    # PERIOD COMPARISON

    story.append(
        Paragraph(
            "2. Business Performance Comparison",
            heading_style
        )
    )

    percentage_change = period_result.get("percentage_change")

    if percentage_change is None:
        percentage_text = "Not available (previous value is zero)"
    else:
        percentage_text = f"{percentage_change:.2f}%"

    period_table = [
        ["Measurement", "Result"],
        [
            "Previous Period Value",
            f"{period_result['previous_value']:,.2f}"
        ],
        [
            "Current Period Value",
            f"{period_result['current_value']:,.2f}"
        ],
        [
            "Absolute Change",
            f"{period_result['absolute_change']:,.2f}"
        ],
        [
            "Percentage Change",
            percentage_text
        ],
        [
            "Performance Status",
            str(period_result["status"])
        ]
    ]

    table = Table(
        period_table,
        colWidths=[200, 280]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2457A6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(table)

    story.append(Spacer(1, 15))

    # CONTRIBUTION ANALYSIS

    story.append(
        Paragraph(
            "3. Segment Contribution Analysis",
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"Business Dimension: {dimension_column}",
            styles["Normal"]
        )
    )

    contribution_data = [
        [
            str(dimension_column),
            "Previous Value",
            "Current Value",
            "Change",
            "Contribution (%)"
        ]
    ]

    for _, row in contribution_df.iterrows():

        contribution = row.get("Contribution (%)")

        contribution_text = (
            "Not available"
            if pd.isna(contribution)
            else f"{contribution:.2f}%"
        )

        contribution_data.append([
            str(row[dimension_column])[:35],
            f"{row['Previous Value']:,.2f}",
            f"{row['Current Value']:,.2f}",
            f"{row['Change']:,.2f}",
            contribution_text
        ])

    table = Table(
        contribution_data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2457A6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(table)

    story.append(Spacer(1, 15))

    # FINDINGS

    story.append(
        Paragraph(
            "4. Key Findings",
            heading_style
        )
    )

    if not contribution_df.empty:

        positive = contribution_df[
            contribution_df["Change"] > 0
        ]

        negative = contribution_df[
            contribution_df["Change"] < 0
        ]

        if not positive.empty:

            largest_positive = positive.loc[
                positive["Change"].idxmax()
            ]

            story.append(
                Paragraph(
                    f"Positive contributor: "
                    f"{largest_positive[dimension_column]} "
                    f"with a change of "
                    f"{largest_positive['Change']:,.2f}.",
                    styles["Normal"]
                )
            )

        if not negative.empty:

            largest_negative = negative.loc[
                negative["Change"].idxmin()
            ]

            story.append(
                Paragraph(
                    f"Negative contributor: "
                    f"{largest_negative[dimension_column]} "
                    f"with a change of "
                    f"{largest_negative['Change']:,.2f}.",
                    styles["Normal"]
                )
            )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "5. Important Interpretation",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Segment contribution represents the mathematical share "
            "of each segment's change in the overall business metric. "
            "These results identify where changes occurred but do not "
            "prove that a particular segment caused the change. "
            "Further investigation is required to establish possible causes.",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated by RootCause AI",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()
