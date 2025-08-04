# resume.py

import pdfplumber
import os

RESUME_PATH = f"D:/job-search-ai/DataScientist_PhanAnhNguyen.pdf"  # Đường dẫn đến file PDF cần trích xuất
WORK_DIR = "D:/job-search-ai"  # Thư mục để lưu file resume.txt

def extract_resume_text(RESUME_PATH=RESUME_PATH):
    # Đọc PDF và trích xuất text
    with pdfplumber.open(RESUME_PATH) as pdf:
        resume_text = "\n".join(
            [page.extract_text() for page in pdf.pages if page.extract_text()]
        )

    # In ra 20 dòng đầu tiên
    print("\n📄 20 dòng đầu trong resume:")
    for i, line in enumerate(resume_text.splitlines()[:20], 1):
        print(f"{i:02d}: {line}")

    # Lưu lại vào file .txt
    os.makedirs(WORK_DIR, exist_ok=True)
    resume_txt_path = os.path.join(WORK_DIR, "resume.txt")
    with open(resume_txt_path, "w", encoding="utf-8") as f:
        f.write(resume_text)

    print(f"\n✅ Văn bản hồ sơ đã được lưu tại: {resume_txt_path}")
    return resume_txt_path

# Cho phép gọi từ script hoặc import
if __name__ == "__main__":
    extract_resume_text()
