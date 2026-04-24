# Math-For-AI-BigInt

Dự án này triển khai các thuật toán toán học hiệu quả để tính toán trên số nguyên lớn (Big Integer), bao gồm **Phép Nhân (Karatsuba)** và **Phép Chia (Knuth Algorithm D)** với các hoạt họa minh họa từng bước.

## Hướng dẫn nhanh

👉 **[Xem README_DETAIL.md để chạy phép nhân, chia và visualization](README_DETAIL.md)**

### Các lệnh cơ bản

**Chạy phép nhân:**
```bash
cd multiply
python multiply.py < input.txt
```

**Chạy phép chia:**
```bash
cd divide
python divide.py < input.txt
```

**Tạo video visualization:**
```bash
cd multiply
python -m manim -pql multiply_visualization.py
```

## Cấu trúc dự án

- **multiply/** - Thuật toán Karatsuba cho phép nhân
- **divide/** - Thuật toán Knuth D cho phép chia
- **README_DETAIL.md** - Hướng dẫn chi tiết cách sử dụng
