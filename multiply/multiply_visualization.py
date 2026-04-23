from manimlib import *


# ============================================================
# Editable inputs
# ============================================================
U_VALUE = "12345678"
V_VALUE = "87654321"
BASE = 10

STEP_RUN_TIME = 0.55
STEP_HOLD_TIME = 0.22
TRANSITION_SHIFT = 0.18

BG_COLOR = "#0f1117"
PANEL_BG = "#141926"
PANEL_ALT = "#1b2233"
TEXT_MAIN = WHITE
TEXT_DIM = GREY_A
ACCENT_CALL = "#7dd3fc"
ACCENT_SPLIT = "#a78bfa"
ACCENT_SUM = "#f59e0b"
ACCENT_BASE = "#34d399"
ACCENT_COMBINE = "#f472b6"
ACCENT_RETURN = "#f87171"
ACCENT_RESULT = "#facc15"
LINE_SOFT = GREY_B


# ============================================================
# Numeric helpers
# ============================================================
def trim_leading_zeros(arr):
    arr = arr[:]
    while len(arr) > 1 and arr[-1] == 0:
        arr.pop()
    return arr


def string_to_little_endian(num_str):
    num_str = num_str.strip()
    if not num_str:
        raise ValueError("Input string must not be empty")
    if not num_str.isdigit():
        raise ValueError(f"Input must contain only digits, got {num_str!r}")
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


# ============================================================
# Karatsuba step tracer
# ============================================================
def karatsuba_steps(a, b, base=10, depth=0, label="root"):
    a = trim_leading_zeros(a[:])
    b = trim_leading_zeros(b[:])

    steps = [{
        "type": "call",
        "depth": depth,
        "label": label,
        "a": little_endian_to_string(a),
        "b": little_endian_to_string(b),
    }]

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
            "a": little_endian_to_string(a),
            "b": little_endian_to_string(b),
            "result": little_endian_to_string(result),
        })
        return result, steps

    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))
    m = n // 2

    a0, a1 = a[:m], a[m:]
    b0, b1 = b[:m], b[m:]

    a0s = little_endian_to_string(a0)
    a1s = little_endian_to_string(a1)
    b0s = little_endian_to_string(b0)
    b1s = little_endian_to_string(b1)

    steps.append({
        "type": "split",
        "depth": depth,
        "label": label,
        "a": little_endian_to_string(a),
        "b": little_endian_to_string(b),
        "m": m,
        "a0": a0s,
        "a1": a1s,
        "b0": b0s,
        "b1": b1s,
    })

    z0, s0 = karatsuba_steps(a0, b0, base, depth + 1, label + ".z0")
    z2, s2 = karatsuba_steps(a1, b1, base, depth + 1, label + ".z2")

    sum_a = add_le(a0, a1, base)
    sum_b = add_le(b0, b1, base)
    sum_a_s = little_endian_to_string(sum_a)
    sum_b_s = little_endian_to_string(sum_b)

    steps.append({
        "type": "sum_parts",
        "depth": depth,
        "label": label,
        "sum_a": sum_a_s,
        "sum_b": sum_b_s,
        "a0": a0s,
        "a1": a1s,
        "b0": b0s,
        "b1": b1s,
    })

    z1_raw, s1 = karatsuba_steps(sum_a, sum_b, base, depth + 1, label + ".z1raw")
    z1 = sub_le(sub_le(z1_raw, z2, base), z0, base)

    steps.extend(s0)
    steps.extend(s2)
    steps.extend(s1)

    z0s = little_endian_to_string(z0)
    z1raws = little_endian_to_string(z1_raw)
    z2s = little_endian_to_string(z2)
    z1s = little_endian_to_string(z1)

    steps.append({
        "type": "combine_parts",
        "depth": depth,
        "label": label,
        "m": m,
        "z0": z0s,
        "z1": z1s,
        "z2": z2s,
        "z1_raw": z1raws,
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


# ============================================================
# Formatting helpers
# ============================================================
def short_label(label, keep=18):
    if len(label) <= keep:
        return label
    return "..." + label[-keep:]


def fit_width(mobj, width):
    if mobj.get_width() > width:
        mobj.set_width(width)
    return mobj


def build_digit_row(value, color, title, box_width=4.0):
    frame = RoundedRectangle(
        corner_radius=0.16,
        width=box_width,
        height=1.2,
        stroke_color=color,
        stroke_width=2,
        fill_color=PANEL_ALT,
        fill_opacity=1,
    )
    label = Text(title, font_size=22, color=TEXT_DIM)
    digits = Text(str(value), font_size=34, color=color)
    fit_width(digits, box_width - 0.5)
    group = VGroup(label, digits).arrange(DOWN, buff=0.14)
    group.move_to(frame.get_center())
    return VGroup(frame, group)


class MultiplicationScene(Scene):
    def make_chip(self, text, color, font_size=20, h_buff=0.22, v_buff=0.12):
        label = Text(text, font_size=font_size, color=color)
        box = RoundedRectangle(
            corner_radius=0.14,
            width=label.get_width() + h_buff * 2,
            height=label.get_height() + v_buff * 2,
            stroke_color=color,
            stroke_width=1.6,
            fill_color=PANEL_ALT,
            fill_opacity=1,
        )
        label.move_to(box.get_center())
        return VGroup(box, label)

    def make_header(self, u_str, v_str):
        title = Text("Karatsuba Multiplication", font_size=34, color=TEXT_MAIN)
        subtitle = Text("single-focus step-by-step animation", font_size=18, color=TEXT_DIM)
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        left_box = build_digit_row(u_str, ACCENT_CALL, "multiplicand A", box_width=3.9)
        right_box = build_digit_row(v_str, ACCENT_BASE, "multiplier B", box_width=3.9)
        op = Text("×", font_size=36, color=LINE_SOFT)
        problem_row = VGroup(left_box, op, right_box).arrange(RIGHT, buff=0.28, aligned_edge=DOWN)

        whole = VGroup(title_block, problem_row).arrange(DOWN, buff=0.32)
        whole.to_edge(UP, buff=0.4)
        return whole

    def empty_stage_panel(self):
        panel = RoundedRectangle(
            corner_radius=0.18,
            width=11.8,
            height=4.7,
            stroke_color=LINE_SOFT,
            stroke_width=1.8,
            fill_color=PANEL_BG,
            fill_opacity=1,
        )
        panel.move_to([0, -0.55, 0])
        return panel

    def build_step_view(self, step, index, total):
        step_type = step["type"]
        color = {
            "call": ACCENT_CALL,
            "split": ACCENT_SPLIT,
            "sum_parts": ACCENT_SUM,
            "base_case": ACCENT_BASE,
            "combine_parts": ACCENT_COMBINE,
            "return": ACCENT_RETURN,
        }[step_type]

        panel = self.empty_stage_panel()
        top_left = panel.get_corner(UL) + RIGHT * 0.4 + DOWN * 0.34
        top_right = panel.get_corner(UR) + LEFT * 0.4 + DOWN * 0.34

        kind = self.make_chip(step_type.replace("_", " ").upper(), color, font_size=18)
        prog = self.make_chip(f"step {index}/{total}", LINE_SOFT, font_size=18)
        depth_chip = self.make_chip(f"depth {step['depth']}", TEXT_DIM, font_size=17)
        label_chip = self.make_chip(short_label(step["label"]), TEXT_DIM, font_size=17)

        kind.move_to(top_left + RIGHT * (kind.get_width() / 2))
        prog.move_to(top_right - RIGHT * (prog.get_width() / 2))
        depth_chip.next_to(kind, DOWN, buff=0.14, aligned_edge=LEFT)
        label_chip.next_to(prog, DOWN, buff=0.14, aligned_edge=RIGHT)

        title = Text("", font_size=34, color=TEXT_MAIN)
        title.move_to(panel.get_center() + UP * 0.9)

        lines = []
        extras = VGroup()

        if step_type == "call":
            title = Text("Enter recursion", font_size=32, color=TEXT_MAIN)
            expr = Text(f"{step['a']} × {step['b']}", font_size=52, color=color)
            hint = Text("check size and recurse if needed", font_size=20, color=TEXT_DIM)
            lines = [expr, hint]

        elif step_type == "split":
            title = Text("Split into high and low parts", font_size=32, color=TEXT_MAIN)
            line1 = Text(f"A = {step['a1']}·10^{step['m']} + {step['a0']}", font_size=28, color=ACCENT_CALL)
            line2 = Text(f"B = {step['b1']}·10^{step['m']} + {step['b0']}", font_size=28, color=ACCENT_BASE)
            line3 = Text(f"m = {step['m']}", font_size=24, color=TEXT_DIM)
            left_half = build_digit_row(step['a1'], ACCENT_CALL, "A high", box_width=2.3)
            right_half = build_digit_row(step['a0'], ACCENT_CALL, "A low", box_width=2.3)
            top_halves = VGroup(left_half, right_half).arrange(RIGHT, buff=0.2)
            left_half_b = build_digit_row(step['b1'], ACCENT_BASE, "B high", box_width=2.3)
            right_half_b = build_digit_row(step['b0'], ACCENT_BASE, "B low", box_width=2.3)
            bottom_halves = VGroup(left_half_b, right_half_b).arrange(RIGHT, buff=0.2)
            halves = VGroup(top_halves, bottom_halves).arrange(DOWN, buff=0.2)
            fit_width(halves, 7.8)
            extras = halves
            lines = [line1, line2, line3]

        elif step_type == "sum_parts":
            title = Text("Prepare the middle product", font_size=32, color=TEXT_MAIN)
            line1 = Text(f"a0 + a1 = {step['a0']} + {step['a1']} = {step['sum_a']}", font_size=27, color=ACCENT_CALL)
            line2 = Text(f"b0 + b1 = {step['b0']} + {step['b1']} = {step['sum_b']}", font_size=27, color=ACCENT_BASE)
            line3 = Text(f"Need z1raw = {step['sum_a']} × {step['sum_b']}", font_size=24, color=color)
            lines = [line1, line2, line3]

        elif step_type == "base_case":
            title = Text("Base case", font_size=32, color=TEXT_MAIN)
            expr = Text(f"{step['a']} × {step['b']} = {step['result']}", font_size=42, color=color)
            hint = Text("small enough → use schoolbook multiplication", font_size=20, color=TEXT_DIM)
            lines = [expr, hint]

        elif step_type == "combine_parts":
            title = Text("Combine z0, z1, z2", font_size=32, color=TEXT_MAIN)
            line1 = Text(f"z0 = {step['z0']}    z2 = {step['z2']}", font_size=28, color=ACCENT_CALL)
            line2 = Text(f"z1raw = {step['z1_raw']}  →  z1 = {step['z1']}", font_size=28, color=ACCENT_SUM)
            line3 = Text(f"result = z2·10^{2 * step['m']} + z1·10^{step['m']} + z0", font_size=24, color=color)
            lines = [line1, line2, line3]

        elif step_type == "return":
            title = Text("Return result", font_size=32, color=TEXT_MAIN)
            expr = Text(f"{short_label(step['label'], keep=24)}  →  {step['result']}", font_size=40, color=color)
            hint = Text("bubble result back to parent call", font_size=20, color=TEXT_DIM)
            lines = [expr, hint]

        title.move_to(panel.get_center() + UP * 0.95)
        fit_width(title, 9.5)

        text_objs = VGroup(*lines)
        text_objs.arrange(DOWN, buff=0.24)
        fit_width(text_objs, 9.6)
        text_objs.move_to(panel.get_center() + UP * 0.05)

        if len(extras) > 0:
            fit_width(extras, 8.2)
            extras.next_to(text_objs, DOWN, buff=0.35)

        return VGroup(panel, kind, prog, depth_chip, label_chip, title, text_objs, extras)

    def transition_to(self, current_group, next_group):
        if current_group is None:
            self.play(FadeIn(next_group, shift=DOWN * TRANSITION_SHIFT), run_time=STEP_RUN_TIME)
            return next_group

        self.play(
            FadeOut(current_group, shift=UP * TRANSITION_SHIFT),
            FadeIn(next_group, shift=DOWN * TRANSITION_SHIFT),
            run_time=STEP_RUN_TIME,
        )
        return next_group

    def make_final_view(self, u_str, v_str, result_str):
        panel = RoundedRectangle(
            corner_radius=0.22,
            width=11.4,
            height=4.9,
            stroke_color=ACCENT_RESULT,
            stroke_width=2.2,
            fill_color=PANEL_BG,
            fill_opacity=1,
        )
        panel.move_to([0, -0.5, 0])

        title = Text("Final result", font_size=36, color=TEXT_MAIN)
        title.move_to(panel.get_center() + UP * 1.45)

        a_box = build_digit_row(u_str, ACCENT_CALL, "multiplicand A", box_width=3.15)
        b_box = build_digit_row(v_str, ACCENT_BASE, "multiplier B", box_width=3.15)
        r_box = build_digit_row(result_str, ACCENT_RESULT, "result", box_width=4.2)

        times = Text("×", font_size=32, color=LINE_SOFT)
        equals = Text("=", font_size=32, color=LINE_SOFT)
        row = VGroup(a_box, times, b_box, equals, r_box).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
        fit_width(row, 10.2)
        row.move_to(panel.get_center() + UP * 0.1)

        verify = Text(
            f"check: {u_str} × {v_str} = {result_str}",
            font_size=22,
            color=TEXT_DIM,
        )
        fit_width(verify, 9.7)
        verify.move_to(panel.get_center() + DOWN * 1.45)

        return VGroup(panel, title, row, verify)

    def construct(self):
        self.camera.background_color = BG_COLOR

        u_str = U_VALUE.strip()
        v_str = V_VALUE.strip()
        if not u_str or not v_str:
            raise ValueError("U_VALUE and V_VALUE must not be empty")
        if not u_str.isdigit() or not v_str.isdigit():
            raise ValueError("This visualization currently supports decimal digits only")

        u = string_to_little_endian(u_str)
        v = string_to_little_endian(v_str)
        result, steps = karatsuba_steps(u, v, BASE)
        result_str = little_endian_to_string(result)

        header = self.make_header(u_str, v_str)
        self.play(FadeIn(header, shift=DOWN * 0.2), run_time=0.8)

        intro = Text(
            "One step on screen at a time. Each step fades out before the next one.",
            font_size=20,
            color=TEXT_DIM,
        )
        intro.next_to(header, DOWN, buff=0.28)
        self.play(FadeIn(intro, shift=UP * 0.1), run_time=0.55)
        self.wait(0.6)
        self.play(FadeOut(intro, shift=UP * 0.1), run_time=0.35)

        current = None
        total = len(steps)
        for index, step in enumerate(steps, start=1):
            view = self.build_step_view(step, index, total)
            current = self.transition_to(current, view)
            self.wait(STEP_HOLD_TIME)

        final_view = self.make_final_view(u_str, v_str, result_str)
        self.play(
            FadeOut(current, shift=UP * TRANSITION_SHIFT),
            FadeIn(final_view, shift=DOWN * TRANSITION_SHIFT),
            run_time=0.7,
        )
        self.wait(2.0)


class KaratsubaStepByStepScene(MultiplicationScene):
    pass
