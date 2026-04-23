from manimlib import *


# ============================================================
# Editable inputs
# ============================================================
U_VALUE = "12345678"
V_VALUE = "87654321"
BASE = 10

# Timing
INTRO_WAIT = 0.5
STEP_IN_TIME = 0.4
STEP_OUT_TIME = 0.28
STEP_HOLD = 0.38
ITEM_TIME = 0.45
FINAL_WAIT = 2.0

# Palette
BG_COLOR = "#0b1020"
SURFACE = "#10182b"
SURFACE_2 = "#15203a"
SURFACE_3 = "#0f1729"
LINE_SOFT = "#73809d"
TEXT_MAIN = WHITE
TEXT_DIM = GREY_B
TEXT_FAINT = GREY_C
ACCENT_A = "#64d2ff"
ACCENT_B = "#6ef3a5"
ACCENT_SPLIT = "#b388ff"
ACCENT_SUM = "#ffb84d"
ACCENT_BASE = "#40e0a8"
ACCENT_COMBINE = "#ff7ac6"
ACCENT_RETURN = "#ff8a80"
ACCENT_RESULT = "#ffd54f"
ACCENT_INFO = "#8ec5ff"


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
        raise ValueError(f"Input must contain only decimal digits, got {num_str!r}")
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
# Layout helpers
# ============================================================
def fit_width(mobj, width):
    if mobj.get_width() > width:
        mobj.set_width(width)
    return mobj


def fit_height(mobj, height):
    if mobj.get_height() > height:
        mobj.set_height(height)
    return mobj


def fit_box(mobj, max_width, max_height):
    fit_width(mobj, max_width)
    fit_height(mobj, max_height)
    fit_width(mobj, max_width)
    return mobj


def short_label(label, keep=18):
    if len(label) <= keep:
        return label
    return "..." + label[-keep:]


def accent_for_step(step_type):
    return {
        "call": ACCENT_INFO,
        "split": ACCENT_SPLIT,
        "sum_parts": ACCENT_SUM,
        "base_case": ACCENT_BASE,
        "combine_parts": ACCENT_COMBINE,
        "return": ACCENT_RETURN,
    }[step_type]


class KaratsubaCleanLayoutScene(Scene):
    STAGE_W = 11.6
    STAGE_H = 5.0
    CONTENT_W = 9.7
    CONTENT_H = 3.2

    def make_pill(self, text, color, font_size=18, fill=SURFACE_2):
        label = Text(text, font_size=font_size, color=color)
        frame = RoundedRectangle(
            corner_radius=0.14,
            width=label.get_width() + 0.34,
            height=label.get_height() + 0.22,
            stroke_color=color,
            stroke_width=1.5,
            fill_color=fill,
            fill_opacity=1,
        )
        label.move_to(frame.get_center())
        return VGroup(frame, label)

    def make_value_box(self, title, value, color, width=2.3, height=1.1, value_font_size=28):
        frame = RoundedRectangle(
            corner_radius=0.16,
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2,
            fill_color=SURFACE_2,
            fill_opacity=1,
        )
        title_m = Text(title, font_size=16, color=TEXT_DIM)
        value_m = Text(str(value), font_size=value_font_size, color=color)
        fit_width(value_m, width - 0.35)
        group = VGroup(title_m, value_m).arrange(DOWN, buff=0.07)
        fit_box(group, width - 0.25, height - 0.18)
        group.move_to(frame.get_center())
        return VGroup(frame, group)

    def make_stage(self):
        outer = RoundedRectangle(
            corner_radius=0.22,
            width=self.STAGE_W,
            height=self.STAGE_H,
            stroke_color=LINE_SOFT,
            stroke_width=1.8,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        outer.move_to([0, -0.55, 0])
        return outer

    def make_header(self, a_str, b_str):
        title = Text("Karatsuba Multiplication", font_size=34, color=TEXT_MAIN)
        subtitle = Text("clean single-step layout", font_size=18, color=TEXT_DIM)
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.07, aligned_edge=LEFT)

        a_box = self.make_value_box("A", a_str, ACCENT_A, width=3.0, value_font_size=30)
        b_box = self.make_value_box("B", b_str, ACCENT_B, width=3.0, value_font_size=30)
        times = Text("×", font_size=32, color=LINE_SOFT)
        row = VGroup(a_box, times, b_box).arrange(RIGHT, buff=0.24, aligned_edge=DOWN)

        header = VGroup(title_block, row).arrange(DOWN, buff=0.22)
        header.to_edge(UP, buff=0.38)
        return header

    def make_meta_row(self, step, index, total, color):
        kind = self.make_pill(step["type"].replace("_", " ").upper(), color, font_size=17)
        depth = self.make_pill(f"depth {step['depth']}", TEXT_DIM, font_size=16)
        label = self.make_pill(short_label(step["label"]), TEXT_FAINT, font_size=15, fill=SURFACE_3)
        idx = self.make_pill(f"{index}/{total}", LINE_SOFT, font_size=16)
        row = VGroup(kind, depth, label, idx).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        fit_width(row, self.CONTENT_W)
        return row

    def make_formula_line(self, latex, color_map=None, scale_value=0.74):
        tex = Tex(latex, color=TEXT_MAIN, tex_to_color_map=color_map or {})
        tex.scale(scale_value)
        return tex

    def make_text_line(self, text, font_size=26, color=TEXT_MAIN):
        return Text(text, font_size=font_size, color=color)

    def make_content_stack(self, *items):
        safe_items = []
        for item in items:
            if item is None:
                continue
            fit_box(item, self.CONTENT_W, 1.35)
            safe_items.append(item)
        content = VGroup(*safe_items)
        if len(safe_items) == 0:
            return content
        content.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        fit_box(content, self.CONTENT_W, self.CONTENT_H)
        return content

    def build_step_view(self, step, index, total, title_text, color, *content_items):
        panel = self.make_stage()
        meta = self.make_meta_row(step, index, total, color)
        meta.move_to(panel.get_top() + DOWN * 0.36)

        title = self.make_text_line(title_text, font_size=30, color=TEXT_MAIN)
        fit_width(title, self.CONTENT_W)
        title.move_to(panel.get_center() + UP * 1.5)

        divider = Line(
            panel.get_left() + RIGHT * 0.45 + UP * 0.95,
            panel.get_right() + LEFT * 0.45 + UP * 0.95,
            color=SURFACE_2,
            stroke_width=2,
        )

        content = self.make_content_stack(*content_items)
        content.move_to(panel.get_center() + DOWN * 0.35)

        return VGroup(panel, meta, title, divider, content)

    def swap_stage(self, old_group, new_group):
        if old_group is None:
            self.play(FadeIn(new_group, shift=DOWN * 0.12), run_time=STEP_IN_TIME)
        else:
            self.play(
                FadeOut(old_group, shift=UP * 0.12),
                FadeIn(new_group, shift=DOWN * 0.12),
                run_time=STEP_IN_TIME,
            )
        return new_group

    def play_call_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        expr = self.make_text_line(f"{step['a']} × {step['b']}", font_size=48, color=color)
        hint = self.make_text_line("Check size: split again or finish directly.", font_size=22, color=TEXT_DIM)
        view = self.build_step_view(step, index, total, "Enter recursive call", color, expr, hint)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def play_base_case_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        row = VGroup(
            self.make_value_box("left", step["a"], ACCENT_A, width=2.1),
            Text("×", font_size=28, color=LINE_SOFT),
            self.make_value_box("right", step["b"], ACCENT_B, width=2.1),
            Text("=", font_size=28, color=LINE_SOFT),
            self.make_value_box("product", step["result"], color, width=2.6),
        ).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        fit_width(row, self.CONTENT_W)

        hint = self.make_text_line("This branch is small enough for direct multiplication.", font_size=21, color=TEXT_DIM)
        view = self.build_step_view(step, index, total, "Base case", color, row, hint)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD + 0.05)
        return current

    def play_return_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        bubble = RoundedRectangle(
            corner_radius=0.18,
            width=5.4,
            height=1.5,
            stroke_color=color,
            stroke_width=2,
            fill_color=SURFACE_2,
            fill_opacity=1,
        )
        label = self.make_text_line(short_label(step["label"], keep=24), font_size=20, color=TEXT_DIM)
        value = self.make_text_line(step["result"], font_size=36, color=color)
        bubble_content = VGroup(label, value).arrange(DOWN, buff=0.06)
        fit_box(bubble_content, 4.9, 1.15)
        bubble_content.move_to(bubble.get_center())
        bubble_group = VGroup(bubble, bubble_content)

        note = self.make_text_line("Send this result back to the parent frame.", font_size=21, color=TEXT_DIM)
        view = self.build_step_view(step, index, total, "Return", color, bubble_group, note)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def play_sum_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        eq1 = self.make_formula_line(
            rf"a_0 + a_1 = {step['a0']} + {step['a1']} = {step['sum_a']}",
            {step['sum_a']: ACCENT_A},
            0.84,
        )
        eq2 = self.make_formula_line(
            rf"b_0 + b_1 = {step['b0']} + {step['b1']} = {step['sum_b']}",
            {step['sum_b']: ACCENT_B},
            0.84,
        )
        target = self.make_value_box("next recursive call", f"{step['sum_a']} × {step['sum_b']}", color, width=5.2, value_font_size=26)
        view = self.build_step_view(step, index, total, "Build the middle product", color, eq1, eq2, target)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def play_split_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        top_row = VGroup(
            self.make_value_box("A", step["a"], ACCENT_A, width=2.9),
            self.make_pill(f"m = {step['m']}", color, font_size=18),
            self.make_value_box("B", step["b"], ACCENT_B, width=2.9),
        ).arrange(RIGHT, buff=0.24, aligned_edge=DOWN)
        fit_width(top_row, self.CONTENT_W)

        split_a = VGroup(
            self.make_value_box("A1", step["a1"], ACCENT_A, width=2.0),
            Text("|", font_size=26, color=LINE_SOFT),
            self.make_value_box("A0", step["a0"], ACCENT_A, width=2.0),
        ).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
        split_b = VGroup(
            self.make_value_box("B1", step["b1"], ACCENT_B, width=2.0),
            Text("|", font_size=26, color=LINE_SOFT),
            self.make_value_box("B0", step["b0"], ACCENT_B, width=2.0),
        ).arrange(RIGHT, buff=0.14, aligned_edge=DOWN)
        split_row = VGroup(split_a, split_b).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        fit_width(split_row, self.CONTENT_W)

        formula = self.make_formula_line(
            rf"A = A_1 \cdot 10^{{{step['m']}}} + A_0,\quad B = B_1 \cdot 10^{{{step['m']}}} + B_0",
            {"A_1": ACCENT_A, "A_0": ACCENT_A, "B_1": ACCENT_B, "B_0": ACCENT_B},
            0.76,
        )

        view = self.build_step_view(step, index, total, "Split into high and low parts", color, top_row, split_row, formula)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def play_combine_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        z_row = VGroup(
            self.make_value_box("z2", step["z2"], ACCENT_A, width=2.2),
            self.make_value_box("z1raw", step["z1_raw"], ACCENT_SUM, width=2.2),
            self.make_value_box("z0", step["z0"], ACCENT_B, width=2.2),
        ).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        fit_width(z_row, self.CONTENT_W)

        fix = self.make_formula_line(
            rf"z_1 = z_{{1raw}} - z_2 - z_0 = {step['z1']}",
            {r"z_1": color, r"z_{1raw}": ACCENT_SUM, r"z_2": ACCENT_A, r"z_0": ACCENT_B, step['z1']: color},
            0.82,
        )
        combine = self.make_formula_line(
            rf"result = z_2 \cdot 10^{{{2 * step['m']}}} + z_1 \cdot 10^{{{step['m']}}} + z_0",
            {r"z_2": ACCENT_A, r"z_1": color, r"z_0": ACCENT_B},
            0.76,
        )
        view = self.build_step_view(step, index, total, "Combine recursive results", color, z_row, fix, combine)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def make_final_view(self, a_str, b_str, result_str):
        panel = RoundedRectangle(
            corner_radius=0.24,
            width=self.STAGE_W,
            height=self.STAGE_H,
            stroke_color=ACCENT_RESULT,
            stroke_width=2.2,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        panel.move_to([0, -0.55, 0])

        title = self.make_text_line("Final result", font_size=34, color=TEXT_MAIN)
        title.move_to(panel.get_center() + UP * 1.5)

        row = VGroup(
            self.make_value_box("A", a_str, ACCENT_A, width=2.7),
            Text("×", font_size=30, color=LINE_SOFT),
            self.make_value_box("B", b_str, ACCENT_B, width=2.7),
            Text("=", font_size=30, color=LINE_SOFT),
            self.make_value_box("A × B", result_str, ACCENT_RESULT, width=3.4),
        ).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        fit_width(row, self.CONTENT_W)
        row.move_to(panel.get_center() + UP * 0.2)

        verify = self.make_text_line(f"check: {a_str} × {b_str} = {result_str}", font_size=21, color=TEXT_DIM)
        fit_width(verify, self.CONTENT_W)
        verify.move_to(panel.get_center() + DOWN * 1.45)
        return VGroup(panel, title, row, verify)

    def construct(self):
        self.camera.background_color = BG_COLOR

        a_str = U_VALUE.strip()
        b_str = V_VALUE.strip()
        if not a_str or not b_str:
            raise ValueError("U_VALUE and V_VALUE must not be empty")
        if not a_str.isdigit() or not b_str.isdigit():
            raise ValueError("This visualization currently supports decimal digits only")

        a = string_to_little_endian(a_str)
        b = string_to_little_endian(b_str)
        result, steps = karatsuba_steps(a, b, BASE)
        result_str = little_endian_to_string(result)

        header = self.make_header(a_str, b_str)
        self.play(FadeIn(header, shift=DOWN * 0.18), run_time=0.75)

        intro = self.make_pill("bounded layout: one step, one card, no overlap", ACCENT_INFO, font_size=17)
        intro.next_to(header, DOWN, buff=0.25)
        self.play(FadeIn(intro, shift=UP * 0.08), run_time=0.4)
        self.wait(INTRO_WAIT)
        self.play(FadeOut(intro, shift=UP * 0.08), run_time=0.25)

        current = None
        total = len(steps)
        for index, step in enumerate(steps, start=1):
            step_type = step["type"]
            if step_type == "call":
                current = self.play_call_step(current, step, index, total)
            elif step_type == "split":
                current = self.play_split_step(current, step, index, total)
            elif step_type == "sum_parts":
                current = self.play_sum_step(current, step, index, total)
            elif step_type == "base_case":
                current = self.play_base_case_step(current, step, index, total)
            elif step_type == "combine_parts":
                current = self.play_combine_step(current, step, index, total)
            elif step_type == "return":
                current = self.play_return_step(current, step, index, total)

        final_view = self.make_final_view(a_str, b_str, result_str)
        self.play(
            FadeOut(current, shift=UP * 0.12),
            FadeIn(final_view, shift=DOWN * 0.12),
            run_time=0.6,
        )
        self.wait(FINAL_WAIT)


class MultiplicationScene(KaratsubaCleanLayoutScene):
    pass


class KaratsubaUltraBeautifulScene(KaratsubaCleanLayoutScene):
    pass


class KaratsubaBeautifulScene(KaratsubaCleanLayoutScene):
    pass
