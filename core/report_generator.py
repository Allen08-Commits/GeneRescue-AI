
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime


def generate_pdf_report(
    trait,
    sequence_results=None,
    gene_results=None,
    variant_summary=None,
    recommendations=None
):
    """Generate a downloadable GeneRescue AI PDF report."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#174C35"),
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#216644"),
        spaceBefore=14,
        spaceAfter=8
    )

    story = []

    story.append(Paragraph("GeneRescue AI", title_style))

    story.append(
        Paragraph(
            "Intelligent Genetic Rescue System for Crop Improvement",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(f"Selected crop trait: {trait}", styles["Normal"])
    )

    story.append(
        Paragraph("1. Sequence Analysis", heading_style)
    )

    if sequence_results:
        for result in sequence_results:
            story.append(
                Paragraph(
                    f"Sequence ID: {result.get('sequence_id', 'Unknown')}<br/>"
                    f"Length: {result.get('length', 'N/A')} bp<br/>"
                    f"GC percentage: {result.get('GC_percentage', 'N/A')}%<br/>"
                    f"AT percentage: {result.get('AT_percentage', 'N/A')}%",
                    styles["BodyText"]
                )
            )
            story.append(Spacer(1, 8))
    else:
        story.append(Paragraph("No sequence analysis supplied.", styles["BodyText"]))

    story.append(
        Paragraph("2. Candidate Gene / ORF Findings", heading_style)
    )

    if gene_results:
        table_data = [
            ["ORF ID", "Strand", "Length (bp)", "Protein Length"]
        ]

        for gene in gene_results[:30]:
            table_data.append([
                str(gene.get("ORF_ID", "N/A")),
                str(gene.get("Strand", "N/A")),
                str(gene.get("Nucleotide_Length", "N/A")),
                str(gene.get("Amino_Acid_Length", "N/A"))
            ])

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[1.2*inch, 0.8*inch, 1.3*inch, 1.3*inch]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#216644")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 7)
        ]))

        story.append(table)
    else:
        story.append(
            Paragraph("No candidate ORFs identified or supplied.", styles["BodyText"])
        )

    story.append(
        Paragraph("3. Variant Analysis", heading_style)
    )

    if variant_summary:
        story.append(
            Paragraph(
                f"Total variants: {variant_summary.get('total_variants', 0)}",
                styles["BodyText"]
            )
        )

        for variant, count in variant_summary.get("variant_types", {}).items():
            story.append(
                Paragraph(f"{variant}: {count}", styles["BodyText"])
            )
    else:
        story.append(
            Paragraph("No variant analysis supplied.", styles["BodyText"])
        )

    story.append(
        Paragraph("4. Genetic Rescue Recommendations", heading_style)
    )

    if recommendations:
        for strategy in recommendations.get(
            "recommended_strategies", []
        ):
            story.append(
                Paragraph(f"• {strategy}", styles["BodyText"])
            )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph("Suggested validation methods:", styles["Heading3"])
        )

        for method in recommendations.get("validation_methods", []):
            story.append(
                Paragraph(f"• {method}", styles["BodyText"])
            )
    else:
        story.append(
            Paragraph("No recommendations supplied.", styles["BodyText"])
        )

    story.append(
        Paragraph("5. Scientific Disclaimer", heading_style)
    )

    story.append(
        Paragraph(
            "This report presents computational analyses and "
            "research-oriented hypotheses. Predicted ORFs are not "
            "experimentally confirmed genes. Variant classifications "
            "are structural and do not establish pathogenicity or "
            "functional effects. All proposed genetic improvement "
            "strategies require independent scientific and experimental "
            "validation before agricultural application.",
            styles["BodyText"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer

