import os
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from read_resume import extract_resume_text
from careerviet import CareervietSpider
import nest_asyncio
from scrapy.crawler import CrawlerProcess

# Load biến môi trường
load_dotenv()

# Thiết lập thư mục mặc định nếu không có .env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = os.path.join(BASE_DIR, "workspace")
JOBS_CSV_PATH = os.path.join(WORK_DIR, "careerviet.csv")


print("BASE_DIR:", BASE_DIR)
print("WORK_DIR:", WORK_DIR)
print("JOBS_CSV_PATH:", JOBS_CSV_PATH)
# Tạo thư mục nếu chưa có
os.makedirs(WORK_DIR, exist_ok=True)

# Cho phép Scrapy chạy trong Jupyter/Streamlit
nest_asyncio.apply()

# Load model embedding
model = SentenceTransformer('all-MiniLM-L6-v2')


# ------------------ Hàm phụ ------------------

def run_careerviet_spider(start_urls):
    process = CrawlerProcess()
    process.crawl(CareervietSpider, start_urls=start_urls)
    process.start()


def generate_embeddings(texts, to_tensor=True):
    texts = [str(t).strip() for t in texts if str(t).strip()]
    return model.encode(texts, convert_to_tensor=to_tensor, show_progress_bar=True)


class VectorStore:
    def __init__(self):
        self.vectors = []
        self.texts = []
        self.urls = []

    def add_vector(self, vector, text, url):
        self.vectors.append(vector)
        self.texts.append(text)
        self.urls.append(url)

    def search(self, query_vector, top_k=5):
        import torch
        vectors_tensor = torch.stack(self.vectors)
        scores = util.cos_sim(query_vector, vectors_tensor)[0]
        top_results = scores.topk(k=top_k)
        return [
            (self.texts[idx], self.urls[idx], float(scores[idx]))
            for idx in top_results.indices
        ]


class QAChain:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def answer_query(self, query, resume_vector):
        top_matches = self.vector_store.search(resume_vector)
        response = "Top matching jobs:\n"
        for i, (job_text, job_url, score) in enumerate(top_matches):
            response += (
                f"\n{i+1}. Score: {score:.4f}\n"
                f"{job_text[:300]}...\n"
                f"Link apply: {job_url}\n"
            )
        return response


# ------------------ Hàm chính ------------------

def main(cv_pdf_path=None, urls_to_scrape=None):
    print("🚀 Starting job matching pipeline...")

    if urls_to_scrape is None:
        urls_to_scrape = ["https://careerviet.vn/viec-lam/data-scientist-k-vi.html"]
    if cv_pdf_path is None:
        cv_pdf_path = os.path.join(WORK_DIR, "uploaded_resume.pdf")

    # 1. Crawl job listings
    print("🔍 Crawling job listings...")
    run_careerviet_spider(urls_to_scrape)

    # 2. Load job data
    print("📂 Loading job data from:", JOBS_CSV_PATH)
    df_jobs = pd.read_csv(JOBS_CSV_PATH)
    df_jobs = df_jobs.drop_duplicates(subset=["job_url"]).fillna("")
    df_jobs["description"] = df_jobs["description"].astype(str)
    df_jobs = df_jobs[df_jobs["description"].str.strip() != ""]

    job_descriptions = df_jobs["description"].tolist()
    job_urls = df_jobs["job_url"].tolist()

    # 3. Extract resume text
    print("📄 Extracting resume text from:", cv_pdf_path)
    extract_resume_text(resume_pdf_path=cv_pdf_path)

    resume_txt_path = os.path.join(WORK_DIR, "resume.txt")
    if not os.path.exists(resume_txt_path):
        raise FileNotFoundError(f"{resume_txt_path} not found. Did resume extraction fail?")

    with open(resume_txt_path, "r", encoding="utf-8") as f:
        resume = f.read().strip()

    if not resume:
        raise ValueError("Resume text is empty!")

    # 4. Generate embeddings
    print("🧠 Generating embeddings...")
    job_vectors = generate_embeddings(job_descriptions, to_tensor=True)
    resume_vector = generate_embeddings([resume], to_tensor=True)[0]

    # 5. Add vectors to store
    vector_store = VectorStore()
    for vector, desc, url in zip(job_vectors, job_descriptions, job_urls):
        vector_store.add_vector(vector, desc, url)

    # 6. Match jobs
    qa_chain = QAChain(vector_store)
    query = "What jobs match my skills? Give me link"
    response = qa_chain.answer_query(query, resume_vector)

    print("✅ Done. Top matches:\n")
    print(response)


# ------------------ Run nếu gọi trực tiếp ------------------

if __name__ == "__main__":
    main()
