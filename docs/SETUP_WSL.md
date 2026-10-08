# Cài WSL Ubuntu và lưu trên ổ D

Hướng dẫn này cài Ubuntu trên WSL 2 và chuyển filesystem của Ubuntu sang ổ D để tránh làm đầy ổ C.

## Yêu cầu

- Windows 10/11 hỗ trợ WSL 2.
- Ổ D còn đủ dung lượng.
- PowerShell mở bằng quyền **Run as Administrator**.

## 1. Cài WSL và Ubuntu

Mở PowerShell với quyền Administrator:

```powershell
wsl --install -d Ubuntu
```

Khởi động lại máy nếu Windows yêu cầu.

Kiểm tra trạng thái:

```powershell
wsl --status
wsl -l -v
```

Ubuntu phải hiển thị `VERSION` là `2`.

## 2. Khởi tạo Ubuntu

Mở ứng dụng **Ubuntu** từ Start Menu.

Lần đầu mở, Ubuntu sẽ yêu cầu tạo:

- Linux username
- Linux password

Kiểm tra môi trường:

```bash
whoami
pwd
java -version
python3 --version
git --version
```

## 3. Chuyển Ubuntu sang ổ D

Đóng mọi cửa sổ Ubuntu. Trong PowerShell, chạy:

```powershell
wsl --shutdown
New-Item -ItemType Directory -Force D:\WSL
wsl --manage Ubuntu --move D:\WSL\Ubuntu
```

Lệnh này chuyển toàn bộ distro Ubuntu, bao gồm source code, packages và filesystem Linux sang:

```text
D:\WSL\Ubuntu
```

Không tự di chuyển file WSL trong `AppData` bằng File Explorer.

Kiểm tra lại:

```powershell
wsl -l -v
wsl -d Ubuntu
```

Trong Ubuntu:

```bash
pwd
```

Kết quả mặc định:

```text
/home/<linux-username>
```

## 4. Cài công cụ cơ bản

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

## 5. Lỗi thường gặp

### `wsl: Failed to translate '...VS Code\bin'`

Đây thường là đường dẫn VS Code không còn tồn tại trong Windows `PATH`.

Lỗi này thường không ảnh hưởng đến việc chạy Ubuntu, Java, Pig hoặc Python. Có thể xử lý sau bằng cách xóa đường dẫn VS Code cũ trong Windows Environment Variables.

### WSL nằm ở ổ C

Kiểm tra lại lệnh chuyển distro:

```powershell
wsl --shutdown
wsl --manage Ubuntu --move D:\WSL\Ubuntu
```

### Docker Desktop bị dừng sau `wsl --shutdown`

Đây là hành vi bình thường. Mở lại Docker Desktop nếu cần dùng Docker.

## Tài liệu tham khảo

- [Microsoft WSL Installation](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Microsoft WSL FAQ](https://learn.microsoft.com/en-us/windows/wsl/faq)
