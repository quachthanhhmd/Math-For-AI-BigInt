from manimlib import *


# ============================================================
# Editable inputs
# ============================================================
U_VALUE = "12345678"
V_VALUE = "87654321"
BASE = 10

# Timing
INTRO_WAIT = 0.6
STEP_IN_TIME = 0.45
STEP_OUT_TIME = 0.3
STEP_HOLD = 0.4
INTERNAL_TIME = 0.55
FINAL_WAIT = 2.2

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



def short_label(label, keep=20):
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


class KaratsubaUltraBeautifulScene(Scene):
    def make_pill(self, text, color, font_size=18, fill=SURFACE_2):
        label = Text(text, font_size=font_size, color=color)
        frame = RoundedRectangle(
            corner_radius=0.14,
            width=label.get_width() + 0.36,
            height=label.get_height() + 0.24,
            stroke_color=color,
            stroke_width=1.6,
            fill_color=fill,
            fill_opacity=1,
        )
        label.move_to(frame.get_center())
        return VGroup(frame, label)

    def make_value_box(self, title, value, color, width=2.7, height=1.28, value_font_size=30):
        frame = RoundedRectangle(
            corner_radius=0.16,
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2,
            fill_color=SURFACE_2,
            fill_opacity=1,
        )
        title_m = Text(title, font_size=18, color=TEXT_DIM)
        value_m = Text(str(value), font_size=value_font_size, color=color)
        fit_width(value_m, width - 0.4)
        group = VGroup(title_m, value_m).arrange(DOWN, buff=0.12)
        group.move_to(frame.get_center())
        return VGroup(frame, group)

    def make_stage(self):
        outer = RoundedRectangle(
            corner_radius=0.22,
            width=11.9,
            height=5.15,
            stroke_color=LINE_SOFT,
            stroke_width=1.8,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        outer.move_to([0, -0.55, 0])
        return outer

    def make_header(self, a_str, b_str):
        title = Text("Karatsuba Multiplication", font_size=34, color=TEXT_MAIN)
        subtitle = Text("cinematic recursive walkthrough", font_size=18, color=TEXT_DIM)
        title_block = VGroup(title, subtitle).arrange(DOWN, buff=0.08, aligned_edge=LEFT)

        a_box = self.make_value_box("multiplicand A", a_str, ACCENT_A, width=3.35, value_font_size=32)
        b_box = self.make_value_box("multiplier B", b_str, ACCENT_B, width=3.35, value_font_size=32)
        times = Text("×", font_size=34, color=LINE_SOFT)
        row = VGroup(a_box, times, b_box).arrange(RIGHT, buff=0.28, aligned_edge=DOWN)

        header = VGroup(title_block, row).arrange(DOWN, buff=0.28)
        header.to_edge(UP, buff=0.38)
        return header

    def make_meta_row(self, step, index, total, color):
        kind = self.make_pill(step["type"].replace("_", " ").upper(), color, font_size=18)
        depth = self.make_pill(f"depth {step['depth']}", TEXT_DIM, font_size=17)
        idx = self.make_pill(f"{index}/{total}", LINE_SOFT, font_size=17)
        label = self.make_pill(short_label(step["label"]), TEXT_FAINT, font_size=16, fill=SURFACE_3)
        row = VGroup(kind, depth, label, idx).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        fit_width(row, 10.8)
        return row

    def make_formula_line(self, latex, color_map=None, scale_value=0.72):
        tex = Tex(latex, color=TEXT_MAIN, tex_to_color_map=color_map or {})
        tex.scale(scale_value)
        return tex

    def swap_stage(self, old_group, new_group):
        if old_group is None:
            self.play(FadeIn(new_group, shift=DOWN * 0.14), run_time=STEP_IN_TIME)
            return new_group
        self.play(
            FadeOut(old_group, shift=UP * 0.14),
            FadeIn(new_group, shift=DOWN * 0.14),
            run_time=STEP_IN_TIME,
        )
        return new_group

    def build_generic_shell(self, step, index, total, title_text, color):
        panel = self.make_stage()
        meta = self.make_meta_row(step, index, total, color)
        meta.move_to(panel.get_top() + DOWN * 0.38)
        title = Text(title_text, font_size=31, color=TEXT_MAIN)
        fit_width(title, 10.2)
        title.move_to(panel.get_center() + UP * 1.45)
        divider = Line(
            panel.get_left() + RIGHT * 0.45 + UP * 0.95,
            panel.get_right() + LEFT * 0.45 + UP * 0.95,
            color=SURFACE_2,
            stroke_width=2,
        )
        shell = VGroup(panel, meta, title, divider)
        return shell, panel, title

    def play_call_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Enter recursive call", color)

        expr = Text(f"{step['a']} × {step['b']}", font_size=52, color=color)
        fit_width(expr, 8.8)
        expr.move_to(panel.get_center() + UP * 0.15)

        hint = Text("Decide whether to split or use the base case.", font_size=21, color=TEXT_DIM)
        fit_width(hint, 9.5)
        hint.move_to(panel.get_center() + DOWN * 1.25)

        view = VGroup(shell, expr, hint)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD)
        return current

    def play_base_case_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Base case: multiply directly", color)

        left = self.make_value_box("left", step["a"], ACCENT_A, width=2.2, value_font_size=28)
        right = self.make_value_box("right", step["b"], ACCENT_B, width=2.2, value_font_size=28)
        product = self.make_value_box("product", step["result"], color, width=2.9, value_font_size=30)
        times = Text("×", font_size=30, color=LINE_SOFT)
        equals = Text("=", font_size=30, color=LINE_SOFT)
        row = VGroup(left, times, right, equals, product).arrange(RIGHT, buff=0.24, aligned_edge=DOWN)
        fit_width(row, 9.8)
        row.move_to(panel.get_center() + UP * 0.15)

        note = Text("Numbers are small enough, so schoolbook multiplication finishes this branch.", font_size=20, color=TEXT_DIM)
        fit_width(note, 9.8)
        note.move_to(panel.get_center() + DOWN * 1.3)

        view = VGroup(shell, row, note)
        current = self.swap_stage(current, view)
        self.wait(STEP_HOLD + 0.1)
        return current

    def play_return_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Return to parent call", color)

        bubble = RoundedRectangle(
            corner_radius=0.18,
            width=6.0,
            height=1.5,
            stroke_color=color,
            stroke_width=2,
            fill_color=SURFACE_2,
            fill_opacity=1,
        )
        bubble.move_to(panel.get_center() + UP * 0.2)
        label = Text(short_label(step["label"], keep=26), font_size=22, color=TEXT_DIM)
        value = Text(step["result"], font_size=36, color=color)
        fit_width(value, 4.8)
        content = VGroup(label, value).arrange(DOWN, buff=0.08).move_to(bubble.get_center())
        arrow = Arrow(
            bubble.get_top() + UP * 0.05,
            bubble.get_top() + UP * 0.8,
            buff=0.05,
            color=color,
            stroke_width=4,
        )
        note = Text("Computed value bubbles upward and becomes available to the previous frame.", font_size=20, color=TEXT_DIM)
        fit_width(note, 9.8)
        note.move_to(panel.get_center() + DOWN * 1.35)

        view = VGroup(shell, bubble, content, arrow, note)
        current = self.swap_stage(current, view)
        self.play(GrowArrow(arrow), run_time=INTERNAL_TIME * 0.75)
        self.wait(STEP_HOLD)
        return current

    def play_sum_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Build the middle product", color)

        left_eq = self.make_formula_line(
            rf"a_0 + a_1 = {step['a0']} + {step['a1']} = {step['sum_a']}",
            {step['sum_a']: ACCENT_A},
            0.88,
        )
        right_eq = self.make_formula_line(
            rf"b_0 + b_1 = {step['b0']} + {step['b1']} = {step['sum_b']}",
            {step['sum_b']: ACCENT_B},
            0.88,
        )
        target = self.make_value_box("recursive target", f"{step['sum_a']} × {step['sum_b']}", color, width=5.4, value_font_size=28)

        left_eq.move_to(panel.get_center() + UP * 0.55)
        right_eq.move_to(panel.get_center() + DOWN * 0.05)
        target.move_to(panel.get_center() + DOWN * 1.25)

        view = VGroup(shell, left_eq, right_eq, target)
        current = self.swap_stage(current, view)
        self.play(FadeIn(left_eq, shift=RIGHT * 0.08), run_time=INTERNAL_TIME * 0.8)
        self.play(FadeIn(right_eq, shift=RIGHT * 0.08), run_time=INTERNAL_TIME * 0.8)
        self.play(FadeIn(target, shift=UP * 0.08), run_time=INTERNAL_TIME)
        self.wait(STEP_HOLD)
        return current

    def play_split_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Split into high and low halves", color)

        a_full = self.make_value_box("A", step["a"], ACCENT_A, width=3.25, value_font_size=32)
        b_full = self.make_value_box("B", step["b"], ACCENT_B, width=3.25, value_font_size=32)
        row = VGroup(a_full, b_full).arrange(RIGHT, buff=0.8)
        row.move_to(panel.get_center() + UP * 0.55)

        a_hi = self.make_value_box("A high", step["a1"], ACCENT_A, width=2.1, value_font_size=26)
        a_lo = self.make_value_box("A low", step["a0"], ACCENT_A, width=2.1, value_font_size=26)
        b_hi = self.make_value_box("B high", step["b1"], ACCENT_B, width=2.1, value_font_size=26)
        b_lo = self.make_value_box("B low", step["b0"], ACCENT_B, width=2.1, value_font_size=26)

        a_parts = VGroup(a_hi, a_lo).arrange(RIGHT, buff=0.18)
        b_parts = VGroup(b_hi, b_lo).arrange(RIGHT, buff=0.18)
        a_parts.move_to(panel.get_center() + LEFT * 2.7 + DOWN * 1.0)
        b_parts.move_to(panel.get_center() + RIGHT * 2.7 + DOWN * 1.0)

        a_arrow = Arrow(a_full.get_bottom(), a_parts.get_top() + UP * 0.12, buff=0.08, color=ACCENT_A, stroke_width=4)
        b_arrow = Arrow(b_full.get_bottom(), b_parts.get_top() + UP * 0.12, buff=0.08, color=ACCENT_B, stroke_width=4)

        split_note = Text(f"m = {step['m']}", font_size=22, color=color)
        split_note.move_to(panel.get_center() + DOWN * 0.25)

        formula_a = self.make_formula_line(
            rf"A = A_1 \cdot 10^{{{step['m']}}} + A_0",
            {"A_1": ACCENT_A, "A_0": ACCENT_A},
            0.84,
        )
        formula_b = self.make_formula_line(
            rf"B = B_1 \cdot 10^{{{step['m']}}} + B_0",
            {"B_1": ACCENT_B, "B_0": ACCENT_B},
            0.84,
        )
        formulas = VGroup(formula_a, formula_b).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        formulas.move_to(panel.get_center() + DOWN * 1.95)

        static_view = VGroup(shell, row, split_note)
        current = self.swap_stage(current, static_view)
        self.play(
            GrowArrow(a_arrow),
            GrowArrow(b_arrow),
            TransformFromCopy(a_full, a_parts),
            TransformFromCopy(b_full, b_parts),
            run_time=INTERNAL_TIME,
        )
        self.play(FadeIn(formulas, shift=UP * 0.08), run_time=INTERNAL_TIME * 0.9)
        current = VGroup(shell, row, split_note, a_arrow, b_arrow, a_parts, b_parts, formulas)
        self.wait(STEP_HOLD)
        return current

    def play_combine_step(self, current, step, index, total):
        color = accent_for_step(step["type"])
        shell, panel, _ = self.build_generic_shell(step, index, total, "Merge the three recursive products", color)

        z2_box = self.make_value_box("z2 = high×high", step["z2"], ACCENT_A, width=2.9, value_font_size=27)
        z1raw_box = self.make_value_box("z1raw", step["z1_raw"], ACCENT_SUM, width=2.4, value_font_size=27)
        z0_box = self.make_value_box("z0 = low×low", step["z0"], ACCENT_B, width=2.9, value_font_size=27)
        top_row = VGroup(z2_box, z1raw_box, z0_box).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        fit_width(top_row, 10.4)
        top_row.move_to(panel.get_center() + UP * 0.6)

        middle_fix = self.make_formula_line(
            rf"z_1 = z_{{1raw}} - z_2 - z_0 = {step['z1']}",
            {r"z_1": color, r"z_{1raw}": ACCENT_SUM, r"z_2": ACCENT_A, r"z_0": ACCENT_B, step['z1']: color},
            0.9,
        )
        middle_fix.move_to(panel.get_center() + DOWN * 0.35)

        final_formula = self.make_formula_line(
            rf"result = z_2\cdot 10^{{{2 * step['m']}}} + z_1\cdot 10^{{{step['m']}}} + z_0",
            {r"z_2": ACCENT_A, r"z_1": color, r"z_0": ACCENT_B},
            0.84,
        )
        final_formula.move_to(panel.get_center() + DOWN * 1.65)

        base_view = VGroup(shell, top_row)
        current = self.swap_stage(current, base_view)
        self.play(FadeIn(top_row, shift=UP * 0.08), run_time=INTERNAL_TIME * 0.9)
        self.play(TransformFromCopy(z1raw_box, middle_fix), run_time=INTERNAL_TIME)
        self.play(FadeIn(final_formula, shift=UP * 0.08), run_time=INTERNAL_TIME * 0.9)
        current = VGroup(shell, top_row, middle_fix, final_formula)
        self.wait(STEP_HOLD + 0.05)
        return current

    def make_final_view(self, a_str, b_str, result_str):
        panel = RoundedRectangle(
            corner_radius=0.24,
            width=11.8,
            height=5.2,
            stroke_color=ACCENT_RESULT,
            stroke_width=2.2,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        panel.move_to([0, -0.55, 0])

        title = Text("Final result", font_size=36, color=TEXT_MAIN)
        title.move_to(panel.get_center() + UP * 1.65)

        a_box = self.make_value_box("A", a_str, ACCENT_A, width=3.0, value_font_size=30)
        b_box = self.make_value_box("B", b_str, ACCENT_B, width=3.0, value_font_size=30)
        result_box = self.make_value_box("A × B", result_str, ACCENT_RESULT, width=4.1, value_font_size=32)
        times = Text("×", font_size=32, color=LINE_SOFT)
        equals = Text("=", font_size=32, color=LINE_SOFT)
        row = VGroup(a_box, times, b_box, equals, result_box).arrange(RIGHT, buff=0.24, aligned_edge=DOWN)
        fit_width(row, 10.6)
        row.move_to(panel.get_center() + UP * 0.25)

        verify = Text(f"check: {a_str} × {b_str} = {result_str}", font_size=22, color=TEXT_DIM)
        fit_width(verify, 9.8)
        verify.move_to(panel.get_center() + DOWN * 1.55)

        shimmer = Line(
            panel.get_left() + RIGHT * 0.65 + DOWN * 0.75,
            panel.get_right() + LEFT * 0.65 + DOWN * 0.75,
            color=ACCENT_RESULT,
            stroke_width=2,
        )

        return VGroup(panel, title, row, shimmer, verify)

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
        self.play(FadeIn(header, shift=DOWN * 0.18), run_time=0.8)

        intro_badge = self.make_pill("inspired by elegant long-division choreography", ACCENT_INFO, font_size=18)
        intro_badge.next_to(header, DOWN, buff=0.28)
        self.play(FadeIn(intro_badge, shift=UP * 0.08), run_time=0.45)
        self.wait(INTRO_WAIT)
        self.play(FadeOut(intro_badge, shift=UP * 0.08), run_time=0.25)

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
            FadeOut(current, shift=UP * 0.14),
            FadeIn(final_view, shift=DOWN * 0.14),
            run_time=0.7,
        )
        self.wait(FINAL_WAIT)


class MultiplicationScene(KaratsubaUltraBeautifulScene):
    pass


class KaratsubaBeautifulScene(KaratsubaUltraBeautifulScene):
    pass
