# LevelDB Viewer

Một công cụ trực quan để xem và duyệt dữ liệu trong các database **LevelDB**.

> Also i have [English](./README_EN.md) version of this README. Translated by Claude on Github Copilot
## LevelDB là gì và thường có mặt ở đâu?

[LevelDB](https://github.com/google/leveldb) là thư viện lưu trữ Key-Value (khóa-giá trị) tốc độ cực nhanh do Google phát triển, lưu trữ dữ liệu dưới dạng các bytes. Nó sử dụng cấu trúc Log-Structured Merge-tree (LSM) nên tốc độ ghi cũng như đọc đều rất tối ưu, không yêu cầu thiết lập client-server cồng kềnh.

Bạn sẽ thường xuyên bắt gặp LevelDB ẩn mình bên trong các thư mục dữ liệu cục bộ của máy tính:
- **Trình duyệt (Browser):** Google Chrome, Microsoft Edge, Brave, v.v. (thư mục Local Storage hoặc IndexedDB).
- **Ứng dụng Desktop Electron:** Slack, Discord, v.v.
- **Blockchain:** Được sử dụng làm cơ sở dữ liệu nội bộ ở trong các node (ví dụ: Geth của Ethereum).
- **Game:** Minecraft (Bedrock Edition) sử dụng công nghệ tương tự LevelDB để lưu trữ chunk dữ liệu thế giới.

## Câu chuyện ra đời

*Tìm mỏi mắt không thấy cái viewer nào. Thôi thì lại "LÀO GÌ CŨNG TÔN !"*

Vì không tìm được một công cụ Viewer nào thực sự ngon, đủ đơn giản nhưng mạnh mẽ để xem mã HEX, văn bản và giải mã các Key-Value từ LevelDB trên Windows, dự án này đã ra đời. Mục tiêu là biến một tác vụ vốn phải dò dẫm dòng lệnh thành một giao diện GUI thân thiện nhưng hiệu năng cao.

## Install/Download

1. **Vào Release download bản mới nhất được build tự động tại [Latest Release Page](//github.com/tansautn/leveldb-viewer/releases/latest)**
2. **Chọn phiên bản phù hợp hệ điều hành, load về (Hỗ trợ: Windows, MacOS, Linux)**
3. **Giải nén, bung package (nếu cần); Tìm file thực thi rồi View thôi**

## Changelog

- Khả năng chỉ có 1 phiên bản thôi. Changelog làm đếch gì

## Công nghệ sử dụng
- Python 3.12+
- PySide6 (GUI framework)
- leveldb-py (Giao tiếp database)

## Hướng dẫn Build

Dự án này sử dụng [uv](https://github.com/astral-sh/uv) để quản lý package siêu tốc và [Nuitka](https://nuitka.net/) để biên dịch ra executable.

### 1. Trên Windows (Sử dụng script có sẵn)

Chạy file script để lấy bản build:
```cmd
build.cmd
```
Script này sẽ tự động: xóa cache, thiết lập `.venv` với Python 3.12, cài dependencies và compile ra `.exe` vào thư mục `dist/`.

### 2. Trên hệ điều hành khác hoặc chạy thủ công

```bash
# 1. Tạo venv bẳng uv
uv venv --python 3.12 --managed-python

# 2. Kích hoạt venv
# Windows:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# 3. Cài đặt thư viện
uv pip install zstandard pyside6 leveldb-py nuitka imageio

# 4. Chạy trực tiếp (Dev)
python src/leveldb-viewer.py

# 5. Build executable bằng Nuitka (Tham khảo build.cmd hoặc .github/workflows/release.yml)
```
