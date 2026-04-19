# SPDX-FileCopyrightText: (c) 2026
#
# SPDX-License-Identifier: Apache-2.0

import sys


def string_to_little_endian(num_str: str) -> list[int]:
    num_str = num_str.strip()
    if not num_str.isdigit():
        raise ValueError(f"Invalid integer string: {num_str}")
    if num_str == "0":
        return [0]
    return [int(ch) for ch in reversed(num_str)]


def little_endian_to_string(arr: list[int]) -> str:
    arr = trim_leading_zeros(arr[:])
    return "".join(str(d) for d in reversed(arr))


def trim_leading_zeros(arr: list[int]) -> list[int]:
    while len(arr) > 1 and arr[-1] == 0:
        arr.pop()
    return arr


def compare_le(a: list[int], b: list[int]) -> int:
    a = trim_leading_zeros(a[:])
    b = trim_leading_zeros(b[:])

    if len(a) < len(b):
        return -1
    if len(a) > len(b):
        return 1

    for i in range(len(a) - 1, -1, -1):
        if a[i] < b[i]:
            return -1
        if a[i] > b[i]:
            return 1
    return 0


def add_le(a: list[int], b: list[int], base: int = 10) -> list[int]:
    n = max(len(a), len(b))
    result = []
    carry = 0

    for i in range(n):
        da = a[i] if i < len(a) else 0
        db = b[i] if i < len(b) else 0
        s = da + db + carry
        result.append(s % base)
        carry = s // base

    if carry:
        result.append(carry)

    return trim_leading_zeros(result)


def sub_le(a: list[int], b: list[int], base: int = 10) -> list[int]:
    # Assume a >= b
    if compare_le(a, b) < 0:
        raise ValueError("sub_le requires a >= b")

    result = []
    borrow = 0

    for i in range(len(a)):
        da = a[i]
        db = b[i] if i < len(b) else 0
        cur = da - db - borrow
        if cur < 0:
            cur += base
            borrow = 1
        else:
            borrow = 0
        result.append(cur)

    return trim_leading_zeros(result)


def shift_left_le(a: list[int], k: int) -> list[int]:
    if a == [0]:
        return [0]
    return [0] * k + a


def schoolbook_mul_le(a: list[int], b: list[int], base: int = 10) -> list[int]:
    if a == [0] or b == [0]:
        return [0]

    result = [0] * (len(a) + len(b))

    for i in range(len(a)):
        carry = 0
        for j in range(len(b)):
            total = result[i + j] + a[i] * b[j] + carry
            result[i + j] = total % base
            carry = total // base

        pos = i + len(b)
        while carry > 0:
            total = result[pos] + carry
            result[pos] = total % base
            carry = total // base
            pos += 1

    return trim_leading_zeros(result)


def karatsuba_le(a: list[int], b: list[int], base: int = 10) -> list[int]:
    """
    Multiply two big integers in little-endian digit arrays using Karatsuba.

    Example:
        1234 -> [4, 3, 2, 1]
    """
    a = trim_leading_zeros(a[:])
    b = trim_leading_zeros(b[:])

    if a == [0] or b == [0]:
        return [0]

    n = max(len(a), len(b))

    # Base case
    if n <= 2:
        return schoolbook_mul_le(a, b, base)

    # Pad to same length
    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))

    m = n // 2

    a0 = a[:m]
    a1 = a[m:]
    b0 = b[:m]
    b1 = b[m:]

    z0 = karatsuba_le(a0, b0, base)
    z2 = karatsuba_le(a1, b1, base)

    a0_plus_a1 = add_le(a0, a1, base)
    b0_plus_b1 = add_le(b0, b1, base)

    z1 = karatsuba_le(a0_plus_a1, b0_plus_b1, base)
    z1 = sub_le(z1, z2, base)
    z1 = sub_le(z1, z0, base)

    result = add_le(
        add_le(z0, shift_left_le(z1, m), base),
        shift_left_le(z2, 2 * m),
        base,
    )
    return trim_leading_zeros(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python multiply.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    test_case_count = 0
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue

        test_case_count += 1
        u_str = parts[0]
        v_str = parts[1]

        u = string_to_little_endian(u_str)
        v = string_to_little_endian(v_str)

        result = karatsuba_le(u, v, base=10)
        result_str = little_endian_to_string(result)

        print(f"Test case {test_case_count}:")
        print(f"  So thu nhat : {u_str}")
        print(f"  So thu hai : {v_str}")
        print(f"  Tich       : {result_str}")
        print(f"  Thuc te    : {int(u_str) * int(v_str)}")
        print()