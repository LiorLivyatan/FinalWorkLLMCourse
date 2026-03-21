# Area: Data Engineering
import sys
import fitz
from bidi.algorithm import get_display

def test_extraction(pdf_path):
    print(f"Testing PDF: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        raw_text = page.get_text("text").strip()
        print("\n=== RAW TEXT (First 300 chars) ===")
        print(raw_text[:300])
        
        # Apply python-bidi
        lines = raw_text.split('\n')
        corrected_lines = [get_display(line) for line in lines]
        corrected_text = "\n".join(corrected_lines)
        
        print("\n=== BIDI CORRECTED TEXT (First 300 chars) ===")
        print(corrected_text[:300])
        print("\n")
        
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    pdf_file = "course-material/00003.pdf"
    if not fitz.os.path.exists(pdf_file):
        print(f"Could not find {pdf_file}")
        sys.exit(1)
        
    test_extraction(pdf_file)
