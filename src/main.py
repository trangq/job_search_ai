import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from read_resume import extract_resume_text
from careerviet import CareervietSpider
import nest_asyncio
from scrapy.crawler import CrawlerProcess

nest_asyncio.apply()

model = SentenceTransformer('all-MiniLM-L6-v2')
WORK_DIR = "D:/job-search-ai"
JOBS_CSV_PATH = f"{WORK_DIR}/careerviet.csv"

def run_careerviet_spider(start_urls):
    process = CrawlerProcess()
    process.crawl(CareervietSpider, start_urls=start_urls)
    process.start()

def generate_embeddings(texts, to_tensor=True):
    texts = [str(t).strip() for t in texts if str(t).strip() != ""]
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

def main():
    load_dotenv()

    # 1. Scrape với link động
    urls_to_scrape = ["https://careerviet.vn/viec-lam/data-scientist-k-vi.html"]
    run_careerviet_spider(urls_to_scrape)

    # 2. Đọc dữ liệu scrape xong
    df_jobs = pd.read_csv(JOBS_CSV_PATH)
    df_jobs = df_jobs.drop_duplicates(subset=["job_url"])
    df_jobs = df_jobs.fillna("")
    df_jobs["description"] = df_jobs["description"].astype(str)
    df_jobs = df_jobs[df_jobs["description"].str.strip() != ""]

    job_descriptions = df_jobs["description"].tolist()
    job_urls = df_jobs["job_url"].tolist()

    # 3. Extract resume text
    extract_resume_text(RESUME_PATH=f"{WORK_DIR}/DataScientist_PhanAnhNguyen.pdf")

    with open(f"{WORK_DIR}/resume.txt", "r", encoding="utf-8") as f:
        resume = f.read().strip()

    if not resume:
        raise ValueError("Resume text is empty!")

    # 4. Tạo embeddings
    job_vectors = generate_embeddings(job_descriptions, to_tensor=True)
    resume_vector = generate_embeddings([resume], to_tensor=True)[0]

    # 5. Thêm vào vector store
    vector_store = VectorStore()
    for vector, desc, url in zip(job_vectors, job_descriptions, job_urls):
        vector_store.add_vector(vector, desc, url)

    # 6. QA và trả lời
    qa_chain = QAChain(vector_store)
    query = "What jobs match my skills?, give me link"
    response = qa_chain.answer_query(query, resume_vector)

    print("Response:", response)


if __name__ == "__main__":
    main()
