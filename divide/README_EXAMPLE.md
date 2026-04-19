
## Ví dụ 5144 / 735

#### 1. Khởi tạo & D1: Chuẩn hóa

- Cơ số: $B = 10$.
- Số chia: $V = [7, 3, 5]$ (độ dài $n = 3$).
- Chỉ số: $v_2 = 7$, $v_1 = 3$, $v_0 = 5$.
- Vì $v_2 = 7 \ge 5$ (đạt chuẩn $\ge B/2$), hệ số chuẩn hóa $d = 1$ nên không cần nhân.
- Số bị chia: $U = 5144$.
- Thêm số 0 ở đầu để đủ kích thước: $m+n = 4+1 = 5$ phần tử.
- Mảng $U = [0, 5, 1, 4, 4]$ (chỉ số $u_4=0, u_3=5, u_2=1, u_1=4, u_0=4$).
- Độ dài thương số:
  $m = \text{len}(U) - \text{len}(V) - 1 = 5 - 3 - 1 = 1$.
- Mảng thương có 2 phần tử ($q_1, q_0$):
  $Q = [0, 0]$.

#### 2. Vòng lặp D2 với $j = 1$ (tìm $q_1$)

**D3: Tính ước lượng $\hat{q}$**

- Lấy $u_{j+n}$ và $u_{j+n-1}$: $u_4, u_3 \Rightarrow 05$.
- Lấy $v_{n-1}$: $v_2 = 7$.
- Tính:
  $\hat{q} = \lfloor 05 \div 7 \rfloor = \textbf{0}$.

**Kiểm tra vi chỉnh**

- Số dư: $r = 05 \pmod 7 = 5$.
- Kiểm tra:
  $\hat{q} \times v_{n-2} \le r \times B + u_{j+n-2}$
  $\Rightarrow 0 \times 3 \le 5 \times 10 + 1$
  $\Rightarrow 0 \le 51$ (đúng, giữ nguyên $\hat{q}=0$).

**D4: Nhân và Trừ**

- Cắt khung 4 phần tử tại $j=1$:
  $[u_4, u_3, u_2, u_1] = 0514$.
- Tính:
  $\hat{q} \times V = 0 \times 735 = 0$.
- Trừ:
  $0514 - 0000 = 0514$ (kết quả $\ge 0$).
- Trạng thái $U$ không đổi: $[0, 5, 1, 4, 4]$.

**D5: Lưu Q**

- Gán $q_1 = \textbf{0}$.
- Mảng $Q$ hiện tại: $[0, \_]$.

#### 3. Vòng lặp D2 với $j = 0$ (tìm $q_0$)

**D3: Tính ước lượng $\hat{q}$**

- Lấy $u_{j+n}$ và $u_{j+n-1}$: $u_3, u_2 \Rightarrow 51$.
- Lấy $v_{n-1}$: $v_2 = 7$.
- Tính:
  $\hat{q} = \lfloor 51 \div 7 \rfloor = \textbf{7}$.

**Kiểm tra vi chỉnh**

- Số dư: $r = 51 \pmod 7 = 2$.
- Với $v_{n-2}=v_1=3$, $u_{j+n-2}=u_1=4$:
  $7 \times 3 \le 2 \times 10 + 4$
  $\Rightarrow 21 \le 24$ (đúng, giữ nguyên $\hat{q}=7$).


**D4: Nhân và Trừ**

- Cắt khung 4 phần tử tại $j=0$:
  $[u_3, u_2, u_1, u_0] = 5144$.
- Tính:
  $\hat{q} \times V = 7 \times 735 = \textbf{5145}$.
- Trừ:
  $5144 - 5145 = \textbf{-1}$.
- Ghi nhận âm (Borrow = 1)

**D6: Cộng bù (Add-Back) vì D4 bị âm**

- Giảm $\hat{q}$ đi 1:
  $\hat{q} = \textbf{6}$.
- Sửa khung $U$ bằng cộng bù với $V$:
  $-1 + 735 = \textbf{734}$.
- Cập nhật khung mới:
  $[u_3, u_2, u_1, u_0] = 0734$.
- Trạng thái $U$ toàn cục:
  $[0, 0, 7, 3, 4]$.

**D5: Lưu Q**

- Gán $q_0 = \textbf{6}$.
- Mảng $Q$ hoàn thành: $[0, 6]$.

#### 4. D8: Hủy chuẩn hóa (Kết luận)

- Thương số:
  $Q = [0, 6] \Rightarrow \textbf{Q = 6}$.
- Số dư:
  từ $U = [0, 0, 7, 3, 4] \Rightarrow 734$.
  Vì $d=1$ nên vẫn là $\textbf{R = 734}$.

Kết quả cuối cùng:

$$
5144 = 735 \times 6 + 734
$$