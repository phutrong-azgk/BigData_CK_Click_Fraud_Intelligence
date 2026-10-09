# Click Fraud Intelligence

Project môn Big Data phân tích rủi ro click fraud trong quảng cáo di động. Hệ thống xử lý dữ liệu click thật bằng Apache Pig và Apache DataFu, sau đó hiển thị kết quả bằng Streamlit.

## Chạy project: Docker trên Windows

### 1. Chuẩn bị

- Cài Docker Desktop và kiểm tra `docker version` hiển thị cả **Client** lẫn **Server**.
- Tải `train_sample.csv` từ [TalkingData AdTracking Fraud Detection Challenge](https://www.kaggle.com/competitions/talkingdata-adtracking-fraud-detection/data).
- Đặt file vừa tải vào đúng đường dẫn `data/raw/train_sample.csv`.

> Dataset là dữ liệu Kaggle có điều kiện sử dụng riêng nên không được đưa vào GitHub hoặc Docker image.

### 2. Chạy

Mở PowerShell tại thư mục gốc project và chạy:

```powershell
docker compose up --build --force-recreate
```

Lần build đầu có thể mất vài phút vì Docker tải Java, Apache Pig và các thư viện Python. Các lần sau dùng cache nên nhanh hơn.

Khi log hiện `You can now view your Streamlit app`, mở:

```text
http://localhost:8501
```

`pipeline` tự thoát sau khi xử lý xong dữ liệu; đây là hành vi bình thường. Service `web` tiếp tục chạy dashboard.

Để dừng dashboard, nhấn `Ctrl + C`, sau đó dọn container nếu cần:

```powershell
docker compose down
```

## Mục tiêu

- Xử lý log click quảng cáo với Apache Pig ở local mode.
- Tổng hợp đặc trưng hành vi theo địa chỉ IP.
- Chấm điểm rủi ro dựa trên click volume, conversion và mức độ lặp lại app/channel.
- Trực quan hoá kết quả để hỗ trợ điều tra IP đáng ngờ.

## Dataset

Dự án dùng `train_sample.csv` gồm 100.000 log click đã ẩn danh của cuộc thi TalkingData:

```text
ip,app,device,os,channel,click_time,attributed_time,is_attributed
```

`is_attributed` có nghĩa click dẫn đến cài đặt ứng dụng. Đây **không phải** nhãn fraud trực tiếp; các nhãn rủi ro của project là suy luận từ hành vi.

## Risk scoring

Mỗi IP nhận một điểm từ 0 đến 100.

| Điều kiện | Điểm |
|---|---:|
| Ít nhất 30 clicks | 50 |
| 10–29 clicks | 30 |
| Không có conversion và có ít nhất 5 clicks | 25 |
| Tối đa 2 app và có ít nhất 5 clicks | 15 |
| Tối đa 2 channel và có ít nhất 5 clicks | 10 |

| Điểm | Nhãn |
|---|---|
| 70–100 | `HIGH_RISK` |
| 40–69 | `MEDIUM_RISK` |
| 0–39 | `LOW_RISK` |

## Dashboard

Dashboard hiển thị KPI tổng quan, click volume theo giờ, phân bố score, quan hệ click volume/conversion rate, top IP cần điều tra và bảng lọc kết quả. `HIGH_RISK`, `MEDIUM_RISK` và `LOW_RISK` là nhãn suy luận rủi ro, không phải kết luận xác nhận fraud.

## Chạy thủ công trong WSL (tuỳ chọn)

Chỉ dùng cách này nếu muốn xem trực tiếp Pig script mà không qua Docker. Xem hướng dẫn cài WSL tại [docs/SETUP_WSL.md](docs/SETUP_WSL.md).

Sau khi đã có Java 8+, Pig 0.17.0, DataFu 1.6.1 và Python 3:

```bash
pig -x local pig/03_real_data_risk.pig

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run web/app.py --server.address 0.0.0.0
```

Mở `http://localhost:8501`.

## Cấu trúc project

```text
.
├── data/raw/                 # đặt train_sample.csv ở đây (không commit)
├── pig/03_real_data_risk.pig # pipeline phân tích
├── scripts/run_pipeline.sh   # entry point cho Docker
├── web/app.py                # Streamlit dashboard
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── docs/SETUP_WSL.md
```

## Công nghệ

- Docker Compose
- Apache Pig 0.17.0
- Apache DataFu Pig 1.6.1
- Python, Streamlit, Pandas, Plotly
- WSL Ubuntu (chỉ là phương án chạy thủ công)
