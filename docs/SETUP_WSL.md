# Cài WSL Ubuntu và lưu trên ổ D

Tài liệu này dành cho người muốn chạy Apache Pig thủ công trong Linux. Với nhu cầu demo/nộp bài, hãy ưu tiên chạy Docker theo [README](../README.md): đơn giản hơn và không cần cài các công cụ bên dưới.

## 1. Cài WSL 2 và Ubuntu

Mở PowerShell bằng quyền Administrator:

```powershell
wsl --install -d Ubuntu
```

Khởi động lại nếu Windows yêu cầu. Sau đó mở Ubuntu từ Start Menu để đặt Linux username và password.

Kiểm tra WSL 2:

```powershell
wsl -l -v
```

Ubuntu cần hiện `VERSION` là `2`.

## 2. Chuyển Ubuntu sang ổ D

Đóng tất cả cửa sổ Ubuntu, rồi chạy PowerShell Administrator:

```powershell
wsl --shutdown
New-Item -ItemType Directory -Force D:\WSL
wsl --manage Ubuntu --move D:\WSL\Ubuntu
```

Lệnh này chuyển toàn bộ filesystem Ubuntu — bao gồm source, packages và môi trường Python — sang ổ D. Không kéo/thả hay di chuyển thủ công các file WSL trong `AppData`.

## 3. Cài công cụ chạy thủ công

Trong Ubuntu:

```bash
sudo apt update
sudo apt install -y openjdk-8-jdk python3 python3-pip python3-venv git wget curl unzip
```

Kiểm tra:

```bash
java -version
python3 --version
git --version
```

Sau đó cài Apache Pig 0.17.0 và DataFu 1.6.1 theo phần chạy thủ công trong README.

## Lỗi thường gặp

### `wsl: Failed to translate '...VS Code\\bin'`

Đây thường là đường dẫn VS Code cũ trong Windows `PATH`. Nó thường không ảnh hưởng tới Java, Pig hay Python trong Ubuntu. Có thể xoá đường dẫn cũ trong Windows Environment Variables khi thuận tiện.

### Docker Desktop dừng sau `wsl --shutdown`

Đây là bình thường vì Docker Desktop sử dụng WSL 2. Khởi động lại Docker Desktop hoặc chạy `docker desktop start` trong PowerShell trước khi dùng Docker.

### Muốn chạy Docker trong Ubuntu

Không bắt buộc. Có thể chạy `docker compose` từ PowerShell trong folder project trên Windows. Docker Desktop sẽ dùng engine Linux của nó.

## Tham khảo

- [Microsoft WSL Installation](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Microsoft WSL FAQ](https://learn.microsoft.com/en-us/windows/wsl/faq)
