# Hướng dẫn chạy Phép nhân và Phép chia với Visualization

Tài liệu này hướng dẫn cách chạy các phép toán số nguyên lớn (Big Integer) bao gồm **Phép Nhân** và **Phép Chia** cùng với các hình ảnh hoạt họa minh họa từng bước của thuật toán.

---

## Yêu cầu hệ thống

- **Python 3.8+**
- **pip** (Python package manager)
- Các thư viện Python được liệt kê trong `requirements.txt`

---

## Cài đặt môi trường

### Bước 1: Cài đặt các thư viện phụ thuộc

Chuyển đến thư mục dự án:

```bash
cd /Users/thanhquach/Coding/Math-For-AI-BigInt
```

Cài đặt các thư viện cần thiết cho visualization (manimgl):

```bash
pip install -r divide/requirements.txt
```

Hoặc cài đặt từng thư viện:

```bash
pip install manimgl audioop-lts
```

---

## Phép Nhân (Karatsuba)

Phép nhân sử dụng **Thuật toán Karatsuba** - một thuật toán nhân hai số nguyên lớn hiệu quả hơn phép nhân thông thường.

### Cách 1: Chạy từ tệp input

Sử dụng tệp `multiply/input.txt` chứa các cặp số cần nhân:

```bash
cd multiply
python multiply.py < input.txt
```

**Định dạng input.txt:**
- Mỗi dòng có dạng: `<số_thứ_nhất> <số_thứ_hai>`
- Mỗi cặp số được tính trên cùng một dòng
- Các số có thể rất lớn (nhiều chữ số)

**Ví dụ nội dung input.txt:**
```
0 0
123 456
1000 1000
9999999999 8888888888
```

### Cách 2: Chạy với input từ bàn phím

```bash
cd multiply
python multiply.py
```

Nhập từng cặp số theo định dạng `<số_1> <số_2>`, nhấn Enter. Để kết thúc, nhấn Ctrl+D (trên Linux/Mac) hoặc Ctrl+Z (trên Windows).

### Output phép nhân

Chương trình sẽ in ra:
- Từng bước nhân chi tiết
- Các giá trị trung gian
- **Kết quả cuối cùng:** `<số_1> × <số_2> = <kết_quả>`

**Ví dụ output:**
```
123 × 456 = 56088
1000 × 1000 = 1000000
```

### Tạo Visualization cho Phép Nhân

Để tạo video hoạt họa minh họa phép nhân:

```bash
cd multiply
python -m manim -pql multiply_visualization.py
```

**Giải thích các tùy chọn:**
- `-p`: Mở video sau khi render hoàn tất
- `-q`: Chất lượng thấp (render nhanh hơn)
- `-l`: Độ phân giải low (480p)

**Để chỉnh các giá trị cho visualization:**

Mở file `multiply_visualization.py` và chỉnh sửa:
```python
U_VALUE = "1234"      # Số thứ nhất
V_VALUE = "5678"      # Số thứ hai
BASE = 10             # Cơ số (thường là 10)
TIME_SCALE = 1.55     # Tốc độ animation (cao hơn = chậm hơn)
```

Lưu file và chạy lại câu lệnh manim ở trên.

---

## Phép Chia (Thuật toán Knuth D)

Phép chia sử dụng **Thuật toán Knuth D** - một thuật toán chia số nguyên lớn hiệu quả được thiết kế bởi Donald Knuth.

### Cách 1: Chạy từ tệp input

Sử dụng tệp `divide/input.txt` chứa các cặp số cần chia:

```bash
cd divide
python divide.py < input.txt
```

**Định dạng input.txt:**
- Mỗi dòng có dạng: `<số_bị_chia> <số_chia>`
- Mỗi cặp số được tính trên cùng một dòng
- Các số có thể rất lớn (nhiều chữ số)

**Ví dụ nội dung input.txt:**
```
1234567890123456789012345678901234567890 1234567890123456789012345678901234567891
99999999999999999999999999999999999999999999 99999999999999999999999999999999999999999999
100000000000000000000000000000000000000000000 99999999999999999999999999999999999999999999
```

### Cách 2: Chạy với input từ bàn phím

```bash
cd divide
python divide.py
```

Nhập từng cặp số theo định dạng `<số_bị_chia> <số_chia>`, nhấn Enter. Để kết thúc, nhấn Ctrl+D (trên Linux/Mac) hoặc Ctrl+Z (trên Windows).

### Cách 3: Chạy với debug mode (xem chi tiết từng bước)

```bash
cd divide
python -c "from divide import knuth_algorithm_d, string_to_little_endian, little_endian_to_string; u = string_to_little_endian('522971'); v = string_to_little_endian('398'); q, r = knuth_algorithm_d(u, v, debug=True); print(f'Thương: {little_endian_to_string(q)}, Dư: {little_endian_to_string(r)}')"
```

### Output phép chia

Chương trình sẽ in ra:
- Từng bước chia chi tiết
- Các giá trị trung gian
- **Kết quả cuối cùng:** `<số_bị_chia> ÷ <số_chia> = <thương> ... <dư>`

**Ví dụ output:**
```
522971 ÷ 398 = 1313 ... 197
```

### Tạo Visualization cho Phép Chia

Để tạo video hoạt họa minh họa phép chia:

```bash
cd divide
python -m manim -pql divide_visualization.py
```

**Giải thích các tùy chọn:**
- `-p`: Mở video sau khi render hoàn tất
- `-q`: Chất lượng thấp (render nhanh hơn)
- `-l`: Độ phân giải low (480p)

**Để chỉnh các giá trị cho visualization:**

Mở file `divide_visualization.py` và chỉnh sửa:
```python
U_VALUE = '522971'    # Số bị chia
V_VALUE = '398'       # Số chia
BASE_VALUE = 10       # Cơ số (thường là 10)
WAIT_SCALE = 1.1      # Tốc độ animation (cao hơn = chậm hơn)
```

Lưu file và chạy lại câu lệnh manim ở trên.

---

## Các tùy chọn Manim Khác

| Tùy chọn       | Mô tả                                    |
| -------------- | ---------------------------------------- |
| `-p`           | Mở video sau khi render                  |
| `-q`           | Chất lượng thấp (480p, render nhanh)     |
| `-m`           | Chất lượng trung bình (720p)             |
| `-h`           | Chất lượng cao (1080p, render lâu)       |
| `-l`           | Độ phân giải thấp (preview only)         |
| `-s`           | Lưu hình ảnh tĩnh (không tạo video)      |
| `--resolution` | Tùy chỉnh độ phân giải (vd: `1920,1080`) |

**Ví dụ:**
```bash
python -m manim -pml multiply_visualization.py    # Chất lượng trung bình, mở video
python -m manim -s divide_visualization.py         # Chỉ lưu hình ảnh
```

---

## Cấu trúc thư mục

```
Math-For-AI-BigInt/
├── README_DETAIL.md                
├── multiply/
│   ├── multiply.py               # Thuật toán Karatsuba
│   ├── multiply_visualization.py # Hoạt họa phép nhân
│   ├── input.txt                 # Các bộ test case
│   └── README.md                 # Giải thích thuật toán
├── divide/
│   ├── divide.py                 # Thuật toán Knuth D
│   ├── divide_visualization.py   # Hoạt họa phép chia
│   ├── input.txt                 # Các bộ test case
│   ├── requirements.txt           # Danh sách thư viện
│   ├── README.md                 # Giải thích thuật toán
│   ├── README_MATH.md            # Chi tiết toán học
│   └── README_EXAMPLE.md         # Ví dụ minh họa
```

---

## Ví dụ thực hành

### Ví dụ 1: Nhân hai số nhỏ
```bash
cd multiply
echo "123 456" | python multiply.py
```

### Ví dụ 2: Chia với visualization
```bash
cd divide
# Chỉnh sửa divide_visualization.py
# U_VALUE = '1234567'
# V_VALUE = '789'
python -m manim -pql divide_visualization.py
```

### Ví dụ 3: Nhân hai số rất lớn
```bash
cd multiply
cat > large_input.txt << EOF
123456789012345678901234567890 987654321098765432109876543210
999999999999999999999999999999 111111111111111111111111111111
EOF
python multiply.py < large_input.txt
```

---

## Tài liệu thêm

- **multiply/README.md** - Giải thích thuật toán Karatsuba
- **divide/README.md** - Giải thích thuật toán Knuth D
- **divide/README_MATH.md** - Chi tiết toán học về Knuth D
- **divide/README_EXAMPLE.md** - Ví dụ minh họa phép chia

---

## Ghi chú

- Cả hai thuật toán hoạt động với số nguyên không âm
- Cơ số mặc định là 10 (hệ thập phân)
- Có thể mở rộng để hỗ trợ các cơ số khác
- Visualization sử dụng thư viện Manim (Mathematical Animation Engine)

---