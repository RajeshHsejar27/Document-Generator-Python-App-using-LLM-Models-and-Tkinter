"""
Report Generation Module
Handles creation of Markdown and PDF reports from user notes and images.
"""

import os
import shutil
from datetime import datetime
from typing import List
import logging
from reportlab.lib.enums import TA_CENTER


logger = logging.getLogger(__name__)

# Try to import required libraries, handle gracefully if not available
try:
    import markdown2
    MARKDOWN2_AVAILABLE = True
except ImportError:
    MARKDOWN2_AVAILABLE = False
    logger.warning("markdown2 not available. Install with: pip install markdown2")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available. Install with: pip install reportlab")


class ReportGenerator:
    """Handles generation of Markdown and PDF reports."""
    
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        self.images_dir = os.path.join(os.path.dirname(__file__), 'images')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        for directory in [self.reports_dir, self.images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
    
    def generate_report(self, notes: str, images: List[str], summary: str, filename: str):
        """
        Generate both Markdown and PDF reports.
        
        Args:
            notes: User's daily notes
            images: List of image file paths
            summary: AI-generated summary
            filename: Base filename for the reports
        """
        logger.info(f"Generating report: {filename}")
        
        # Copy images to reports/images folder
        copied_images = self._copy_images_to_reports(images, filename)
        
        # Generate Markdown report
        markdown_path = self._generate_markdown_report(
            notes, copied_images, summary, filename
        )
        
        # Generate PDF report
        pdf_path = self._generate_pdf_report(
            notes, copied_images, summary, filename, markdown_path
        )
        
        logger.info(f"Reports generated successfully: {markdown_path}, {pdf_path}")
        return markdown_path, pdf_path
    
    def generate_detailed_report(self, original_notes: str, detailed_notes: str, 
                                images: List[str], summary: str, filename: str):
        """
        Generate reports with both original and detailed notes.
        
        Args:
            original_notes: User's original daily notes
            detailed_notes: AI-generated detailed version
            images: List of image file paths
            summary: AI-generated summary
            filename: Base filename for the reports
        """
        logger.info(f"Generating detailed report: {filename}")
        
        # Copy images to reports/images folder
        copied_images = self._copy_images_to_reports(images, filename)
        
        # Generate Markdown report with both versions
        markdown_path = self._generate_detailed_markdown_report(
            original_notes, detailed_notes, copied_images, summary, filename
        )
        
        # Generate PDF report with both versions
        pdf_path = self._generate_detailed_pdf_report(
            original_notes, detailed_notes, copied_images, summary, filename
        )
        
        logger.info(f"Detailed reports generated successfully: {markdown_path}, {pdf_path}")
        return markdown_path, pdf_path
    
    def _copy_images_to_reports(self, image_paths: List[str], filename: str) -> List[dict]:
        """
        Copy images to the reports/images folder and return relative paths.
        
        Args:
            image_paths: List of source image paths
            filename: Base filename for organizing images
            
        Returns:
            List of dictionaries with image information
        """
        copied_images = []
        
        if not image_paths:
            return copied_images
        
        # Create subfolder for this report's images
        report_images_dir = os.path.join(self.reports_dir, 'images', filename)
        if not os.path.exists(report_images_dir):
            os.makedirs(report_images_dir)
        
        for i, image_path in enumerate(image_paths):
            try:
                # Get file extension
                _, ext = os.path.splitext(image_path)
                
                # Create new filename
                new_filename = f"image_{i+1:02d}{ext}"
                dest_path = os.path.join(report_images_dir, new_filename)
                
                # Copy the image
                shutil.copy2(image_path, dest_path)
                
                # Store relative path info
                relative_path = f"images/{filename}/{new_filename}"
                copied_images.append({
                    'original_path': image_path,
                    'dest_path': dest_path,
                    'relative_path': relative_path,
                    'filename': new_filename,
                    'original_name': os.path.basename(image_path)
                })
                
                logger.info(f"Copied image: {image_path} -> {dest_path}")
                
            except Exception as e:
                logger.error(f"Error copying image {image_path}: {e}")
        
        return copied_images
    
    def _generate_markdown_report(self, notes: str, images: List[dict], 
                                summary: str, filename: str) -> str:
        """Generate a Markdown report."""
        # Create timestamp
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M")
        
        # Build markdown content
        markdown_content = f"""# Daily Log – {date_str}

*Generated on {date_str} at {time_str}*

## 📝 Key Activities

{self._format_notes_for_markdown(notes)}

"""
        
        # Add images section if images exist
        if images:
            markdown_content += "## 🖼️ Images\n\n"
            for img in images:
                markdown_content += f"![{img['original_name']}]({img['relative_path']})\n\n"
                markdown_content += f"*{img['original_name']}*\n\n"
        
        # Add summary section
        markdown_content += f"""## 🧠 Summary

{summary}

---

*Report generated by Personal Documentation Assistant*
"""
        
        # Write markdown file
        markdown_path = os.path.join(self.reports_dir, f"{filename}.md")
        try:
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Markdown report saved: {markdown_path}")
        except Exception as e:
            logger.error(f"Error writing markdown file: {e}")
            raise
        
        return markdown_path
    
    def _generate_detailed_markdown_report(self, original_notes: str, detailed_notes: str,
                                         images: List[dict], summary: str, filename: str) -> str:
        """Generate a Markdown report with both original and detailed notes."""
        # Create timestamp
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M")
        
        # Build markdown content
        markdown_content = f"""# {filename} {date_str}

*Generated on {date_str} at {time_str}*

## 📝 Original Notes

{self._format_notes_for_markdown(original_notes)}

## 📋 Detailed Documentation

{detailed_notes}

"""
        
        # Add images section if images exist
        if images:
            markdown_content += "## 🖼️ Images\n\n"
            for img in images:
                markdown_content += f"![{img['original_name']}]({img['relative_path']})\n\n"
                markdown_content += f"*{img['original_name']}*\n\n"
        
        # Add summary section
        markdown_content += f"""## 🧠 Summary

{summary}

---

*Detailed report generated by Personal Documentation Assistant*
"""
        
        # Write markdown file
        markdown_path = os.path.join(self.reports_dir, f"{filename}-detailed.md")
        try:
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Detailed markdown report saved: {markdown_path}")
        except Exception as e:
            logger.error(f"Error writing detailed markdown file: {e}")
            raise
        
        return markdown_path
    
    def _generate_pdf_report(self, notes: str, images: List[dict], 
                           summary: str, filename: str, markdown_path: str) -> str:
        """Generate a PDF report."""
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available, skipping PDF generation")
            return None
        
        pdf_path = os.path.join(self.reports_dir, f"{filename}.pdf")
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content elements)
            story = []
            styles = getSampleStyleSheet()

            #Define a custom 'Caption' style
            caption_style = ParagraphStyle(
                name='Caption',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=6,
            )

            # Add it to the stylesheet
            styles.add(caption_style)
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2E3440')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#3B4252')
            )
            
            # Title
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            title = Paragraph(f"Daily Log – {date_str}", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Generated timestamp
            time_str = timestamp.strftime("%H:%M")
            subtitle = Paragraph(
                f"<i>Generated on {date_str} at {time_str}</i>",
                styles['Normal']
            )
            story.append(subtitle)
            story.append(Spacer(1, 24))
            
            # Key Activities section
            activities_heading = Paragraph("📝 Key Activities", heading_style)
            story.append(activities_heading)
            
            formatted_notes = self._format_notes_for_pdf(notes, styles)
            story.append(formatted_notes)
            story.append(Spacer(1, 20))
            
            # Images section
            if images:
                images_heading = Paragraph("🖼️ Images", heading_style)
                story.append(images_heading)
                
                for img in images:
                    try:
                        # Add image
                        img_element = RLImage(
                            img['dest_path'],
                            width=4*inch,
                            height=3*inch,
                            kind='proportional'
                        )
                        story.append(img_element)
                        
                        # Add image caption
                        caption = Paragraph(
                            f"<i>{img['original_name']}</i>",
                            styles['Caption']
                        )
                        story.append(caption)
                        story.append(Spacer(1, 12))
                        
                    except Exception as e:
                        logger.error(f"Error adding image to PDF: {e}")
                        # Add error message instead
                        error_msg = Paragraph(
                            f"<i>Error loading image: {img['original_name']}</i>",
                            styles['Caption']
                        )
                        story.append(error_msg)
                        story.append(Spacer(1, 12))
            
            # Summary section
            summary_heading = Paragraph("🧠 Summary", heading_style)
            story.append(summary_heading)
            
            summary_para = Paragraph(summary, styles['Normal'])
            story.append(summary_para)
            story.append(Spacer(1, 24))
            
            # Footer
            footer = Paragraph(
                "<i>Report generated by Personal Documentation Assistant</i>",
                styles['Caption']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report saved: {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
        
        return pdf_path
    
    def _generate_detailed_pdf_report(self, original_notes: str, detailed_notes: str,
                                    images: List[dict], summary: str, filename: str) -> str:
        """Generate a PDF report with both original and detailed notes."""
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available, skipping detailed PDF generation")
            return None
        
        pdf_path = os.path.join(self.reports_dir, f"{filename}-detailed.pdf")
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story (content elements)
            story = []
            styles = getSampleStyleSheet()
            
            # Define a custom 'Caption' style
            caption_style = ParagraphStyle(
                name='Caption',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=6,
            )

            # Add it to the stylesheet
            styles.add(caption_style)
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2E3440')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.HexColor('#3B4252')
            )
            
            # Title
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            title = Paragraph(f"{filename} {date_str}", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Generated timestamp
            time_str = timestamp.strftime("%H:%M")
            subtitle = Paragraph(
                f"<i>Generated on {date_str} at {time_str}</i>",
                styles['Normal']
            )
            story.append(subtitle)
            story.append(Spacer(1, 24))
            
            # Original Notes section
            original_heading = Paragraph("📝 Original Notes", heading_style)
            story.append(original_heading)
            
            formatted_original = self._format_notes_for_pdf(original_notes, styles)
            story.append(formatted_original)
            story.append(Spacer(1, 20))
            
            # Detailed Documentation section
            detailed_heading = Paragraph("📋 Detailed Documentation", heading_style)
            story.append(detailed_heading)
            
            detailed_para = Paragraph(detailed_notes.replace('\n', '<br/>'), styles['Normal'])
            story.append(detailed_para)
            story.append(Spacer(1, 20))
            
            # Images section
            if images:
                images_heading = Paragraph("🖼️ Images", heading_style)
                story.append(images_heading)
                
                for img in images:
                    try:
                        # Add image
                        img_element = RLImage(
                            img['dest_path'],
                            width=4*inch,
                            height=3*inch,
                            kind='proportional'
                        )
                        story.append(img_element)
                        
                        # Add image caption
                        caption = Paragraph(
                            f"<i>{img['original_name']}</i>",
                            styles['Caption']
                        )
                        story.append(caption)
                        story.append(Spacer(1, 12))
                        
                    except Exception as e:
                        logger.error(f"Error adding image to detailed PDF: {e}")
                        # Add error message instead
                        error_msg = Paragraph(
                            f"<i>Error loading image: {img['original_name']}</i>",
                            styles['Caption']
                        )
                        story.append(error_msg)
                        story.append(Spacer(1, 12))
            
            # Summary section
            summary_heading = Paragraph("🧠 Summary", heading_style)
            story.append(summary_heading)
            
            summary_para = Paragraph(summary, styles['Normal'])
            story.append(summary_para)
            story.append(Spacer(1, 24))
            
            # Footer
            footer = Paragraph(
                "<i>Detailed report generated by Personal Documentation Assistant</i>",
                styles['Caption']
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            logger.info(f"Detailed PDF report saved: {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error generating detailed PDF: {e}")
            raise
        
        return pdf_path
    
    def _format_notes_for_markdown(self, notes: str) -> str:
        """Format notes for markdown display."""
        lines = notes.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # Convert bullet points
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if not line.startswith('- '):
                    line = '- ' + line[1:].strip()
            else:
                # Add bullet point if not present
                line = '- ' + line
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_notes_for_pdf(self, notes: str, styles) -> Paragraph:
        """Format notes for PDF display."""
        lines = notes.strip().split('\n')
        formatted_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_text.append('<br/>')
                continue
            
            # Convert to bullet points
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                line = '• ' + line[1:].strip()
            else:
                line = '• ' + line
            
            formatted_text.append(line + '<br/>')
        
        content = ''.join(formatted_text)
        return Paragraph(content, styles['Normal'])