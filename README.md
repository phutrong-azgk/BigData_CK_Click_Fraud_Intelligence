# Click Fraud Intelligence

Hệ thống phân tích rủi ro click fraud cho quảng cáo di động, sử dụng Apache Pig, Apache DataFu và Streamlit.

## Mục tiêu

- Xử lý log click quảng cáo quy mô lớn bằng Apache Pig.
- Trích xuất đặc trưng hành vi theo IP.
- Chấm điểm rủi ro dựa trên click volume, conversion và mức độ lặp lại app/channel.
- Hiển thị kết quả qua dashboard Streamlit.

## Công nghệ

- Apache Pig 0.17.0
- Apache DataFu Pig 1.6.1
- Python
- Streamlit
- Pandas
- Plotly
- WSL Ubuntu

## Dataset

Dự án sử dụng `train_sample.csv` từ [TalkingData AdTracking Fraud Detection Challenge](https://www.kaggle.com/competitions/talkingdata-adtracking-fraud-detection/data).

Dataset gồm 100.000 log click đã được ẩn danh:

```text
ip, app, device, os, channel, click_time, attributed_time, is_attributed
```

`is_attributed` biểu thị click có dẫn đến cài đặt ứng dụng hay không. Đây không phải nhãn fraud trực tiếp.

Raw dataset không được đưa vào repository. Sau khi tải từ Kaggle, đặt file tại:

```text
data/raw/train_sample.csv
```

## Cấu trúc project

```text
click-fraud/
├── data/
│   └── raw/
│       └── train_sample.csv
├── lib/
│   └── datafu-pig-1.6.1.jar
├── pig/
│   └── 03_real_data_risk.pig
├── output/
│   ├── real_ip_risk/
│   └── hourly_stats/
├── web/
│   └── app.py
├── requirements.txt
└── README.md
```

## Chuẩn bị

Cần có Java 8+, Apache Pig 0.17.0 và Python 3.

Tải DataFu Pig JAR:

```bash
mkdir -p lib

wget -O lib/datafu-pig-1.6.1.jar \
  https://repo.maven.apache.org/maven2/org/apache/datafu/datafu-pig/1.6.1/datafu-pig-1.6.1.jar
```

## Chạy pipeline Pig

Nếu đã chạy pipeline trước đó, xóa output sinh ra để Pig có thể tạo lại:

```bash
rm -rf output/real_ip_risk output/hourly_stats
```

Chạy pipeline:

```bash
pig -x local pig/03_real_data_risk.pig
```

Pipeline tạo hai output:

```text
output/real_ip_risk/part-r-00000
output/hourly_stats/part-r-00000
```

## Risk scoring

Mỗi IP được chấm điểm từ 0 đến 100.

| Điều kiện | Điểm |
|---|---:|
| Ít nhất 30 clicks | 50 |
| Từ 10 đến 29 clicks | 30 |
| Không có conversion và có ít nhất 5 clicks | 25 |
| Tối đa 2 app và có ít nhất 5 clicks | 15 |
| Tối đa 2 channel và có ít nhất 5 clicks | 10 |

Phân loại:

| Điểm | Nhãn |
|---|---|
| 70–100 | `HIGH_RISK` |
| 40–69 | `MEDIUM_RISK` |
| 0–39 | `LOW_RISK` |

## Chạy web dashboard

Tạo môi trường Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chạy Streamlit:

```bash
streamlit run web/app.py --server.address 0.0.0.0
```

Mở trình duyệt tại:

```text
http://localhost:8501
```

## Dashboard

Dashboard cung cấp:

- Tổng số clicks và IP.
- Số IP high-risk và medium-risk.
- Click volume theo giờ.
- Phân bố risk score.
- Biểu đồ click volume so với conversion rate.
- Top IP cần điều tra.
- Bảng filter kết quả theo nhãn và risk score.

## Lưu ý

`HIGH_RISK`, `MEDIUM_RISK` và `LOW_RISK` là suy luận rủi ro dựa trên hành vi, không phải nhãn fraud đã được xác nhận.
