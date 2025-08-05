import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from src.read_resume import extract_resume_text
from src.main import generate_embeddings, VectorStore, QAChain, WORK_DIR, JOBS_CSV_PATH
from dotenv import load_dotenv
from src.careerviet import CareervietSpider
import nest_asyncio
from scrapy.crawler import CrawlerProcess
from src.main import run_careerviet_spider, WORK_DIR

# Optional: Load environment variables (nếu dùng .env)
load_dotenv()

st.set_page_config(page_title="Job Match AI", layout="wide")

st.title("Job Match AI: Find Jobs That Fit Your CV")
st.markdown("""
## User Guide
1. Tải lên CV của bạn dưới định dạng PDF bằng trình tải tệp bên dưới.
2. Chọn lĩnh vực ngành nghề.
3. Ứng dụng sẽ trích xuất nội dung từ CV của bạn và so khớp với các công việc hiện có.
4. Bạn sẽ nhận được danh sách các công việc phù hợp nhất kèm theo liên kết để ứng tuyển.
""")

# Mapping ngành nghề -> URL
category_to_url = {
    "Bán hàng / Kinh doanh": "https://careerviet.vn/viec-lam/ban-hang-kinh-doanh-c31-vi.html",
    "Hành chính / Thư ký": "https://careerviet.vn/viec-lam/hanh-chinh-thu-ky-c3-vi.html",
    "Kế toán / Kiểm toán": "https://careerviet.vn/viec-lam/ke-toan-kiem-toan-c1-vi.html",
    "Tiếp thị / Marketing": "https://careerviet.vn/viec-lam/tiep-thi-marketing-c7-vi.html",
    "Nhân sự": "https://careerviet.vn/viec-lam/nhan-su-c25-vi.html",
    "CNTT - Phần mềm": "https://careerviet.vn/viec-lam/cntt-phan-mem-c36-vi.html",
    "CNTT - Phần cứng / Mạng": "https://careerviet.vn/viec-lam/cntt-phan-cung-mang-c24-vi.html",
    "Cơ khí / Ô tô / Tự động hóa": "https://careerviet.vn/viec-lam/co-khi-o-to-tu-dong-hoa-c5-vi.html",
    "Dầu khí": "https://careerviet.vn/viec-lam/dau-khi-c13-vi.html",
    "Dệt may / Da giày / Thời trang": "https://careerviet.vn/viec-lam/det-may-da-giay-thoi-trang-c10-vi.html",
    "Công nghệ thực phẩm / Dinh dưỡng": "https://careerviet.vn/viec-lam/cong-nghe-thuc-pham-dinh-duong-c52-vi.html",
}

# Hiển thị selectbox thay vì nhập URL
selected_category = st.selectbox("Chọn ngành nghề để thu thập việc làm:", list(category_to_url.keys()))
selected_url = category_to_url[selected_category]

# Nút crawl
crawl_btn = st.button("Crawl jobs from selected category")

if crawl_btn:
    with st.spinner(f"Đang thu thập việc làm cho ngành: {selected_category}"):
        run_careerviet_spider([selected_url])
        st.success("Crawling completed! You can now upload your CV.")
        st.info(f"Crawled jobs saved to: `{WORK_DIR}`")

uploaded_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])

if uploaded_file is not None:
    resume_path = os.path.join(WORK_DIR, "uploaded_resume.pdf")
    with open(resume_path, "wb") as f:
        f.write(uploaded_file.read())
    try:
        # Gọi hàm với tên tham số đúng
        extract_resume_text(resume_pdf_path=resume_path)
        st.success("Resume uploaded and text extracted successfully!")
        with open(os.path.join(WORK_DIR, "resume.txt"), "r", encoding="utf-8") as f:
            resume = f.read().strip()
        if not resume:
            st.error("Resume text extraction failed or file is empty.")
        else:
            st.success("Resume uploaded and extracted successfully!")
            # Load jobs data
            df_jobs = pd.read_csv(JOBS_CSV_PATH)
            df_jobs = df_jobs.drop_duplicates(subset=["job_url"])
            df_jobs = df_jobs.fillna("")
            df_jobs["description"] = df_jobs["description"].astype(str)
            df_jobs = df_jobs[df_jobs["description"].str.strip() != ""]
            job_descriptions = df_jobs["description"].tolist()
            job_urls = df_jobs["job_url"].tolist()

            # Embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            job_vectors = generate_embeddings(job_descriptions, to_tensor=True)
            resume_vector = generate_embeddings([resume], to_tensor=True)[0]

            # Vector store
            vector_store = VectorStore()
            for vector, desc, url in zip(job_vectors, job_descriptions, job_urls):
                vector_store.add_vector(vector, desc, url)

            # QA
            qa_chain = QAChain(vector_store)
            query = "What jobs match my skills? Give me links"
            response = qa_chain.answer_query(query, resume_vector)

            st.markdown("### Top Matching Jobs")
            for line in response.split("\n"):
                if line.startswith("Link apply:"):
                    url = line.replace("Link apply: ", "").strip()
                    st.markdown(f"[Apply here]({url})")
                else:
                    st.write(line)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload your CV to get job recommendations.")
