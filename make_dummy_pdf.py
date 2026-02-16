from pypdf import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Test Document for RAG Automation")
    c.drawString(100, 730, "This is a sample PDF file created to test the RAG evaluation system.")
    c.drawString(100, 710, "The capital of France is Paris.")
    c.drawString(100, 690, "Photosynthesis is the process used by plants to convert light energy into chemical energy.")
    c.drawString(100, 670, "Python is a popular programming language.")
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_dummy_pdf("data/test_sample.pdf")
