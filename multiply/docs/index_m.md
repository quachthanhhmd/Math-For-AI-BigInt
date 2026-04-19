## Giải thích thành phần $z_1$ trong Karatsuba

### Bối cảnh

Sau khi tách hai số thành hai nửa, ta viết:

$$
U = U_1 B^m + U_0,
\qquad
V = V_1 B^m + V_0
$$

Khai triển tích:

$$
U \cdot V = (U_1 B^m + U_0)(V_1 B^m + V_0)
$$

$$
= U_1V_1 B^{2m} + (U_1V_0 + U_0V_1)B^m + U_0V_0
$$

Nếu làm trực tiếp, ta phải tính đủ 4 tích con:

- $U_0V_0$
- $U_1V_1$
- $U_1V_0$
- $U_0V_1$

Karatsuba muốn bỏ bớt 1 phép nhân lớn, nên nó nhắm vào phần giữa:

$$
U_1V_0 + U_0V_1
$$

---

### Mẹo đại số cốt lõi

Xét biểu thức:

$$
(U_0 + U_1)(V_0 + V_1)
$$

Khai triển ra:

$$
(U_0 + U_1)(V_0 + V_1) = U_0V_0 + U_0V_1 + U_1V_0 + U_1V_1
$$

Đặt:

$$
z_0 = U_0V_0,
\qquad
z_2 = U_1V_1
$$

Khi đó:

$$
(U_0 + U_1)(V_0 + V_1) = z_0 + z_2 + U_1V_0 + U_0V_1
$$

Suy ra phần giữa chính là:

$$
U_1V_0 + U_0V_1 = (U_0 + U_1)(V_0 + V_1) - z_0 - z_2
$$

Vì vậy Karatsuba định nghĩa:

$$
z_1 = (U_0 + U_1)(V_0 + V_1) - z_0 - z_2
$$

và ghép kết quả cuối cùng bằng:

$$
U \cdot V = z_2 B^{2m} + z_1 B^m + z_0
$$

---

### Tại sao bước này đáng giá?

Nếu không dùng mẹo trên, số phép nhân lớn là 4.

Nếu dùng Karatsuba:

- 1 phép nhân để tính $z_0$
- 1 phép nhân để tính $z_2$
- 1 phép nhân để tính $(U_0+U_1)(V_0+V_1)$

Tổng cộng chỉ còn **3 phép nhân lớn**.

Đổi lại, ta phải làm thêm vài phép cộng và trừ, nhưng những phép này rẻ hơn rất nhiều so với phép nhân trên số nguyên lớn.

---

## Trường hợp 1: Ví dụ cơ bản

Tính:

$$
1234 \times 5678
$$

Chọn $m = 2$:

$$
1234 = 12 \cdot 10^2 + 34
$$

$$
5678 = 56 \cdot 10^2 + 78
$$

Suy ra:

- $U_1 = 12$, $U_0 = 34$
- $V_1 = 56$, $V_0 = 78$

Tính hai biên:

$$
z_0 = 34 \times 78 = 2652
$$

$$
z_2 = 12 \times 56 = 672
$$

Tính phần giữa bằng mẹo Karatsuba:

$$
z_1 = (34 + 12)(78 + 56) - 2652 - 672
$$

$$
z_1 = 46 \times 134 - 3324 = 6164 - 3324 = 2840
$$

Ghép lại:

$$
1234 \times 5678 = 672 \cdot 10^4 + 2840 \cdot 10^2 + 2652 = 7006652
$$

Ở đây, $z_1 = 2840$ chính là phần đại diện cho:

$$
U_1V_0 + U_0V_1 = 12 \times 78 + 34 \times 56 = 936 + 1904 = 2840
$$

---

## Trường hợp 2: Tổng hai nửa bị carry

Tính:

$$
9999 \times 9999
$$

Chọn $m = 2$:

$$
9999 = 99 \cdot 10^2 + 99
$$

$$
9999 = 99 \cdot 10^2 + 99
$$

Khi đó:

$$
z_0 = 99 \times 99 = 9801
$$

$$
z_2 = 99 \times 99 = 9801
$$

Tổng hai nửa là:

$$
U_0 + U_1 = 99 + 99 = 198
$$

$$
V_0 + V_1 = 99 + 99 = 198
$$

Đây là điểm quan trọng: tổng này **dài hơn từng nửa ban đầu**. Nhưng thuật toán vẫn hoạt động bình thường vì:

- `add_le` xử lý carry đầy đủ
- lời gọi đệ quy cho $z_1$ không yêu cầu đầu vào phải có cùng số chữ số như trước
- code sẽ tiếp tục padding nếu cần

Tính:

$$
z_1 = 198 \times 198 - 9801 - 9801
$$

$$
z_1 = 39204 - 19602 = 19602
$$

Phần giữa vẫn được tính chính xác dù tổng bị "tràn" sang thêm một chữ số.

---

## Trường hợp 3: Hai số có độ dài lệch nhau

Tính:

$$
12345 \times 67
$$

Trong code, hai số sẽ được padding để có cùng độ dài trước khi tách.

Ta có thể nhìn bài toán dưới dạng:

$$
12345 = 123 \cdot 10^2 + 45
$$

$$
67 = 0 \cdot 10^2 + 67
$$

Tức là:

- $U_1 = 123$, $U_0 = 45$
- $V_1 = 0$, $V_0 = 67$

Khi đó:

$$
z_0 = 45 \times 67 = 3015
$$

$$
z_2 = 123 \times 0 = 0
$$

$$
z_1 = (45 + 123)(67 + 0) - 3015 - 0
$$

$$
z_1 = 168 \times 67 - 3015 = 11256 - 3015 = 8241
$$

Ghép lại:

$$
12345 \times 67 = 0 \cdot 10^4 + 8241 \cdot 10^2 + 3015
$$

$$
= 824100 + 3015 = 827115
$$

Điểm cần nhớ là padding bằng 0 **không làm thay đổi giá trị toán học**, nó chỉ giúp việc chia đôi hai số trở nên nhất quán.

---

## Kết luận

$z_1$ là trái tim của Karatsuba.

Nó không phải là một tích biên như $z_0$ hay $z_2$, mà là cách mã hóa phần giao nhau:

$$
U_1V_0 + U_0V_1
$$

bằng một phép nhân mới:

$$
(U_0 + U_1)(V_0 + V_1)
$$

rồi trừ ngược hai phần đã biết.

Nhờ đó, Karatsuba đổi bài toán:

- từ **4 phép nhân lớn**
- thành **3 phép nhân lớn + vài phép cộng/trừ**

và đây chính là lý do nó nhanh hơn schoolbook multiplication khi kích thước số đủ lớn.
