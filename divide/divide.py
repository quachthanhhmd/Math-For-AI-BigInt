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

def knuth_algorithm_d(u, v, base=10, debug=False):
    """
    Chia u cho v trong hệ cơ số `base`.
    u, v là các mảng chữ số Little-Endian (VD: 123 -> [3, 2, 1]).
    Trả về: (Thương số Q, Số dư R) dạng mảng.
    """
    if debug:
        print(f"\n{'='*60}")
        print(f"KNUTH ALGORITHM D - Chia {little_endian_to_string(u)} / {little_endian_to_string(v)}")
        print(f"{'='*60}")
        print(f"Input (Little-Endian): u = {u}, v = {v}, base = {base}\n")
    
    # Xóa các số 0 vô nghĩa ở cuối mảng (leading zeros in math)
    while len(u) > 1 and u[-1] == 0: u.pop()
    while len(v) > 1 and v[-1] == 0: v.pop()
        
    n = len(v)
    m = len(u) - n
    
    if debug:
        print(f"Sau khi xóa leading zeros: u = {u}, v = {v}")
        print(f"n = len(v) = {n}, m = len(u) - n = {m}\n")
    
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
    
    if debug:
        print(f"\n{'─'*60}")
        print(f"BƯỚC D1: CHUẨN HÓA (Normalize)")
        print(f"{'─'*60}")
        print(f"d = ⌊B / (v[{n-1}] + 1)⌋ = ⌊{base} / ({v[-1]} + 1)⌋ = {d}")
        print(f"u_norm = u × d = {little_endian_to_string(u)} × {d} = {little_endian_to_string(u_norm)}")
        print(f"v_norm = v × d = {little_endian_to_string(v)} × {d} = {little_endian_to_string(v_norm)}")
        print(f"u_norm (array): {u_norm}")
        print(f"v_norm (array): {v_norm}\n")

    # Bước D2: Khởi tạo vòng lặp (j chạy từ m xuống 0)
    for j in range(m, -1, -1):
        
        # Bước D3: Ước lượng thương số (Calculate q_hat)
        numerator = u_norm[j + n] * base + u_norm[j + n - 1]
        q_hat = numerator // v_norm[-1]
        r_hat = numerator % v_norm[-1]
        
        if debug:
            print(f"\n{'─'*60}")
            print(f"LẶP j = {j} - TÌM q[{j}]")
            print(f"{'─'*60}")
            print(f"D3: Ước lượng q̂")
            print(f"  Cửa sổ: u[{j+n}:{j}] = {u_norm[j:j+n+1][::-1]}")
            print(f"  numerator = u[{j+n}] × B + u[{j+n-1}] = {u_norm[j+n]} × {base} + {u_norm[j+n-1]} = {numerator}")
            print(f"  q̂ = ⌊{numerator} / {v_norm[-1]}⌋ = {q_hat}")
            print(f"  r̂ = {numerator} mod {v_norm[-1]} = {r_hat}")
        
        # Kiểm tra và tinh chỉnh q_hat dựa trên chữ số tiếp theo
        while q_hat == base or (q_hat * v_norm[-2] > base * r_hat + u_norm[j + n - 2]):
            q_hat -= 1
            r_hat += v_norm[-1]
            if r_hat >= base:
                break
        
        if debug and (q_hat != (numerator // v_norm[-1])):
            print(f"  q̂ adjusted = {q_hat}")
                
        # Bước D4 & D5: Nhân và Trừ (Multiply and subtract)
        if debug:
            print(f"\nD4-D5: Nhân & Trừ")
            print(f"  Tính: u[{j}:{j+n}] - q̂ × v_norm")
        
        carry = 0
        for i in range(n):
            temp = u_norm[j + i] - q_hat * v_norm[i] - carry
            u_norm[j + i] = temp % base
            carry = -(temp // base)
            if debug and i == 0:
                print(f"    u[{j}] = {u_norm[j]}, carry = {carry}")
                
        # Trừ carry cuối cùng vào phần tử cao nhất
        temp = u_norm[j + n] - carry
        
        if temp < 0:
            # Bước D6: Sửa sai (Add back)
            # Nếu kết quả âm, ta đã ước lượng q_hat quá lớn (lệch 1 đơn vị)
            if debug:
                print(f"  Kết quả âm! Cần sửa sai (D6)")
            q_hat -= 1
            carry = 0
            for i in range(n):
                temp = u_norm[j + i] + v_norm[i] + carry
                u_norm[j + i] = temp % base
                carry = temp // base
            u_norm[j + n] += carry
            if debug:
                print(f"  q̂ -= 1 → q̂ = {q_hat}")
        else:
            u_norm[j + n] = temp
        
        if debug:
            print(f"  u_norm sau bước: {u_norm}")
        
        # Lưu lại chữ số của thương
        q[j] = q_hat
        if debug:
            print(f"  q[{j}] = {q_hat}")

    # Bước D8: Giải chuẩn hóa (Unnormalize) để tìm số dư thật
    remainder = []
    carry = 0
    # Cắt lấy n chữ số đầu của u_norm rồi chia ngược lại cho d
    for i in range(n - 1, -1, -1):
        temp = carry * base + u_norm[i]
        remainder.append(temp // d)
        carry = temp % d
    remainder.reverse() # Xoay lại thành Little-Endian
    
    if debug:
        print(f"\n{'─'*60}")
        print(f"BƯỚC D8: GIẢI CHUẨN HÓA (Unnormalize)")
        print(f"{'─'*60}")
        print(f"Q (thương) = {little_endian_to_string(q)}")
        print(f"R (dư gốc) = {little_endian_to_string(remainder)}\n")
    
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

def parse_test_cases(lines):
    """
    Hỗ trợ 2 định dạng input:
    1) Mỗi dòng chứa 2 số: "u v"
    2) Mỗi 2 dòng là 1 test case: dòng 1 là u, dòng 2 là v
    """
    cleaned = []
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if line:
            cleaned.append(line)

    if not cleaned:
        return []

    if all(len(line.split()) >= 2 for line in cleaned):
        return [(line.split()[0], line.split()[1]) for line in cleaned]

    if all(len(line.split()) == 1 for line in cleaned):
        if len(cleaned) % 2 != 0:
            raise ValueError("Input dạng 2 dòng/case phải có số dòng chẵn.")
        return [(cleaned[i], cleaned[i + 1]) for i in range(0, len(cleaned), 2)]

    raise ValueError("Định dạng input không hợp lệ. Dùng 'u v' mỗi dòng hoặc 2 dòng/case.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python divide.py <file_input> [--debug]")
        print("Định dạng file: mỗi dòng 'u v' hoặc mỗi 2 dòng là một test case.")
        sys.exit(1)

    base = 10
    filename = sys.argv[1]
    debug_mode = "--debug" in sys.argv[2:]

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

            test_cases = parse_test_cases(lines)
            if not test_cases:
                print("Lỗi: File không có test case hợp lệ.")
                sys.exit(1)

            passed = 0
            failed = 0

            if debug_mode and len(test_cases) > 1:
                print("[Ghi chú] --debug đang bật: chỉ in chi tiết cho test case đầu tiên.\n")

            for idx, (u_str, v_str) in enumerate(test_cases, start=1):
                print(f"\n{'=' * 64}")
                print(f"TEST CASE {idx}")
                print(f"{'=' * 64}")
                print(f"Số bị chia (u): {u_str}")
                print(f"Số chia (v)   : {v_str}")

                try:
                    if not u_str.isdigit() or not v_str.isdigit():
                        raise ValueError("Mỗi test case phải chứa số nguyên không âm.")
                    if int(v_str) == 0:
                        raise ValueError("Số chia không được bằng 0.")

                    u = string_to_little_endian(u_str)
                    v = string_to_little_endian(v_str)

                    q, r = knuth_algorithm_d(u, v, base, debug=(debug_mode and idx == 1))

                    q_str = little_endian_to_string(q)
                    r_str = little_endian_to_string(r)

                    expected_q, expected_r = divmod(int(u_str), int(v_str))
                    ok = (q_str == str(expected_q) and r_str == str(expected_r))

                    print(f"Thương (q)    : {q_str}")
                    print(f"Dư (r)        : {r_str}")
                    print(f"Thực tế q, r  : {expected_q}, {expected_r}")
                    print(f"Kết luận      : {'OK' if ok else 'SAI'}")

                    if ok:
                        passed += 1
                    else:
                        failed += 1

                except Exception as case_error:
                    failed += 1
                    print(f"Kết luận      : ERROR - {case_error}")

            print(f"\nTổng kết: {passed} OK, {failed} lỗi, tổng {len(test_cases)} test case.")
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{filename}'")
    except Exception as e:
        print(f"Lỗi: {e}")