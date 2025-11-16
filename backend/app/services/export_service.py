import csv
import json
from io import StringIO, BytesIO
from typing import List, Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import pandas as pd


class ExportService:
    """Service for exporting analysis results"""

    @staticmethod
    def export_to_csv(data: List[Dict]) -> str:
        """Export data to CSV format"""
        if not data:
            return ""

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()

    @staticmethod
    def export_to_json(data: List[Dict]) -> str:
        """Export data to JSON format"""
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def export_to_pdf(data: List[Dict], title: str = "Sentiment Analysis Report") -> bytes:
        """Export data to PDF format"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Container for the 'Flowable' objects
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        heading_style = styles['Heading2']
        normal_style = styles['Normal']

        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 0.3*inch))

        # Summary
        if data:
            elements.append(Paragraph(f"Total Analyses: {len(data)}", heading_style))
            elements.append(Spacer(1, 0.2*inch))

            # Calculate statistics
            sentiments = [d.get('sentiment_label') for d in data if d.get('sentiment_label')]
            if sentiments:
                positive = sentiments.count('positive')
                negative = sentiments.count('negative')
                neutral = sentiments.count('neutral')

                summary_data = [
                    ['Metric', 'Count', 'Percentage'],
                    ['Positive', str(positive), f"{positive/len(sentiments)*100:.1f}%"],
                    ['Negative', str(negative), f"{negative/len(sentiments)*100:.1f}%"],
                    ['Neutral', str(neutral), f"{neutral/len(sentiments)*100:.1f}%"]
                ]

                summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 0.3*inch))

            # Detailed results
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Results", heading_style))
            elements.append(Spacer(1, 0.2*inch))

            for idx, item in enumerate(data[:50]):  # Limit to 50 items
                elements.append(Paragraph(f"<b>Analysis {idx + 1}</b>", normal_style))
                elements.append(Spacer(1, 0.1*inch))

                # Create table for this item
                item_data = []

                if item.get('text'):
                    text = item['text'][:200] + "..." if len(item['text']) > 200 else item['text']
                    item_data.append(['Text', text])

                if item.get('sentiment_label'):
                    item_data.append(['Sentiment', item['sentiment_label'].upper()])

                if item.get('sentiment_confidence'):
                    item_data.append(['Confidence', f"{item['sentiment_confidence']*100:.1f}%"])

                if item.get('emotion_label'):
                    item_data.append(['Emotion', item['emotion_label'].upper()])

                if item.get('language'):
                    item_data.append(['Language', item['language']])

                if item_data:
                    item_table = Table(item_data, colWidths=[1.5*inch, 5*inch])
                    item_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(item_table)

                elements.append(Spacer(1, 0.2*inch))

        # Build PDF
        doc.build(elements)

        return buffer.getvalue()

    @staticmethod
    def export_to_excel(data: List[Dict]) -> bytes:
        """Export data to Excel format"""
        if not data:
            return b""

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Analysis Results')

        return buffer.getvalue()

    @staticmethod
    def prepare_export_data(analyses: List) -> List[Dict]:
        """Prepare analysis data for export"""
        export_data = []

        for analysis in analyses:
            data = {
                'id': analysis.id,
                'text': analysis.text,
                'analysis_type': analysis.analysis_type,
                'sentiment_label': analysis.sentiment_label,
                'sentiment_confidence': analysis.sentiment_confidence,
                'sentiment_positive': analysis.sentiment_positive,
                'sentiment_negative': analysis.sentiment_negative,
                'sentiment_neutral': analysis.sentiment_neutral,
                'emotion_label': analysis.emotion_label,
                'emotion_confidence': analysis.emotion_confidence,
                'language': analysis.language,
                'model_used': analysis.model_used,
                'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                'processing_time': analysis.processing_time
            }
            export_data.append(data)

        return export_data


# Global instance
export_service = ExportService()
