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


class MultiplicationScene(Scene):
    WINDOW_SIZE = 4
    CARD_W = 6.4
    CARD_H = 0.95

    def construct(self):
        u_str = "12345678"
        v_str = "87654321"

        u = string_to_little_endian(u_str)
        v = string_to_little_endian(v_str)
        result, steps = karatsuba_steps(u, v)

        self.camera.background_color = "#0E1116"

        header = self.build_header(u_str, v_str)
        legend = self.build_legend()
        window_group = self.build_window_panel()
        focus_group = self.build_focus_panel()
        footer = self.build_footer(little_endian_to_string(result))

        self.play(FadeIn(header, shift=DOWN))
        self.play(FadeIn(legend, shift=RIGHT), FadeIn(window_group, shift=UP), FadeIn(focus_group, shift=LEFT))

        panel = window_group.panel
        visible_cards = []

        for idx, step in enumerate(steps, start=1):
            card = self.build_step_card(step, idx, len(steps))
            self.push_step_into_window(card, visible_cards, panel)
            self.update_focus_panel(focus_group, step, idx, len(steps))
            self.wait(0.16)

        self.play(FadeIn(footer, shift=UP))
        self.wait(2)

    def build_header(self, u_str, v_str):
        box = RoundedRectangle(
            corner_radius=0.18,
            width=12.6,
            height=1.15,
            stroke_color=GREY_B,
            stroke_width=1.4,
            fill_color="#121722",
            fill_opacity=1,
        )
        box.to_edge(UP, buff=0.22)

        title = Text("Karatsuba Multiplication", font_size=30, color=WHITE)
        subtitle = Text(f"Input: {u_str} x {v_str}", font_size=21, color=GREY_A)
        text_group = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        text_group.move_to(box.get_center())
        text_group.align_to(box, LEFT).shift(RIGHT * 0.32)
        return VGroup(box, text_group)

    def build_legend(self):
        frame = RoundedRectangle(
            corner_radius=0.16,
            width=3.2,
            height=3.35,
            stroke_color=GREY_B,
            stroke_width=1.2,
            fill_color="#131823",
            fill_opacity=1,
        )
        frame.to_corner(UL, buff=0.38)
        frame.shift(DOWN * 1.52)

        title = Text("Step types", font_size=20, color=GREY_A)
        rows = VGroup(
            self.legend_row(BLUE_B, "Call"),
            self.legend_row(TEAL_B, "Split"),
            self.legend_row(GREEN_B, "Sum parts"),
            self.legend_row(ORANGE, "Base case"),
            self.legend_row(PURPLE_B, "Combine"),
            self.legend_row(YELLOW_B, "Return"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        body = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        body.move_to(frame.get_center())
        body.align_to(frame, LEFT).shift(RIGHT * 0.22)
        return VGroup(frame, body)

    def legend_row(self, color, label):
        dot = Dot(radius=0.045, color=color)
        text = Text(label, font_size=16, color=GREY_A)
        return VGroup(dot, text).arrange(RIGHT, buff=0.12)

    def build_window_panel(self):
        panel = RoundedRectangle(
            corner_radius=0.18,
            width=6.95,
            height=4.65,
            stroke_color=GREY_B,
            stroke_width=1.3,
            fill_color="#121722",
            fill_opacity=1,
        )
        panel.move_to(np.array([0.2, -0.95, 0]))

        title = Text("Recent steps", font_size=22, color=GREY_A)
        title.next_to(panel.get_top(), DOWN, buff=0.14)
        title.align_to(panel, LEFT).shift(RIGHT * 0.22)

        hint = Text("Sliding window", font_size=15, color=GREY_C)
        hint.next_to(title, RIGHT, buff=0.22)

        group = VGroup(panel, title, hint)
        group.panel = panel
        return group

    def build_focus_panel(self):
        frame = RoundedRectangle(
            corner_radius=0.18,
            width=3.75,
            height=4.65,
            stroke_color=GREY_B,
            stroke_width=1.3,
            fill_color="#121722",
            fill_opacity=1,
        )
        frame.to_edge(RIGHT, buff=0.45)
        frame.shift(DOWN * 0.95)

        title = Text("Current focus", font_size=22, color=GREY_A)
        title.next_to(frame.get_top(), DOWN, buff=0.14)
        title.align_to(frame, LEFT).shift(RIGHT * 0.22)

        headline = Text("Waiting", font_size=20, color=WHITE)
        headline.move_to(frame.get_center() + UP * 1.25)

        line1 = Text("A compact summary of", font_size=18, color=GREY_A)
        line2 = Text("the active step appears here.", font_size=18, color=GREY_A)
        body = VGroup(line1, line2).arrange(DOWN, buff=0.12)
        body.move_to(frame.get_center() + UP * 0.3)

        chip = RoundedRectangle(
            corner_radius=0.12,
            width=2.8,
            height=0.55,
            stroke_color=BLUE_B,
            stroke_width=1.2,
            fill_color="#182234",
            fill_opacity=1,
        )
        chip.move_to(frame.get_center() + DOWN * 1.0)
        chip_text = Text("z = z2*B^(2m) + z1*B^m + z0", font_size=14, color=BLUE_B)
        chip_text.move_to(chip.get_center())
        chip_text.set_width(2.45)

        group = VGroup(frame, title, headline, body, chip, chip_text)
        group.meta_headline = headline
        group.meta_body = body
        group.meta_chip = chip_text
        return group

    def build_footer(self, result_text):
        frame = RoundedRectangle(
            corner_radius=0.15,
            width=12.0,
            height=0.78,
            stroke_color=YELLOW_B,
            stroke_width=1.4,
            fill_color="#211A10",
            fill_opacity=1,
        )
        frame.to_edge(DOWN, buff=0.22)
        text = Text(f"Final result = {result_text}", font_size=24, color=YELLOW_B)
        text.move_to(frame.get_center())
        return VGroup(frame, text)

    def build_step_card(self, step, idx, total):
        color = self.color_for_step(step["type"])
        title_text, detail_text = self.card_copy(step)

        card = RoundedRectangle(
            corner_radius=0.12,
            width=self.CARD_W,
            height=self.CARD_H,
            stroke_color=color,
            stroke_width=1.4,
            fill_color="#18202B",
            fill_opacity=1,
        )

        meta = Text(
            f"{step['type'].upper()}   depth={step.get('depth', 0)}   {idx}/{total}",
            font_size=14,
            color=color,
        )
        headline = Text(title_text, font_size=20, color=WHITE)
        detail = Text(detail_text, font_size=15, color=GREY_A)

        headline.set_width(self.CARD_W - 0.45)
        detail.set_width(self.CARD_W - 0.45)

        text_group = VGroup(meta, headline, detail).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        text_group.move_to(card.get_center())
        text_group.align_to(card, LEFT).shift(RIGHT * 0.18)

        return VGroup(card, text_group)

    def push_step_into_window(self, new_card, visible_cards, panel):
        animations = []
        if len(visible_cards) >= self.WINDOW_SIZE:
            outgoing = visible_cards.pop(0)
            animations.append(FadeOut(outgoing, shift=UP * 0.18))

        visible_cards.append(new_card)
        self.position_cards(visible_cards, panel)

        new_card.set_opacity(0)
        self.add(new_card)
        animations.append(FadeIn(new_card, shift=DOWN * 0.15))

        targets = self.card_targets(panel, len(visible_cards))
        for mob, target in zip(visible_cards, targets):
            animations.append(mob.animate.move_to(target))

        self.play(*animations, run_time=0.35)

    def position_cards(self, cards, panel):
        targets = self.card_targets(panel, len(cards))
        for mob, target in zip(cards, targets):
            mob.move_to(target)

    def card_targets(self, panel, count):
        left_x = panel.get_left()[0] + 0.2 + self.CARD_W / 2
        first_y = panel.get_top()[1] - 0.9
        gap = 1.02
        return [np.array([left_x, first_y - i * gap, 0]) for i in range(count)]

    def update_focus_panel(self, focus_group, step, idx, total):
        header, line_a, line_b, chip = self.focus_copy(step, idx, total)

        new_headline = Text(header, font_size=20, color=self.color_for_step(step["type"]))
        new_headline.move_to(focus_group.meta_headline)
        new_headline.set_width(3.0)

        new_body = VGroup(
            Text(line_a, font_size=17, color=GREY_A),
            Text(line_b, font_size=17, color=GREY_A),
        ).arrange(DOWN, buff=0.12)
        new_body.move_to(focus_group.meta_body)
        new_body.set_width(3.05)

        new_chip = Text(chip, font_size=14, color=BLUE_B)
        new_chip.move_to(focus_group.meta_chip)
        new_chip.set_width(2.45)

        self.play(
            Transform(focus_group.meta_headline, new_headline),
            Transform(focus_group.meta_body, new_body),
            Transform(focus_group.meta_chip, new_chip),
            run_time=0.22,
        )

    def color_for_step(self, step_type):
        return {
            "call": BLUE_B,
            "split": TEAL_B,
            "sum_parts": GREEN_B,
            "base_case": ORANGE,
            "combine_parts": PURPLE_B,
            "return": YELLOW_B,
        }.get(step_type, GREY_B)

    def short_label(self, label, limit=18):
        if len(label) <= limit:
            return label
        return "..." + label[-(limit - 3):]

    def card_copy(self, step):
        label = self.short_label(step.get("label", ""))
        step_type = step["type"]
        if step_type == "call":
            return (f"Enter {label}", f"Multiply {step['a']} x {step['b']}")
        if step_type == "split":
            return (f"Split with m = {step['m']}", f"a: {step['a1']}|{step['a0']}    b: {step['b1']}|{step['b0']}")
        if step_type == "sum_parts":
            return ("Build middle product", f"({step['sum_a']}) x ({step['sum_b']})")
        if step_type == "base_case":
            return (f"Base case at {label}", f"result = {step['result']}")
        if step_type == "combine_parts":
            return ("Combine z0, z1, z2", f"z0={step['z0']}  z1={step['z1']}  z2={step['z2']}")
        return (f"Return {label}", f"result = {step['result']}")

    def focus_copy(self, step, idx, total):
        step_type = step["type"]
        progress = f"step {idx}/{total}"
        if step_type == "call":
            return ("Enter recursion", progress, f"subproblem: {self.short_label(step['label'], 24)}", "recurse until n <= 2")
        if step_type == "split":
            return ("Split operands", progress, f"m = {step['m']}", "a = a1*B^m + a0")
        if step_type == "sum_parts":
            return ("Prepare z1 raw", progress, f"sum_a={step['sum_a']}, sum_b={step['sum_b']}", "z1 = z1raw - z2 - z0")
        if step_type == "base_case":
            return ("Direct multiply", progress, f"small product = {step['result']}", "schoolbook multiply")
        if step_type == "combine_parts":
            return ("Merge pieces", progress, f"m = {step['m']}", "z = z2*B^(2m) + z1*B^m + z0")
        return ("Return upward", progress, f"value = {step['result']}", "pass result to caller")


class KaratsubaScene(MultiplicationScene):
    pass
