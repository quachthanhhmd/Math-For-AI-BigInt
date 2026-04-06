# SPDX-FileCopyrightText: (c) 2026
#
# SPDX-License-Identifier: Apache-2.0

from manimlib import *


def trim_leading_zeros(arr):
    arr = arr[:]
    while len(arr) > 1 and arr[-1] == 0:
        arr.pop()
    return arr


def string_to_little_endian(num_str):
    num_str = num_str.strip()
    if num_str == "0":
        return [0]
    return [int(ch) for ch in reversed(num_str)]


def little_endian_to_string(arr):
    arr = trim_leading_zeros(arr)
    return "".join(str(d) for d in reversed(arr))


def add_le(a, b, base=10):
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


def compare_le(a, b):
    a = trim_leading_zeros(a)
    b = trim_leading_zeros(b)
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


def sub_le(a, b, base=10):
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


def shift_left_le(a, k):
    if a == [0]:
        return [0]
    return [0] * k + a


def schoolbook_mul_le(a, b, base=10):
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


def karatsuba_steps(a, b, base=10, depth=0, label="root"):
    a = trim_leading_zeros(a[:])
    b = trim_leading_zeros(b[:])

    steps = []
    steps.append({
        "type": "call",
        "depth": depth,
        "label": label,
        "a": little_endian_to_string(a),
        "b": little_endian_to_string(b),
    })

    if a == [0] or b == [0]:
        steps.append({
            "type": "return",
            "depth": depth,
            "label": label,
            "result": "0",
        })
        return [0], steps

    n = max(len(a), len(b))
    if n <= 2:
        result = schoolbook_mul_le(a, b, base)
        steps.append({
            "type": "base_case",
            "depth": depth,
            "label": label,
            "result": little_endian_to_string(result),
        })
        return result, steps

    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))
    m = n // 2

    a0, a1 = a[:m], a[m:]
    b0, b1 = b[:m], b[m:]

    steps.append({
        "type": "split",
        "depth": depth,
        "label": label,
        "m": m,
        "a0": little_endian_to_string(a0),
        "a1": little_endian_to_string(a1),
        "b0": little_endian_to_string(b0),
        "b1": little_endian_to_string(b1),
    })

    z0, s0 = karatsuba_steps(a0, b0, base, depth + 1, label + ".z0")
    z2, s2 = karatsuba_steps(a1, b1, base, depth + 1, label + ".z2")

    sum_a = add_le(a0, a1, base)
    sum_b = add_le(b0, b1, base)

    steps.append({
        "type": "sum_parts",
        "depth": depth,
        "label": label,
        "sum_a": little_endian_to_string(sum_a),
        "sum_b": little_endian_to_string(sum_b),
    })

    z1_raw, s1 = karatsuba_steps(sum_a, sum_b, base, depth + 1, label + ".z1raw")
    z1 = sub_le(sub_le(z1_raw, z2, base), z0, base)

    steps.extend(s0)
    steps.extend(s2)
    steps.extend(s1)

    steps.append({
        "type": "combine_parts",
        "depth": depth,
        "label": label,
        "z0": little_endian_to_string(z0),
        "z1": little_endian_to_string(z1),
        "z2": little_endian_to_string(z2),
    })

    result = add_le(
        add_le(z0, shift_left_le(z1, m), base),
        shift_left_le(z2, 2 * m),
        base,
    )

    steps.append({
        "type": "return",
        "depth": depth,
        "label": label,
        "result": little_endian_to_string(result),
    })

    return result, steps


class MultiplicationScene(Scene):
    def construct(self):
        u_str = "12345678"
        v_str = "87654321"

        u = string_to_little_endian(u_str)
        v = string_to_little_endian(v_str)

        result, steps = karatsuba_steps(u, v)

        title = Text("Karatsuba Multiplication Visualization", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        subtitle = Text(f"U = {u_str}, V = {v_str}", font_size=28)
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle))

        y = 2.2
        shown = VGroup()

        for step in steps[:10]:
            if step["type"] == "call":
                txt = Text(
                    f'Call {step["label"]}: {step["a"]} x {step["b"]}',
                    font_size=24,
                )
            elif step["type"] == "split":
                txt = Text(
                    f'Split: a=({step["a1"]},{step["a0"]}), b=({step["b1"]},{step["b0"]}), m={step["m"]}',
                    font_size=24,
                )
            elif step["type"] == "sum_parts":
                txt = Text(
                    f'Sum parts: (a0+a1)={step["sum_a"]}, (b0+b1)={step["sum_b"]}',
                    font_size=24,
                )
            elif step["type"] == "combine_parts":
                txt = Text(
                    f'Combine: z2={step["z2"]}, z1={step["z1"]}, z0={step["z0"]}',
                    font_size=24,
                )
            elif step["type"] == "base_case":
                txt = Text(
                    f'Base case {step["label"]}: result={step["result"]}',
                    font_size=24,
                )
            else:
                txt = Text(
                    f'Return {step["label"]}: result={step["result"]}',
                    font_size=24,
                )

            txt.move_to([0, y, 0])
            y -= 0.55
            shown.add(txt)

        self.play(LaggedStart(*[FadeIn(m) for m in shown], lag_ratio=0.15))

        final = Text(
            f"Final Result = {little_endian_to_string(result)}",
            font_size=32,
            color=YELLOW,
        )
        final.to_edge(DOWN)
        self.play(Write(final))
        self.wait(2)