## Giải thích tham số $d$ (Scaling Factor)

### Bối cảnh

Giả sử chúng ta đang làm việc ở **hệ thập phân**, tức là $B = 10$.

Điều kiện chuẩn hóa: Chữ số dẫn đầu của số chia sau khi nhân với $d$ phải thỏa:

$$
v'_{n-1} = d \cdot v_{n-1} \ge \left\lfloor \frac{B}{2} \right\rfloor = 5
$$

---

### Trường hợp 1: Chia cho 45

**Đầu vào:**
- Số chia: $V = 45$
- Chữ số dẫn đầu: $v_{n-1} = 4$

**Tính $d$:**

$$
d = \left\lfloor \frac{10}{4 + 1} \right\rfloor = \left\lfloor \frac{10}{5} \right\rfloor = 2
$$

**Kiểm chứng:**

$$
V' = 45 \times 2 = 90
$$

Chữ số dẫn đầu mới: $9 \ge 5$ (Thoả)

---

### Trường hợp 2: Chia cho 182

**Đầu vào:**
- Số chia: $V = 182$
- Chữ số dẫn đầu: $v_{n-1} = 1$

**Tính $d$:**

$$
d = \left\lfloor \frac{10}{1 + 1} \right\rfloor = \left\lfloor \frac{10}{2} \right\rfloor = 5
$$

**Kiểm chứng:**

$$
V' = 182 \times 5 = 910
$$

Chữ số dẫn đầu mới: $9 \ge 5$ (Thoả)

---

### Trường hợp 3: Chia cho 735

**Đầu vào:**
- Số chia: $V = 735$
- Chữ số dẫn đầu: $v_{n-1} = 7$

**Tính $d$:**

$$
d = \left\lfloor \frac{10}{7 + 1} \right\rfloor = \left\lfloor \frac{10}{8} \right\rfloor = 1
$$

**Kiểm chứng:**

$$
V' = 735 \times 1 = 735
$$

Chữ số dẫn đầu: $7$ đã $\ge 5$ ✓ (Thoả)