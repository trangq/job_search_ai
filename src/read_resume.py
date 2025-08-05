import pdfplumber
import os

# Thư mục workspace mặc định nằm cùng thư mục file này
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = os.path.join(BASE_DIR, "workspace")


print("BASE_DIR:", BASE_DIR)
print("WORK_DIR:", WORK_DIR)
def extract_resume_text(resume_pdf_path, output_dir=WORK_DIR):
    """
    Đọc file PDF resume, trích xuất text, lưu ra file txt trong output_dir.
    
    Args:
        resume_pdf_path (str): Đường dẫn file PDF resume.
        output_dir (str): Thư mục lưu file txt kết quả.
    
    Returns:
        tuple: (resume_text (str), resume_txt_path (str))
    """
    os.makedirs(output_dir, exist_ok=True)

    with pdfplumber.open(resume_pdf_path) as pdf:
        resume_text = "\n".join(
            [page.extract_text() for page in pdf.pages if page.extract_text()]
        )
    
    print("\n📄 20 dòng đầu trong resume:")
    for i, line in enumerate(resume_text.splitlines()[:20], 1):
        print(f"{i:02d}: {line}")

    resume_txt_path = os.path.join(output_dir, "resume.txt")
    with open(resume_txt_path, "w", encoding="utf-8") as f:
        f.write(resume_text)

    print(f"\n✅ Văn bản hồ sơ đã được lưu tại: {resume_txt_path}")
    return resume_text, resume_txt_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        resume_pdf_path = sys.argv[1]
    else:
        print("Vui lòng truyền đường dẫn file PDF resume khi chạy script.")
        sys.exit(1)
    extract_resume_text(resume_pdf_path)
    print("Hãy kiểm tra file resume.txt trong thư mục workspace.")