# Job Search AI

## Mô tả

Project này giúp tìm kiếm và gợi ý các công việc phù hợp dựa trên mô tả công việc và hồ sơ ứng viên (resume).  
Sử dụng mô hình `all-MiniLM-L6-v2` để chuyển mô tả và resume thành vector embedding, rồi so sánh để tìm công việc tương thích.

---

## 📸 Giao diện minh họa

### Chọn ngành nghề để crawl:
![select-category](images/nganhnghe.png)

### Kết quả đề xuất công việc:
![results](images/ketqua.png)


## Yêu cầu

- Python >= 3.8
- Các thư viện cần thiết:
  ```bash
  pip install pandas python-dotenv sentence-transformers torch pdfplumber
