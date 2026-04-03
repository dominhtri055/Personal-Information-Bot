# People Info Bot

A Flask web application that searches for public professional information about a person using SerpApi.

---

## English

### 1. Overview

People Info Bot is a Flask web application that searches for **public professional information** about a person using **SerpApi**.

The app can display:

- Name
- Role / title
- Degree
- Current affiliation
- Public email
- LinkedIn profile
- Profile image
- Source links

This project is designed for searching public-facing profiles such as:

- professors
- researchers
- academic staff
- public professionals

---

### 2. Features

- Search by full name
- Optional hint such as school, city, or company
- Search public results using SerpApi
- Try to extract:
  - role
  - degree
  - affiliation
  - email
  - LinkedIn
- Show a profile image if available
- Show source links
- Simple Flask web interface

---

### 3. Project Structure

```text
BOT/
│
├── app.py
├── Bot.py
├── .env
├── requirements.txt
└── templates/
    └── index.html
```

File descriptions:

- `app.py`: runs the Flask web app
- `Bot.py`: main search and extraction logic
- `.env`: stores your API key
- `requirements.txt`: Python dependencies
- `templates/index.html`: frontend HTML page

---

### 4. How It Works

The bot works in these steps:

1. The user enters a name.
2. The user can optionally enter a hint.
3. The bot sends search queries through SerpApi.
4. It collects public web results.
5. It ranks likely official pages higher.
6. It visits public pages and extracts text.
7. It tries to find:
   - role
   - degree
   - affiliation
   - public email
8. It checks whether a public LinkedIn result appears.
9. It tries to get an image.
10. It displays the result on the web page.

---

### 5. Requirements

Before running the project, make sure you have:

- Python 3.10 or newer
- pip installed
- A SerpApi account
- A valid `SERPAPI_KEY`

---

### 6. Installation

Open a terminal in your project folder:
```bash
cd <Current folder>
```

Install the required packages:

```bash
pip install flask requests beautifulsoup4 python-dotenv
```

You can also create a `requirements.txt` file:

```txt
flask
requests
beautifulsoup4
python-dotenv
```

Then install with:

```bash
pip install -r requirements.txt
```

---

### 7. Environment Setup

Create a file named `.env` in the root folder:

```env
SERPAPI_KEY=your_real_serpapi_key_here
```

Important notes:

- The `.env` file must be in the same folder as `app.py`
- The `.env` file must be in the same folder as `Bot.py`

---

### 8. Running the Project

Start the Flask app:

```bash
python app.py
```

Then open this address in your browser:

```text
http://127.0.0.1:5000
```

---

### 9. Example Usage

Examples:

- `Miroslav Krstić` with hint `UC San Diego`
- `Zhong-Ping Jiang` with hint `NYU`
- `Wassim M. Haddad` with hint `Georgia Tech`

---

### 10. Main Files

#### `app.py`

This file runs the Flask website and handles the search form.

Example:

```python
from flask import Flask, render_template, request
from people_info_bot import search_person

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        hint = request.form.get("hint", "").strip()

        if not name:
            error = "Please enter a name."
        else:
            try:
                result = search_person(name, hint)
            except Exception as e:
                error = str(e)

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
```

#### `Bot.py`

This file handles:

- Google search through SerpApi
- image search through SerpApi
- page fetching
- HTML parsing
- email extraction
- role extraction
- degree extraction
- affiliation extraction
- LinkedIn detection

#### `templates/index.html`

This file contains the web interface:

- search form
- result display
- image section
- source links
- notes section

---

### 11. Troubleshooting

#### Error: `Thiếu SERPAPI_KEY trong file .env`

Cause:
- The `.env` file is missing
- The `.env` file is in the wrong folder
- The API key is empty or invalid

Fix:

```env
SERPAPI_KEY=your_real_serpapi_key_here
```

Make sure `.env` is in the project root folder.

#### Error: `TemplateNotFound: index.html`

Cause:
- Flask cannot find the HTML template

Fix:
Make sure the file is here:

```text
templates/index.html
```

Not here:

- `template/index.html`
- `index.html` in the root folder

#### No results found

Possible reasons:

- the name is too common
- the hint is missing
- the person has limited public information
- the API key is invalid
- the search result is ambiguous

Try adding a better hint, such as:

- school
- company
- city
- department

Example:

```text
Name: Yuxin Chen
Hint: University of Chicago
```

#### Wrong image

Sometimes image search may return a similar person with the same name.

To improve accuracy, add a better hint such as:

- school
- company
- city
- department

---

### 12. Safety and Intended Use

This project is intended for finding **public professional information only**.

Do not use it to collect:

- private information
- hidden contact details
- sensitive personal data

Appropriate use cases:

- academic lookup
- faculty research
- public professional profiles

---

### 13. Future Improvements

Possible future improvements:

- export to JSON
- export to Excel
- batch search
- better confidence scoring
- duplicate filtering
- improved image ranking
- deployment to cloud
- better UI design

---

### 14. Quick Start

```bash
cd <your current folder path>
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

### 15. Summary

This project uses Flask + SerpApi to search public web data about a person and display structured results in a simple website.

---

## Tiếng Việt

### 1. Tổng quan

People Info Bot là một ứng dụng web viết bằng **Flask** dùng **SerpApi** để tìm **thông tin nghề nghiệp công khai** của một người.

Ứng dụng có thể hiển thị:

- Tên
- Vai trò / chức danh
- Học vị
- Nơi công tác hiện tại
- Email công khai
- LinkedIn
- Ảnh đại diện
- Các nguồn tham khảo

Project này phù hợp để tìm các hồ sơ công khai như:

- giáo sư
- nhà nghiên cứu
- nhân sự học thuật
- người làm việc chuyên nghiệp có hồ sơ công khai

---

### 2. Chức năng

- Tìm theo họ tên đầy đủ
- Có thể nhập thêm gợi ý như trường, thành phố hoặc công ty
- Tìm kết quả công khai bằng SerpApi
- Cố gắng trích xuất:
  - chức danh
  - học vị
  - nơi công tác
  - email
  - LinkedIn
- Hiển thị ảnh nếu có
- Hiển thị nguồn tham khảo
- Giao diện web đơn giản bằng Flask

---

### 3. Cấu trúc thư mục

```text
Bot/
│
├── app.py
├── Bot.py
├── .env
├── requirements.txt
└── templates/
    └── index.html
```

Mô tả file:

- `app.py`: chạy website Flask
- `Bot.py`: chứa logic tìm kiếm và trích xuất chính
- `.env`: lưu API key
- `requirements.txt`: danh sách thư viện Python
- `templates/index.html`: file giao diện HTML

---

### 4. Bot hoạt động như thế nào

Bot hoạt động theo các bước sau:

1. Người dùng nhập tên.
2. Người dùng có thể nhập thêm gợi ý.
3. Bot gửi truy vấn tìm kiếm qua SerpApi.
4. Bot thu thập các kết quả công khai trên web.
5. Bot ưu tiên các trang có vẻ là nguồn chính thức.
6. Bot truy cập các trang công khai và lấy nội dung văn bản.
7. Bot cố gắng tìm:
   - chức danh
   - học vị
   - nơi công tác
   - email công khai
8. Bot kiểm tra xem có LinkedIn công khai hay không.
9. Bot cố gắng lấy ảnh.
10. Bot hiển thị kết quả trên website.

---

### 5. Yêu cầu

Trước khi chạy project, bạn cần có:

- Python 3.10 trở lên
- pip
- Tài khoản SerpApi
- `SERPAPI_KEY` hợp lệ

---

### 6. Cài đặt

Mở terminal tại thư mục project:

```bash
cd <Nơi lưu file>
```

Cài các thư viện cần thiết:

```bash
pip install flask requests beautifulsoup4 python-dotenv
```

Bạn cũng có thể tạo file `requirements.txt`:

```txt
flask
requests
beautifulsoup4
python-dotenv
```

Sau đó cài bằng:

```bash
pip install -r requirements.txt
```

---

### 7. Thiết lập biến môi trường

Tạo file `.env` trong thư mục gốc:

```env
SERPAPI_KEY=your_real_serpapi_key_here
```

Lưu ý quan trọng:

- File `.env` phải nằm cùng thư mục với `app.py`
- File `.env` phải nằm cùng thư mục với `Bot.py`

---

### 8. Chạy project

Chạy ứng dụng Flask:

```bash
python app.py
```

Sau đó mở trình duyệt tại địa chỉ:

```text
http://127.0.0.1:5000
```

---

### 9. Ví dụ sử dụng

Ví dụ tìm kiếm:

- `Miroslav Krstić` với gợi ý `UC San Diego`
- `Zhong-Ping Jiang` với gợi ý `NYU`
- `Wassim M. Haddad` với gợi ý `Georgia Tech`

---

### 10. Các file chính

#### `app.py`

File này chạy website Flask và xử lý form tìm kiếm.

Ví dụ:

```python
from flask import Flask, render_template, request
from people_info_bot import search_person

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        hint = request.form.get("hint", "").strip()

        if not name:
            error = "Please enter a name."
        else:
            try:
                result = search_person(name, hint)
            except Exception as e:
                error = str(e)

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
```

#### `Bot.py`

File này xử lý:

- tìm kiếm Google qua SerpApi
- tìm ảnh qua SerpApi
- tải nội dung trang
- phân tích HTML
- trích xuất email
- trích xuất chức danh
- trích xuất học vị
- trích xuất nơi công tác
- nhận diện LinkedIn

#### `templates/index.html`

File này chứa giao diện web:

- form tìm kiếm
- phần hiển thị kết quả
- phần ảnh
- phần nguồn tham khảo
- phần ghi chú

---

### 11. Lỗi thường gặp

#### Lỗi: `Thiếu SERPAPI_KEY trong file .env`

Nguyên nhân:

- thiếu file `.env`
- file `.env` nằm sai chỗ
- API key bị trống hoặc không hợp lệ

Cách sửa:

```env
SERPAPI_KEY=your_real_serpapi_key_here
```

Đảm bảo file `.env` nằm trong thư mục gốc của project.

#### Lỗi: `TemplateNotFound: index.html`

Nguyên nhân:

- Flask không tìm thấy file giao diện HTML

Cách sửa:
Đảm bảo file nằm đúng ở đây:

```text
templates/index.html
```

Không phải ở đây:

- `template/index.html`
- `index.html` nằm ngoài thư mục gốc

#### Không có kết quả

Các nguyên nhân có thể:

- tên quá phổ biến
- thiếu gợi ý
- người đó có ít thông tin công khai
- API key không đúng
- kết quả tìm kiếm bị mơ hồ

Hãy thử thêm gợi ý tốt hơn như:

- tên trường
- tên công ty
- thành phố
- khoa / bộ môn

Ví dụ:

```text
Name: Yuxin Chen
Hint: University of Chicago
```

#### Ảnh sai người

Đôi khi phần tìm ảnh có thể trả về ảnh của người khác trùng tên.

Để tăng độ chính xác, hãy nhập thêm gợi ý như:

- trường
- công ty
- thành phố
- khoa / bộ môn

---

### 12. Mục đích sử dụng và lưu ý

Project này chỉ nên dùng để tìm **thông tin nghề nghiệp công khai**.

Không nên dùng để thu thập:

- thông tin riêng tư
- thông tin liên hệ bị ẩn
- dữ liệu cá nhân nhạy cảm

Các mục đích phù hợp:

- tra cứu học thuật
- tìm giáo sư / giảng viên
- tìm hồ sơ nghề nghiệp công khai

---

### 13. Hướng phát triển

Các hướng nâng cấp có thể làm tiếp:

- xuất JSON
- xuất Excel
- tìm nhiều người cùng lúc
- chấm điểm độ tin cậy
- lọc trùng
- xếp hạng ảnh tốt hơn
- deploy lên cloud
- cải thiện giao diện

---

### 14. Chạy nhanh

```bash
cd <Foler lưu project>
pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại:

```text
http://127.0.0.1:5000
```

---

### 15. Tóm tắt

Project này dùng Flask + SerpApi để tìm dữ liệu công khai trên web về một người và hiển thị kết quả có cấu trúc trên website đơn giản.
