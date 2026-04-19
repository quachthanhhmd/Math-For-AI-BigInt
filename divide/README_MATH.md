## Giải thích theo toán trừu tượng

Thuật toán này giải quyết bài toán tìm đa thức thương $Q(B)$ và đa thức dư $R(B)$ trên không gian các đa thức, trong đó mọi hệ số phải được duy trì ở dạng chuẩn tắc thuộc vành:

$$
\mathbb{Z}_B = \{0, 1, 2, \dots, B-1\}
$$

### 1. Vành đa thức $\mathbb{Z}_B$ biểu diễn cho số nguyên lớn

Cho cơ số $B \ge 2$. Một số nguyên $U$ và $V$ được biểu diễn duy nhất dưới dạng đa thức bậc $k$ và $i$ theo biến vành $\mathbb{Z}_B$:

$$U(X) = \sum_{k=0}^{m+n-1} u_k B^k = u_k B^k + u_{k-1} B^{k-1} + \dots + u_1 B + u_0$$

$$V(X) = \sum_{i=0}^{n-1} v_i B^i = v_k B^i + v_{i-1} B^{i-1} + \dots + v_1 B + v_0$$

Điều kiện cần: mọi hệ số $u_k, v_i \in \mathbb{Z}_B$.

Mục tiêu của thuật toán là đi tìm đa thức thương $Q(X) = \sum_{j=0}^{m} q_j X^j$ và đa thức dư $R(X)$ sao cho:$$U(X) = Q(X) \cdot V(X) + R(X)$$



với ràng buộc bậc của $R$ nhỏ hơn bậc của $V$ ($deg(R)$ < $deg(V)$), và mọi hệ số của $Q, R$ $\in$ $\mathbb{Z}_B$.

### 2. Bước D1: Phép đồng dạng đa thức (Isomorphic Scaling)

Thuật toán không giải trực tiếp trên $U, V$ vì sai số khi xấp xỉ sẽ không hội tụ. Thay vào đó, ta tạo một **hệ phương trình đồng dạng** bằng cách nhân cả hai với một vô hướng $d \in \mathbb{Z}^+$:

$$
U'(X) = d \cdot U(X), \quad V'(X) = d \cdot V(X)
$$

Phép chia trên $(U', V')$ cho cùng thương số $Q(X)$ như trên $(U, V)$ nhưng với sai số được kiểm soát.

#### Điều kiện chuẩn hóa metrik

Chọn $d$ sao cho hệ số dẫn đầu của $V'$ đạt đến gần nửa cơ số:

$$
d = \left\lfloor \frac{B}{v_{n-1} + 1} \right\rfloor
$$

Mục tiêu: đảm bảo rằng

$$
v'_{n-1} = d \cdot v_{n-1} \ge \left\lfloor \frac{B}{2} \right\rfloor
$$

**Tại sao điều kiện này lại quan trọng?**

Khi hệ số dẫn đầu của số chia "đủ lớn", nó lấp đầy phần lớn không gian chứa của cơ số $B$. Điều này giới hạn sai số khi máy tính dùng phép chia xấp xỉ để ước lượng thương số $\hat{q}$. 

Xem thêm: [Ví dụ cụ thể về tính toán $d$ với các số chia khác nhau](docs/index_d.md)

### 3. Bước D3: Phép chiếu (Projection) và xấp xỉ Diophantine

Để tìm được hệ số thương chuẩn xác $q_j$, về nguyên tắc, ta phải lấy toàn bộ phần đa thức bị chia $U'(X)$ chia cho toàn bộ đa thức số chia $V'(X)$. Nhưng $V'(X)$ là một đa thức có thể dài hàng vạn bậc. Việc giải phương trình trên một không gian chiều khổng lồ như vậy là bất khả thi về mặt tính toán.


Trong đại số đa thức, hệ số dẫn đầu (leading coefficients) mang trọng số áp đảo, quyết định xu hướng của toàn bộ đa thức.Do đó, Knuth áp dụng một phép chiếu: Ta chủ động "phớt lờ" toàn bộ phần đuôi của đa thức $V'(X)$ (coi các hệ số từ bậc $n-2$ trở xuống bằng $0$). Ta hạ không gian bài toán từ $n$ chiều xuống chỉ còn không gian $2$ chiều.Lúc này, bài toán tìm nghiệm phức tạp thu gọn lại thành phép tính xấp xỉ cục bộ (tại lân cận của bậc cao nhất $j+n$):$$\hat{q} = \left\lfloor \frac{u'_{j+n}X + u'_{j+n-1}}{v'_{n-1}} \right\rfloor \Bigg|_{X=B}$$Dịch nghĩa công thức: Lấy đúng 2 hệ số cao nhất của phần $U'$ đang xét, đem chia cho đúng 1 hệ số cao nhất của $V'$. Định giá tại $X = B$.
### 4. Bước D4: Phép trừ đa thức (Polynomial Subtraction)

Ta thực hiện phép trừ đa thức để bóc tách dần các bậc của $U'(X)$:

$$
U^{(\text{mới})}(X) = U^{(\text{cũ})}(X) - (\hat{q} X^j) \cdot V'(X)
$$

Khai triển theo luật phân phối:

$$
(\hat{q} X^j) \cdot \left( \sum_{i=0}^{n-1} v'_i X^i \right) = \sum_{i=0}^{n-1} (\hat{q} v'_i) X^{j+i}
$$

**Nguồn gốc của chỉ số $j+i$:**

Sự xuất hiện của tổng $j+i$ không phải thủ thuật lập trình, mà là **tất yếu của luật nhân lũy thừa**: khi ta nhân $X^j \cdot X^i$, số mũ cộng lại thành $X^{j+i}$.

### 5. D5: Thực hiện phép cộng trừ trên hệ số B (Carry/Borrow)

Sau phép trừ đa thức, hệ số mới tại bậc $X^{j+i}$ là:

$$
X_{\text{temp}} = u'_{j+i} - \hat{q} \cdot v'_i - c_{\text{cũ}}
$$

Hệ số này thuộc $\mathbb{Z}$ nhưng có thể **vi phạm điều kiện chuẩn tắc** (có thể âm hoặc $\ge B$).

Ta áp dụng **định lý chia có dư Euclidean** để khôi phục dạng chuẩn tắc:

$$
X_{\text{temp}} = c_{\text{mới}} \cdot B + r, \quad 0 \le r < B
$$

**Tách thành 2 phần:**

- **Phần dư** $r = X_{\text{temp}} \bmod B$: được giữ lại làm hệ số chuẩn tắc cho bậc $X^{j+i}$
- **Thương số** $c_{\text{mới}} = \lfloor X_{\text{temp}} / B \rfloor$: được đẩy lên bậc $X^{j+i+1}$ dưới dạng **Carry/Borrow** để tiếp tục tham gia vào phương trình bậc cao hơn

**Đẳng thức đại số:** $c_{\text{mới}} \cdot B \cdot X^{j+i} \equiv c_{\text{mới}} \cdot X^{j+i+1}$

### 6. Bước D6: Perturbation & Add-Back

Vì $\hat{q}$ là **nghiệm xấp xỉ** (có thể lớn hơn nghiệm thực tối đa 2 đơn vị), phép trừ đa thức có thể dẫn đến **hệ số cao nhất của $U^{(\text{mới})}(X)$ bị âm**, vi phạm tính không âm của không gian nghiệm.

**Khi phát hiện sự vi phạm** ($u'_{\text{cao nhất}} < 0$), hệ thống tự động thực hiện bổ chính:

1. Giảm nghiệm xấp xỉ: $\hat{q} \mapsto \hat{q} - 1$
2. Cộng bù lại đa thức chia vào phần dư: $U^{(\text{mới})}(X) \mapsto U^{(\text{mới})}(X) + X^j \cdot V'(X)$

**Quy trình này lặp lại** (tối đa 2 lần) cho đến khi $U^{(\text{mới})}(X)$ hoàn toàn trở về **dạng chuẩn tắc không âm**. Lúc này:

- $\hat{q}$ **hội tụ về nghiệm thực** $q_j$
- Đa thức $U(X)$ hiện tại chính là **đa thức dư** $R(X)$


### Bước D7: Huy Chuẩn hoá

Sau khi có kết quả $Q(X)$ và $R(X)$, nếu $d > 1$. Ta huỷ chuẩn hoá bằng công thức.
$$R(X)_{new} = \frac{R(X)}{d}$$

Bởi vì ở D1, ta nhân $U(X), V(X)$