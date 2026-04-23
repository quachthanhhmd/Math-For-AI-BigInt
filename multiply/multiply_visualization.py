from manimlib import *


# =========================
# Numeric helpers
# =========================
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
        raise ValueError(f"Input must contain only digits, got: {num_str!r}")
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


# =========================
# Karatsuba trace generator
# =========================
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
        "m": m,
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


# =========================
# Scene
# =========================
class MultiplicationScene(Scene):
    WINDOW_SIZE = 6

    def construct(self):
        u_str = "12345678"
        v_str = "87654321"

        u = string_to_little_endian(u_str)
        v = string_to_little_endian(v_str)
        result, steps = karatsuba_steps(u, v)

        self.camera.background_color = "#0F1117"

        header = self.build_header(u_str, v_str)
        legend = self.build_legend()
        panel = self.build_window_panel()
        formula_card = self.build_formula_card()
        footer = self.build_footer(little_endian_to_string(result))

        self.play(FadeIn(header, shift=DOWN), FadeIn(legend, shift=LEFT))
        self.play(FadeIn(panel, shift=UP), FadeIn(formula_card, shift=RIGHT))

        visible_cards = []

        for idx, step in enumerate(steps, start=1):
            step_card = self.build_step_card(step, idx, len(steps))
            self.push_step_into_window(step_card, visible_cards, panel)
            self.update_formula_card(formula_card, step)
            self.wait(0.2)

        self.play(FadeIn(footer, shift=UP))
        self.wait(2)

    # ---------- Layout ----------
    def build_header(self, u_str, v_str):
        title = Text("Karatsuba Multiplication", font_size=38, color=BLUE_B)
        subtitle = Text(
            f"Input: {u_str} × {v_str}",
            font_size=24,
            color=GREY_A,
        )
        text_group = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        box = RoundedRectangle(
            corner_radius=0.18,
            height=1.25,
            width=12.8,
            stroke_color=GREY_B,
            stroke_width=1.5,
            fill_color="#171A21",
            fill_opacity=1,
        )
        text_group.move_to(box.get_center())
        text_group.align_to(box, LEFT).shift(RIGHT * 0.35)

        group = VGroup(box, text_group)
        group.to_edge(UP, buff=0.2)
        return group

    def build_legend(self):
        legend_title = Text("Step types", font_size=22, color=GREY_A)
        entries = VGroup(
            self.legend_row(BLUE_B, "Call / recursion entry"),
            self.legend_row(TEAL_B, "Split operands"),
            self.legend_row(GREEN_B, "Compute sums"),
            self.legend_row(ORANGE, "Base-case multiply"),
            self.legend_row(PURPLE_B, "Combine z0, z1, z2"),
            self.legend_row(YELLOW_B, "Return result"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        body = VGroup(legend_title, entries).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        frame = RoundedRectangle(
            corner_radius=0.16,
            height=3.15,
            width=3.5,
            stroke_color=GREY_B,
            stroke_width=1.2,
            fill_color="#151821",
            fill_opacity=1,
        )
        body.move_to(frame.get_center())
        body.align_to(frame, LEFT).shift(RIGHT * 0.25)
        group = VGroup(frame, body)
        group.to_corner(UL, buff=0.45)
        group.shift(DOWN * 1.15)
        return group

    def legend_row(self, color, text):
        dot = Dot(radius=0.06, color=color)
        label = Text(text, font_size=17, color=GREY_A)
        return VGroup(dot, label).arrange(RIGHT, buff=0.12)

    def build_window_panel(self):
        panel = RoundedRectangle(
            corner_radius=0.18,
            height=5.55,
            width=8.1,
            stroke_color=GREY_B,
            stroke_width=1.4,
            fill_color="#12151C",
            fill_opacity=1,
        )
        panel.to_edge(LEFT, buff=3.8)
        panel.shift(DOWN * 0.85)

        title = Text("Sliding window of recent steps", font_size=24, color=GREY_A)
        title.next_to(panel.get_top(), DOWN, buff=0.16)
        title.align_to(panel, LEFT)
        title.shift(RIGHT * 0.22)

        self.add(panel, title)
        return panel

    def build_formula_card(self):
        frame = RoundedRectangle(
            corner_radius=0.18,
            height=5.55,
            width=4.25,
            stroke_color=GREY_B,
            stroke_width=1.4,
            fill_color="#12151C",
            fill_opacity=1,
        )
        frame.to_edge(RIGHT, buff=0.45)
        frame.shift(DOWN * 0.85)

        title = Text("Current focus", font_size=24, color=GREY_A)
        title.next_to(frame.get_top(), DOWN, buff=0.16)
        title.align_to(frame, LEFT)
        title.shift(RIGHT * 0.22)

        headline = Text("Waiting for step...", font_size=22, color=WHITE)
        headline.move_to(frame.get_center() + UP * 1.2)

        body = Text("Karatsuba splits, recurses, then combines.", font_size=20, color=GREY_A)
        body.set_width(3.6)
        body.move_to(frame.get_center())

        formula = Text("z = z2·B^(2m) + z1·B^m + z0", font_size=21, color=BLUE_B)
        formula.set_width(3.7)
        formula.move_to(frame.get_center() + DOWN * 1.35)

        group = VGroup(frame, title, headline, body, formula)
        group.meta_headline = headline
        group.meta_body = body
        group.meta_formula = formula
        return group

    def build_footer(self, result_text):
        frame = RoundedRectangle(
            corner_radius=0.18,
            height=0.95,
            width=12.4,
            stroke_color=YELLOW_B,
            stroke_width=1.6,
            fill_color="#221B10",
            fill_opacity=1,
        )
        frame.to_edge(DOWN, buff=0.25)

        text = Text(
            f"Final result = {result_text}",
            font_size=30,
            color=YELLOW_B,
        )
        text.move_to(frame.get_center())
        return VGroup(frame, text)

    # ---------- Step rendering ----------
    def build_step_card(self, step, idx, total):
        color = self.color_for_step(step["type"])
        text_lines = self.describe_step(step)

        badge = Text(f"{idx}/{total}", font_size=16, color=GREY_A)
        tag = Text(step["type"].upper(), font_size=16, color=color)
        depth = Text(f"depth={step.get('depth', 0)}", font_size=16, color=GREY_A)
        top_row = VGroup(tag, depth, badge).arrange(RIGHT, buff=0.25)

        body_items = [Text(line, font_size=18, color=WHITE) for line in text_lines]
        body = VGroup(*body_items).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        body.set_width(6.7)

        card = RoundedRectangle(
            corner_radius=0.12,
            height=max(0.78, 0.46 + 0.34 * (len(text_lines) + 1)),
            width=7.35,
            stroke_color=color,
            stroke_width=1.6,
            fill_color="#1A1F29",
            fill_opacity=1,
        )

        content = VGroup(top_row, body).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        content.move_to(card.get_center())
        content.align_to(card, LEFT).shift(RIGHT * 0.2)

        return VGroup(card, content)

    def push_step_into_window(self, new_card, visible_cards, panel):
        anchor_x = panel.get_center()[0]
        base_top = panel.get_top()[1] - 0.65
        spacing = 0.12

        new_card.move_to([anchor_x, base_top, 0])
        new_card.align_to(panel, LEFT)
        new_card.shift(RIGHT * 0.35)

        animations = []
        if len(visible_cards) < self.WINDOW_SIZE:
            target_y = self.compute_y_positions(panel, len(visible_cards) + 1)[-1]
            new_card.move_to([anchor_x, target_y + 0.3, 0])
            new_card.align_to(panel, LEFT)
            new_card.shift(RIGHT * 0.35)
            animations.append(FadeIn(new_card, shift=UP * 0.2))
            visible_cards.append(new_card)
        else:
            old_first = visible_cards.pop(0)
            animations.append(FadeOut(old_first, shift=UP * 0.2))
            visible_cards.append(new_card)
            animations.append(FadeIn(new_card, shift=DOWN * 0.2))

        y_positions = self.compute_y_positions(panel, len(visible_cards))
        for mob, y in zip(visible_cards, y_positions):
            animations.append(mob.animate.move_to([anchor_x, y, 0]).align_to(panel, LEFT).shift(RIGHT * 0.35))

        self.play(*animations, run_time=0.45)

    def compute_y_positions(self, panel, count):
        top_y = panel.get_top()[1] - 0.72
        positions = []
        current_y = top_y
        for _ in range(count):
            positions.append(current_y)
            current_y -= 0.82
        return positions

    def update_formula_card(self, formula_card, step):
        headline_text, body_text, formula_text = self.focus_copy(step)

        new_headline = Text(headline_text, font_size=22, color=self.color_for_step(step["type"]))
        new_headline.move_to(formula_card.meta_headline)
        new_headline.set_width(3.6)

        new_body = Text(body_text, font_size=20, color=GREY_A)
        new_body.set_width(3.6)
        new_body.move_to(formula_card.meta_body)

        new_formula = Text(formula_text, font_size=21, color=BLUE_B)
        new_formula.set_width(3.7)
        new_formula.move_to(formula_card.meta_formula)

        self.play(
            Transform(formula_card.meta_headline, new_headline),
            Transform(formula_card.meta_body, new_body),
            Transform(formula_card.meta_formula, new_formula),
            run_time=0.28,
        )

    # ---------- Content helpers ----------
    def color_for_step(self, step_type):
        return {
            "call": BLUE_B,
            "split": TEAL_B,
            "sum_parts": GREEN_B,
            "base_case": ORANGE,
            "combine_parts": PURPLE_B,
            "return": YELLOW_B,
        }.get(step_type, GREY_B)

    def describe_step(self, step):
        step_type = step["type"]
        if step_type == "call":
            return [
                f"Label: {step['label']}",
                f"Multiply {step['a']} × {step['b']}",
            ]
        if step_type == "split":
            return [
                f"m = {step['m']}",
                f"a = a1|a0 = {step['a1']} | {step['a0']}",
                f"b = b1|b0 = {step['b1']} | {step['b0']}",
            ]
        if step_type == "sum_parts":
            return [
                f"a0 + a1 = {step['sum_a']}",
                f"b0 + b1 = {step['sum_b']}",
                "Prepare raw middle product",
            ]
        if step_type == "base_case":
            return [
                f"Direct multiply at {step['label']}",
                f"result = {step['result']}",
            ]
        if step_type == "combine_parts":
            return [
                f"z0 = {step['z0']}",
                f"z1 = {step['z1']}",
                f"z2 = {step['z2']}",
                f"Assemble with m = {step['m']}",
            ]
        return [
            f"Return from {step['label']}",
            f"result = {step['result']}",
        ]

    def focus_copy(self, step):
        step_type = step["type"]
        if step_type == "call":
            return (
                "Enter recursion",
                f"Work on subproblem {step['label']}: {step['a']} × {step['b']}",
                "Recurse until size <= 2",
            )
        if step_type == "split":
            return (
                "Split inputs",
                f"Break each number into low/high halves with m = {step['m']}",
                "a = a1·B^m + a0,  b = b1·B^m + b0",
            )
        if step_type == "sum_parts":
            return (
                "Build middle term",
                "Add halves first, then recurse on (a0+a1)(b0+b1)",
                "z1 = z1raw - z2 - z0",
            )
        if step_type == "base_case":
            return (
                "Base case",
                f"Small enough to multiply directly at {step['label']}",
                f"result = {step['result']}",
            )
        if step_type == "combine_parts":
            return (
                "Combine subproducts",
                "Merge low, middle, and high contributions into one value",
                "z = z2·B^(2m) + z1·B^m + z0",
            )
        return (
            "Propagate upward",
            f"Subproblem {step['label']} finishes with result {step['result']}",
            "Return to caller",
        )


# Optional alias if the render command expects a different class name.
class KaratsubaScene(MultiplicationScene):
    pass
