
import pandas as pd
from io import BytesIO
from pypdf import PdfReader

from backend.core.report_generator import generate_investigation_pdf


def test_pdf_report_generation():

    contribution_df = pd.DataFrame({
        "Region": ["North", "South"],
        "Previous Value": [100, 200],
        "Current Value": [120, 100],
        "Change": [20, -100],
        "Contribution (%)": [-25, 125]
    })

    period_result = {
        "previous_value": 300,
        "current_value": 220,
        "absolute_change": -80,
        "percentage_change": -26.67,
        "status": "Decreased"
    }

    pdf_data = generate_investigation_pdf(
        dataset_name="sample_sales.csv",
        metric="Sales",
        previous_period="2025-01-01 to 2025-01-31",
        current_period="2025-02-01 to 2025-02-28",
        period_result=period_result,
        contribution_df=contribution_df,
        dimension_column="Region"
    )

    assert isinstance(pdf_data, bytes)
    assert len(pdf_data) > 0
    assert pdf_data.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_data))

    assert len(reader.pages) >= 1

    extracted_text = ""

    for page in reader.pages:
        extracted_text += page.extract_text() or ""

    assert "RootCause AI" in extracted_text
    assert "Business Performance Comparison" in extracted_text
    assert "Segment Contribution Analysis" in extracted_text
    assert "North" in extracted_text
    assert "South" in extracted_text
