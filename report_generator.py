from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class MyopiaReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
    
    def generate_report(self, patient_info, prediction_results, output_path, risk_factors=None, progression_timeline=None, comparative_stats=None):
        """Generate comprehensive PDF report"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Header
        story.append(Paragraph("Stellest AI", self.styles['CustomTitle']))
        story.append(Paragraph("Myopia Progression Assessment Report", self.styles['Heading2']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"<b>Report Date:</b> {report_date}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.styles['CustomHeading']))
        patient_data = [
            ['Field', 'Value'],
            ['Patient Name', patient_info.get('name', 'N/A')],
            ['Age', f"{patient_info.get('age', 'N/A')} years"],
            ['Gender', patient_info.get('gender', 'N/A')],
            ['Date of Assessment', patient_info.get('date', report_date)],
        ]
        
        patient_table = Table(patient_data, colWidths=[2.5 * inch, 3 * inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Clinical Data
        story.append(Paragraph("Clinical Assessment", self.styles['CustomHeading']))
        clinical_data = [
            ['Parameter', 'Right Eye', 'Left Eye'],
            ['Spherical (D)', 
             f"{patient_info.get('re_spherical', 'N/A')}",
             f"{patient_info.get('le_spherical', 'N/A')}"],
            ['Cylinder (D)', 
             f"{patient_info.get('re_cylinder', 'N/A')}",
             f"{patient_info.get('le_cylinder', 'N/A')}"],
            ['Axial Length (mm)', 
             f"{patient_info.get('re_axial_length', 'N/A')}",
             f"{patient_info.get('le_axial_length', 'N/A')}"],
        ]
        
        clinical_table = Table(clinical_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
        clinical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(clinical_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Risk Assessment - MAIN RESULTS
        story.append(Paragraph("AI-Powered Risk Assessment", self.styles['CustomHeading']))
        
        risk_category = prediction_results['risk_category']
        risk_color = self._get_risk_color(risk_category)
        
        story.append(Paragraph(
            f"<b>Progression Risk:</b> <font color='{risk_color}'>{risk_category}</font>",
            self.styles['CustomBody']
        ))
        
        risk_probs = prediction_results['risk_probabilities']
        story.append(Paragraph(
            f"<b>Risk Probabilities:</b><br/>"
            f"• Low Risk: {risk_probs['low']:.1%}<br/>"
            f"• Medium Risk: {risk_probs['medium']:.1%}<br/>"
            f"• High Risk: {risk_probs['high']:.1%}",
            self.styles['CustomBody']
        ))
        
        story.append(Paragraph(
            f"<b>Estimated Progression Rate:</b> {prediction_results['estimated_progression']} D/year",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Stellest Effectiveness
        story.append(Paragraph("Stellest Lens Effectiveness", self.styles['CustomHeading']))
        stellest_data = prediction_results['stellest_effectiveness']
        
        effectiveness_table = [
            ['Metric', 'Value'],
            ['Without Stellest', f"{stellest_data['without_stellest']} D/year"],
            ['With Stellest', f"{stellest_data['with_stellest']} D/year"],
            ['Progression Reduction', f"{stellest_data['reduction_percentage']}%"]
        ]
        
        eff_table = Table(effectiveness_table, colWidths=[3 * inch, 2.5 * inch])
        eff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06A77D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(eff_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Risk Factors
        story.append(Paragraph("Risk Factor Analysis", self.styles['CustomHeading']))
        
        risk_factors = []
        if patient_info.get('myopic_parents', 0) > 0:
            risk_factors.append(f"• Parental myopia history ({['None', 'One parent', 'Both parents'][patient_info.get('myopic_parents', 0)]})")
        
        if patient_info.get('age', 15) < 12:
            risk_factors.append(f"• Young age ({patient_info.get('age')} years) - higher progression risk")
        
        if patient_info.get('screen_hours', 0) > 3:
            risk_factors.append(f"• High screen time ({patient_info.get('screen_hours')} hours/day)")
        
        if patient_info.get('outdoor_hours', 0) < 2:
            risk_factors.append(f"• Limited outdoor time ({patient_info.get('outdoor_hours')} hours/day)")
        
        if patient_info.get('myopia_severity', 0) > 3:
            risk_factors.append(f"• High myopia severity ({patient_info.get('myopia_severity')} D)")
        
        if patient_info.get('avg_axial_length', 23) > 24.5:
            risk_factors.append(f"• Elongated axial length ({patient_info.get('avg_axial_length')} mm)")
        
        if risk_factors:
            story.append(Paragraph("Identified Risk Factors:", self.styles['CustomBody']))
            for factor in risk_factors:
                story.append(Paragraph(factor, self.styles['CustomBody']))
        else:
            story.append(Paragraph("No significant risk factors identified.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Recommendations
        story.append(Paragraph("Clinical Recommendations", self.styles['CustomHeading']))
        recommendations = self._generate_recommendations(patient_info, prediction_results)
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Detailed Analysis Section
        story.append(Paragraph("Detailed Clinical Analysis", self.styles['CustomHeading']))
        
        analysis_items = []
        
        # Age-based analysis
        if patient_info.get('age', 15) < 10:
            analysis_items.append(f"<b>Age Factor:</b> Patient is {patient_info.get('age')} years old, which indicates higher progression risk. Younger children typically show faster myopia progression.")
        elif patient_info.get('age', 15) < 12:
            analysis_items.append(f"<b>Age Factor:</b> Patient is {patient_info.get('age')} years old, indicating moderate progression risk. Close monitoring is recommended.")
        else:
            analysis_items.append(f"<b>Age Factor:</b> Patient is {patient_info.get('age')} years old. Progression typically slows with age, but monitoring remains important.")
        
        # Genetic analysis
        myopic_parents = patient_info.get('myopic_parents', 0)
        if myopic_parents == 2:
            analysis_items.append("<b>Genetic Risk:</b> Both parents have myopia, indicating strong genetic predisposition. This increases progression risk significantly.")
        elif myopic_parents == 1:
            analysis_items.append("<b>Genetic Risk:</b> One parent has myopia, indicating moderate genetic predisposition.")
        else:
            analysis_items.append("<b>Genetic Risk:</b> No parental myopia history. Lower genetic risk factor.")
        
        # Severity analysis
        severity = patient_info.get('myopia_severity', 0)
        if severity > 3:
            analysis_items.append(f"<b>Myopia Severity:</b> High myopia ({severity:.2f} D) detected. Requires intensive management and regular monitoring.")
        elif severity > 1.5:
            analysis_items.append(f"<b>Myopia Severity:</b> Moderate myopia ({severity:.2f} D). Appropriate treatment and monitoring recommended.")
        else:
            analysis_items.append(f"<b>Myopia Severity:</b> Mild myopia ({severity:.2f} D). Early intervention can help slow progression.")
        
        # Axial length analysis
        axial_len = patient_info.get('avg_axial_length', 23)
        if axial_len > 24.5:
            analysis_items.append(f"<b>Axial Length:</b> {axial_len:.2f} mm - Above normal range (>24.5mm). Indicates significant eye elongation and higher risk.")
        elif axial_len > 24.0:
            analysis_items.append(f"<b>Axial Length:</b> {axial_len:.2f} mm - Approaching upper normal limit. Regular monitoring essential.")
        else:
            analysis_items.append(f"<b>Axial Length:</b> {axial_len:.2f} mm - Within normal range. Continue preventive measures.")
        
        # Compliance analysis
        compliance = patient_info.get('compliance_score', 1) * 100
        if compliance >= 90:
            analysis_items.append(f"<b>Treatment Compliance:</b> Excellent ({compliance:.0f}%). Patient is wearing lenses as recommended.")
        elif compliance >= 75:
            analysis_items.append(f"<b>Treatment Compliance:</b> Good ({compliance:.0f}%). Slight improvement could enhance effectiveness.")
        else:
            analysis_items.append(f"<b>Treatment Compliance:</b> Needs improvement ({compliance:.0f}%). Better compliance will significantly improve outcomes.")
        
        # Lifestyle analysis
        screen_hrs = patient_info.get('screen_hours', 0)
        outdoor_hrs = patient_info.get('outdoor_hours', 0)
        if screen_hrs > 4:
            analysis_items.append(f"<b>Lifestyle Risk:</b> High screen time ({screen_hrs} hours/day) increases progression risk. Reduction recommended.")
        if outdoor_hrs < 2:
            analysis_items.append(f"<b>Lifestyle Risk:</b> Low outdoor time ({outdoor_hrs} hours/day). Increasing outdoor activity to 2+ hours/day is protective.")
        if screen_hrs <= 4 and outdoor_hrs >= 2:
            analysis_items.append("<b>Lifestyle Risk:</b> Screen time and outdoor activity levels are within acceptable ranges.")
        
        for item in analysis_items:
            story.append(Paragraph(f"• {item}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Treatment Effectiveness Summary
        story.append(Paragraph("Treatment Effectiveness Summary", self.styles['CustomHeading']))
        stellest_data = prediction_results['stellest_effectiveness']
        story.append(Paragraph(
            f"<b>Projected Outcome:</b> With current compliance, Stellest lens is expected to reduce progression by "
            f"<b>{stellest_data['reduction_percentage']:.1f}%</b>. Without treatment, progression would be "
            f"<b>{stellest_data['without_stellest']:.2f} D/year</b>, compared to "
            f"<b>{stellest_data['with_stellest']:.2f} D/year</b> with Stellest.",
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Monitoring Schedule
        story.append(Paragraph("Recommended Monitoring Schedule", self.styles['CustomHeading']))
        
        if risk_category == "High Risk":
            monitoring = "Every 3 months"
        elif risk_category == "Medium Risk":
            monitoring = "Every 4-6 months"
        else:
            monitoring = "Every 6 months"
        
        story.append(Paragraph(f"<b>Follow-up Interval:</b> {monitoring}", self.styles['CustomBody']))
        story.append(Paragraph(
            "<b>Monitoring Parameters:</b><br/>"
            "• Refraction (spherical and cylindrical)<br/>"
            "• Axial length measurement<br/>"
            "• Visual acuity assessment<br/>"
            "• Compliance with Stellest wearing schedule<br/>"
            "• Quality of life assessment",
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Risk Factor Breakdown
        if risk_factors:
            story.append(Paragraph("Risk Factor Breakdown", self.styles['CustomHeading']))
            story.append(Paragraph(
                f"<b>Overall Risk Score:</b> {risk_factors['total_score']:.1f} / {risk_factors['max_possible_score']} "
                f"({risk_factors['risk_percentage']:.0f}% of maximum risk)",
                self.styles['CustomBody']
            ))
            
            story.append(Paragraph("<b>Contributing Factors:</b>", self.styles['CustomBody']))
            for factor in risk_factors['factors']:
                impact_color = '#C73E1D' if factor['impact'] == 'High' else '#F18F01' if factor['impact'] == 'Medium' else '#06A77D'
                story.append(Paragraph(
                    f"• <b>{factor['factor']}</b> ({factor['impact']} Impact, Score: {factor['score']:.1f}): {factor['description']}",
                    self.styles['CustomBody']
                ))
            
            story.append(Spacer(1, 0.3 * inch))
        
        # Progression Timeline
        if progression_timeline:
            story.append(Paragraph("Long-term Progression Projections", self.styles['CustomHeading']))
            
            timeline_data = [['Year', 'Age', 'With Stellest (D)', 'Without Treatment (D)', 'Saved (D)']]
            for t in progression_timeline:
                timeline_data.append([
                    str(t['year']),
                    f"{t['projected_age']:.1f}",
                    f"{t['severity_with_treatment']:.2f}",
                    f"{t['severity_without_treatment']:.2f}",
                    f"{t['saved_diopters']:.2f}"
                ])
            
            timeline_table = Table(timeline_data, colWidths=[0.8 * inch, 0.8 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ]))
            story.append(timeline_table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Comparative Statistics
        if comparative_stats:
            story.append(Paragraph("Population Comparison Analysis", self.styles['CustomHeading']))
            
            story.append(Paragraph(
                f"<b>Age Group:</b> {comparative_stats['age_group']} years<br/>"
                f"<b>Population Average Severity:</b> {comparative_stats['population_avg_severity']} D<br/>"
                f"<b>Patient Severity:</b> {comparative_stats['patient_severity']:.2f} D<br/>"
                f"<b>Difference:</b> {comparative_stats['severity_difference']:+.2f} D<br/>"
                f"<b>Comparison:</b> {comparative_stats['comparison']}<br/><br/>"
                f"<b>Axial Length:</b><br/>"
                f"• Normal for age: {comparative_stats['normal_axial_length']:.2f} mm<br/>"
                f"• Patient: {comparative_stats['patient_axial_length']:.2f} mm<br/>"
                f"• Difference: {comparative_stats['axial_length_difference']:+.2f} mm",
                self.styles['CustomBody']
            ))
            
            story.append(Spacer(1, 0.3 * inch))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Footer disclaimer
        story.append(Paragraph(
            "<i>This report is generated by Stellest AI using machine learning algorithms trained on clinical data. "
            "It should be used as a clinical decision support tool and not as a replacement for professional medical judgment. "
            "Please consult with an eye care professional for comprehensive assessment and treatment planning.</i>",
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _get_risk_color(self, risk_category):
        """Get color code for risk category"""
        color_map = {
            'Low Risk': '#06A77D',
            'Medium Risk': '#F18F01',
            'High Risk': '#C73E1D'
        }
        return color_map.get(risk_category, '#000000')
    
    def _generate_recommendations(self, patient_info, prediction_results):
        """Generate personalized recommendations"""
        recommendations = []
        
        risk_category = prediction_results['risk_category']
        
        # General recommendations
        recommendations.append(
            "Continue wearing Stellest lenses for at least 12 hours daily to achieve optimal myopia control effect."
        )
        
        # Risk-specific recommendations
        if risk_category == "High Risk":
            recommendations.append(
                "Given the high progression risk, consider additional myopia control strategies such as "
                "low-dose atropine in consultation with your ophthalmologist."
            )
            recommendations.append(
                "Schedule frequent follow-ups (every 3 months) to monitor progression closely."
            )
        
        # Environmental recommendations
        if patient_info.get('screen_hours', 0) > 3:
            recommendations.append(
                f"Reduce screen time from current {patient_info.get('screen_hours')} hours/day to less than 2 hours. "
                "Follow the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds."
            )
        
        if patient_info.get('outdoor_hours', 0) < 2:
            recommendations.append(
                f"Increase outdoor time from current {patient_info.get('outdoor_hours')} hours/day to at least 2 hours daily. "
                "Outdoor activity has been shown to have protective effects against myopia progression."
            )
        
        # Compliance recommendations
        if patient_info.get('compliance_score', 1) < 0.8:
            recommendations.append(
                "Improve compliance with Stellest wearing schedule to maximize treatment effectiveness."
            )
        
        # Axial length specific
        if patient_info.get('avg_axial_length', 23) > 24.5:
            recommendations.append(
                "Axial length is above normal range. Regular monitoring is essential to track any further elongation."
            )
        
        recommendations.append(
            "Maintain good reading distance (at least 30cm from eyes) and ensure adequate lighting during near work."
        )
        
        recommendations.append(
            "Consider nutritional support with foods rich in Omega-3 fatty acids and antioxidants for overall eye health."
        )
        
        return recommendations


if __name__ == "__main__":
    # Test report generation
    generator = MyopiaReportGenerator()
    print("✓ Report generator initialized")
