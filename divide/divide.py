import sys

def multiply_by_scalar(arr, scalar, base):
    """Hàm phụ trợ: Nhân một số (dạng mảng) với một số nguyên nhỏ"""
    res = []
    carry = 0
    for x in arr:
        temp = x * scalar + carry
        res.append(temp % base)
        carry = temp // base
    if carry > 0:
        res.append(carry)
    return res

def knuth_algorithm_d(u, v, base=10):
    """
    Chia u cho v trong hệ cơ số `base`.
    u, v là các mảng chữ số Little-Endian (VD: 123 -> [3, 2, 1]).
    Trả về: (Thương số Q, Số dư R) dạng mảng.
    """
    # Xóa các số 0 vô nghĩa ở cuối mảng (leading zeros in math)
    while len(u) > 1 and u[-1] == 0: u.pop()
    while len(v) > 1 and v[-1] == 0: v.pop()
        
    n = len(v)
    m = len(u) - n
    
    # Algorithm D yêu cầu số chia có ít nhất 2 chữ số. 
    # Nếu n=1, ta chỉ cần chia trực tiếp (Algorithm S).
    if n <= 1:
        raise ValueError("Thuật toán D yêu cầu số chia có >= 2 chữ số.")
    if m < 0:
        return [0], u.copy() # Nếu số bị chia < số chia -> Thương = 0, Dư = u

    # Khởi tạo mảng thương số
    q = [0] * (m + 1)
    
    # Bước D1: Chuẩn hóa (Normalize)
    # Tìm hệ số d sao cho chữ số đầu tiên của v_norm >= base / 2
    d = base // (v[-1] + 1)
    
    u_norm = multiply_by_scalar(u, d, base)
    v_norm = multiply_by_scalar(v, d, base)
    
    # Đảm bảo u_norm có đủ độ dài (m + n + 1) chữ số
    while len(u_norm) < m + n + 1:
        u_norm.append(0)

    # Bước D2: Khởi tạo vòng lặp (j chạy từ m xuống 0)
    for j in range(m, -1, -1):
        
        # Bước D3: Ước lượng thương số (Calculate q_hat)
        numerator = u_norm[j + n] * base + u_norm[j + n - 1]
        q_hat = numerator // v_norm[-1]
        r_hat = numerator % v_norm[-1]
        
        # Kiểm tra và tinh chỉnh q_hat dựa trên chữ số tiếp theo
        while q_hat == base or (q_hat * v_norm[-2] > base * r_hat + u_norm[j + n - 2]):
            q_hat -= 1
            r_hat += v_norm[-1]
            if r_hat >= base:
                break
                
        # Bước D4 & D5: Nhân và Trừ (Multiply and subtract)
        carry = 0
        for i in range(n):
            temp = u_norm[j + i] - q_hat * v_norm[i] - carry
            u_norm[j + i] = temp % base
            carry = -(temp // base)
                
        # Trừ carry cuối cùng vào phần tử cao nhất
        temp = u_norm[j + n] - carry
        
        if temp < 0:
            # Bước D6: Sửa sai (Add back)
            # Nếu kết quả âm, ta đã ước lượng q_hat quá lớn (lệch 1 đơn vị)
            q_hat -= 1
            carry = 0
            for i in range(n):
                temp = u_norm[j + i] + v_norm[i] + carry
                u_norm[j + i] = temp % base
                carry = temp // base
            u_norm[j + n] += carry
        else:
            u_norm[j + n] = temp
            
        # Lưu lại chữ số của thương
        q[j] = q_hat

    # Bước D8: Giải chuẩn hóa (Unnormalize) để tìm số dư thật
    remainder = []
    carry = 0
    # Cắt lấy n chữ số đầu của u_norm rồi chia ngược lại cho d
    for i in range(n - 1, -1, -1):
        temp = carry * base + u_norm[i]
        remainder.append(temp // d)
        carry = temp % d
    remainder.reverse() # Xoay lại thành Little-Endian
    
    # Xóa các số 0 thừa
    while len(q) > 1 and q[-1] == 0: q.pop()
    while len(remainder) > 1 and remainder[-1] == 0: remainder.pop()

    return q, remainder

def string_to_little_endian(s):
    return [int(c) for c in reversed(s.strip())]

def little_endian_to_string(arr):
    if not arr:
        return "0"
    return "".join(str(x) for x in reversed(arr))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python divide.py <file_input>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) < 2:
                print("Lỗi: File cần có ít nhất 2 dòng, mỗi dòng chứa một số.")
                sys.exit(1)
                
            u_str = lines[0]
            v_str = lines[1]
            
            u = string_to_little_endian(u_str)
            v = string_to_little_endian(v_str)
            
            q, r = knuth_algorithm_d(u, v)
            
            print(f"Số bị chia (u): {u_str}")
            print(f"Số chia (v)   : {v_str}")
            print(f"Thương (q)    : {little_endian_to_string(q)}")
            print(f"Dư (r)        : {little_endian_to_string(r)}")
            print(f"Thực tế: ",  int(u_str)/int(v_str))
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{filename}'")
    except Exception as e:
        print(f"Lỗi: {e}")