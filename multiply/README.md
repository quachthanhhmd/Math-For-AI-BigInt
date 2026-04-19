## Giải thích thuật toán nhân số nguyên lớn bằng Karatsuba

### Khởi tạo

Giả sử ta cần tính tích của hai số nguyên lớn:

$$
U \times V
$$

Trong cơ số $B$, ta biểu diễn:

$$
U = (u_{n-1}, u_{n-2}, \dots, u_1, u_0)_B,
\qquad
V = (v_{m-1}, v_{m-2}, \dots, v_1, v_0)_B
$$

Trong file `multiply.py`, chương trình đang dùng:

- **Cơ số $B = 10$**
- **Mảng little-endian** để lưu chữ số, tức là chữ số hàng đơn vị đứng trước.

Ví dụ:

- `1234` được lưu thành `[4, 3, 2, 1]`
- `5678` được lưu thành `[8, 7, 6, 5]`

### Tại sao lại dùng little-endian?

Không phải vì toán học bắt buộc như vậy, mà vì đây là cách biểu diễn rất thuận lợi cho máy tính:

- Phép cộng/trừ bắt đầu từ chữ số thấp nhất.
- Carry và borrow lan dần sang trái, nên việc duyệt từ index nhỏ đến lớn sẽ tự nhiên hơn.
- Khi cần dịch trái theo cơ số $B$, ta chỉ cần chèn thêm số `0` vào đầu mảng.

Ví dụ:

- `1234` lưu thành `[4,3,2,1]`
- Nhân với $10^2$ tương đương `123400`
- Trong little-endian, chỉ cần thêm 2 số 0 ở đầu: `[0,0,4,3,2,1]`

### Cách chọn cơ số Base

Ở đây mã nguồn đang chọn $B = 10$ để dễ kiểm tra bằng mắt và thuận tiện cho việc học thuật toán.

Trong các thư viện BigInt thực tế, người ta thường chọn:

- $B = 2^{32}$ trên hệ 32-bit
- $B = 2^{64}$ trên hệ 64-bit

Lý do là vì:

- Tận dụng đúng kích thước thanh ghi CPU.
- Các phép chia/lấy dư theo lũy thừa của 2 rất nhanh ở mức phần cứng.
- Số lượng "chữ số" nội bộ giảm xuống rất nhiều so với cơ số 10.

---

## Thuật toán Karatsuba

### Ý tưởng trung tâm

Nếu nhân theo cách đặt tính thông thường, ta phải tính đủ 4 tích con khi tách đôi hai số:

$$
U = U_1 B^m + U_0,
\qquad
V = V_1 B^m + V_0
$$

Khi đó:

$$
U \cdot V = U_1V_1 B^{2m} + (U_1V_0 + U_0V_1)B^m + U_0V_0
$$

Cách thông thường cần 4 phép nhân:

- $U_0V_0$
- $U_1V_1$
- $U_1V_0$
- $U_0V_1$

Karatsuba giảm còn **3 phép nhân lớn** bằng mẹo đại số:

$$
(U_0 + U_1)(V_0 + V_1) = U_0V_0 + U_1V_1 + U_1V_0 + U_0V_1
$$

Suy ra:

$$
U_1V_0 + U_0V_1 = (U_0 + U_1)(V_0 + V_1) - U_0V_0 - U_1V_1
$$

Đặt:

$$
z_0 = U_0V_0
$$

$$
z_2 = U_1V_1
$$

$$
z_1 = (U_0 + U_1)(V_0 + V_1) - z_0 - z_2
$$

Ta ghép lại được:

$$
U \cdot V = z_2 B^{2m} + z_1 B^m + z_0
$$

---

### K1: Chuẩn hóa độ dài và điểm dừng

Trước tiên, thuật toán lấy:

$$
n = \max(\text{len}(U), \text{len}(V))
$$

Nếu một số ngắn hơn, nó được **padding thêm số 0** để hai bên có cùng độ dài.

Nếu kích thước đủ nhỏ (trong code là `n <= 2`) thì không đệ quy nữa, mà chuyển sang **schoolbook multiplication**.

**Bản chất:**

Đây là bước chọn ngưỡng tối ưu. Với số rất ngắn, chi phí đệ quy còn đắt hơn lợi ích Karatsuba.

**Mục đích:**

Giữ cho thuật toán nhanh hơn cách nhân thường trên các số lớn, nhưng không bị tốn overhead trên các số nhỏ.

---

### K2: Chia đôi số

Chọn:

$$
m = \left\lfloor \frac{n}{2} \right\rfloor
$$

Rồi tách mỗi số thành 2 nửa:

$$
U = U_1 B^m + U_0,
\qquad
V = V_1 B^m + V_0
$$

Trong code:

- `a0 = a[:m]`
- `a1 = a[m:]`
- `b0 = b[:m]`
- `b1 = b[m:]`

Do mảng là little-endian nên:

- `a0`, `b0` là **nửa thấp**
- `a1`, `b1` là **nửa cao**

**Bản chất:**

Đây là phép tách một bài toán lớn thành các bài toán con nhỏ hơn, theo tinh thần divide-and-conquer.

**Mục đích:**

Biến phép nhân lớn thành các phép nhân trên những khối nhỏ hơn, rồi ghép lại bằng dịch cơ số.

---

### K3: Tính hai tích biên $z_0$ và $z_2$

Ta tính đệ quy:

$$
z_0 = U_0 \cdot V_0
$$

$$
z_2 = U_1 \cdot V_1
$$

**Bản chất:**

- $z_0$ là phần tích của nửa thấp
- $z_2$ là phần tích của nửa cao

**Mục đích:**

Đây là hai đầu mút của kết quả cuối cùng: một phần nằm ở vùng chữ số thấp, một phần nằm ở vùng chữ số cao.

---

### K4: Tính tích giữa $z_1$

Thay vì tính trực tiếp:

$$
U_1V_0 + U_0V_1
$$

Karatsuba dùng:

$$
z_1 = (U_0 + U_1)(V_0 + V_1) - z_2 - z_0
$$

**Bản chất:**

Đây là bước tiết kiệm số lần nhân. Ta chấp nhận thêm phép cộng và trừ để đổi lấy việc bớt đi 1 phép nhân lớn.

**Mục đích:**

Giảm độ phức tạp thời gian từ gần $O(n^2)$ xuống:

$$
T(n) = 3T(n/2) + O(n)
$$

Theo định lý Master, nghiệm xấp xỉ là:

$$
T(n) = O(n^{\log_2 3}) \approx O(n^{1.585})
$$

Xem giải thích chi tiết hơn ở: [`docs/index_z1.md`](docs/index_z1.md)

---

### K5: Dịch trái theo cơ số và ghép kết quả

Sau khi có $z_0$, $z_1$, $z_2$, ta ghép lại:

$$
U \cdot V = z_0 + z_1 B^m + z_2 B^{2m}
$$

Trong code, việc nhân với $B^m$ hoặc $B^{2m}$ được thực hiện bằng `shift_left_le`:

- `shift_left_le(z1, m)`
- `shift_left_le(z2, 2*m)`

Vì mảng đang ở little-endian, dịch trái theo cơ số nghĩa là thêm số 0 vào **đầu mảng**.

**Bản chất:**

Đây là bước đặt các khối con về đúng trọng số vị trí của chúng trong biểu diễn đa thức theo cơ số $B$.

**Mục đích:**

Khôi phục lại một số hoàn chỉnh từ 3 mảnh con đã được tính riêng.

---

### K6: Xóa số 0 vô nghĩa

Trong suốt quá trình cộng/trừ/đệ quy, một số kết quả trung gian có thể sinh thêm các số 0 ở đầu phần cao.

Hàm `trim_leading_zeros` sẽ loại bỏ các số 0 đó để đảm bảo:

- So sánh đúng độ dài số
- Biểu diễn nhất quán
- Không làm phình kích thước giả tạo trong các lần đệ quy sau

---

## Ví dụ trực quan

Xét:

$$
1234 \times 5678
$$

Chọn $m = 2$, khi đó:

$$
1234 = 12 \cdot 10^2 + 34
$$

$$
5678 = 56 \cdot 10^2 + 78
$$

Ta có:

$$
z_0 = 34 \times 78 = 2652
$$

$$
z_2 = 12 \times 56 = 672
$$

$$
z_1 = (34+12)(78+56) - 2652 - 672
$$

$$
z_1 = 46 \times 134 - 2652 - 672 = 6164 - 3324 = 2840
$$

Ghép lại:

$$
1234 \times 5678 = 672 \cdot 10^4 + 2840 \cdot 10^2 + 2652
$$

$$
= 6{,}720{,}000 + 284{,}000 + 2{,}652 = 7{,}006{,}652
$$

---

## Tóm tắt tinh thần của thuật toán

Karatsuba không làm phép màu nào cả. Nó chỉ dùng một quan sát rất đẹp:

- **Phép nhân lớn là đắt**
- **Phép cộng/trừ là rẻ hơn nhiều**

Nên thay vì dùng 4 phép nhân lớn, ta đổi sang:

- 3 phép nhân lớn
- thêm vài phép cộng/trừ/dịch vị trí

Khi lặp lại ý tưởng này theo đệ quy, tổng chi phí giảm đáng kể.

Vì vậy Karatsuba là một bước chuyển rất quan trọng từ nhân "đặt tính" sang nhân số lớn theo tư duy chia để trị.
