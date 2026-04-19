from manimlib import *

U_VALUE = '8153492' #'5144123122'
V_VALUE = '299'
BASE_VALUE = 10



# WAIT TIME
WAIT_SCALE = 1
WAIT_SCALE_D = WAIT_SCALE * 1.2

DIGIT_SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def digit_to_symbol(value):
    if not isinstance(value, int):
        return str(value)
    if 0 <= value < len(DIGIT_SYMBOLS):
        return DIGIT_SYMBOLS[value]
    return str(value)


def int_to_base_str(value, base):
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    n = abs(value)
    out = []
    while n > 0:
        out.append(DIGIT_SYMBOLS[n % base])
        n //= base
    return sign + "".join(reversed(out))


def digits_to_str(digits, base, msd_first=False):
    seq = digits if msd_first else reversed(digits)
    out = []
    for d in seq:
        if isinstance(d, int):
            out.append(digit_to_symbol(d))
        else:
            out.append(str(d))
    return "".join(out) if out else "0"


def digits_le_to_int(digits, base):
    value = 0
    for d in reversed(digits):
        value = value * base + d
    return value


def digits_be_to_int(digits, base):
    value = 0
    for d in digits:
        value = value * base + d
    return value


def multiply_by_scalar(arr, scalar, base):
    res = []
    carry = 0
    for x in arr:
        temp = x * scalar + carry
        res.append(temp % base)
        carry = temp // base
    if carry > 0:
        res.append(carry)
    return res


def safe_highlight(mobj, color=YELLOW, buff=0.06, stroke_width=3):
    return ShowCreationThenFadeOut(
        SurroundingRectangle(
            mobj,
            color=color,
            buff=buff,
            stroke_width=stroke_width,
        )
    )




def knuth_algorithm_d_steps(u, v, base=10):
    steps = []
    u, v = u.copy(), v.copy()
    while len(u) > 1 and u[-1] == 0: u.pop()
    while len(v) > 1 and v[-1] == 0: v.pop()

    n = len(v)
    m = len(u) - n
    if n <= 1:
        return []

    q = [0] * (m + 1)
    d = base // (v[-1] + 1)

    u_norm = multiply_by_scalar(u, d, base)
    v_norm = multiply_by_scalar(v, d, base)
    while len(u_norm) < m + n + 1:
        u_norm.append(0)

    steps.append({
        "type": "normalize", "d": d,
        "u_orig": u.copy(), "v_orig": v.copy(),
        "u_norm": u_norm.copy(), "v_norm": v_norm.copy(),
    })

    for j in range(m, -1, -1):
        window_digits = [u_norm[k] for k in range(j + n, j - 1, -1)]
        window_value_str = digits_to_str(window_digits, base, msd_first=True)
        numerator_str = f"{digit_to_symbol(u_norm[j + n])}{digit_to_symbol(u_norm[j + n - 1])}"
        numerator = u_norm[j + n] * base + u_norm[j + n - 1]
        q_hat = numerator // v_norm[-1]
        r_hat = numerator % v_norm[-1]

        while q_hat == base or (q_hat * v_norm[-2] > base * r_hat + u_norm[j + n - 2]):
            q_hat -= 1
            r_hat += v_norm[-1]
            if r_hat >= base:
                break

        steps.append({
            "type": "estimate_q_hat", "j": j, "q_hat": q_hat,
            "numerator": numerator,
            "numerator_str": numerator_str,
            "window_digits": window_digits,
            "window_value_str": window_value_str,
            "u_idx_1": j + n, "u_idx_2": j + n - 1,
            "v_idx": n - 1, "v_val_first": v_norm[-1],
        })

        carry = 0
        for i in range(n):
            current_window_digits = [u_norm[k] for k in range(j + n, j - 1, -1)]
            steps.append({
                "type": "interaction_highlight",
                "u_idx": j + i,
                "v_idx": i,
                "j": j,
                "window_digits": current_window_digits,
            })
            old_val = u_norm[j + i]
            v_val = v_norm[i]
            old_carry = carry
            temp = old_val - q_hat * v_val - old_carry
            u_norm[j + i] = temp % base
            carry = -(temp // base)
            steps.append({
                "type": "interaction_update",
                "u_idx": j + i, "v_idx": i,
                "j": j,
                "window_digits": current_window_digits,
                "old_val": old_val, "v_val": v_val,
                "q_hat": q_hat, "old_carry": old_carry,
                "temp": temp, "base": base,
                "new_carry": carry, "new_val": u_norm[j + i],
            })

        top_temp = u_norm[j + n] - carry
        if top_temp < 0:
            q_hat -= 1
            carry = 0
            for i in range(n):
                temp = u_norm[j + i] + v_norm[i] + carry
                u_norm[j + i] = temp % base
                carry = temp // base
            # Use the top digit value after borrow (top_temp), not loop temp.
            u_norm[j + n] = top_temp + carry
            steps.append({"type": "add_back", "j": j, "u_norm": u_norm.copy(), "q_hat": q_hat})
        else:
            u_norm[j + n] = top_temp
            steps.append({"type": "subtract", "j": j, "u_norm": u_norm.copy(), "q_hat": q_hat})

        q[j] = q_hat

    remainder, carry = [], 0
    for i in range(n - 1, -1, -1):
        temp = carry * base + u_norm[i]
        remainder.append(temp // d)
        carry = temp % d
    remainder.reverse()

    while len(q) > 1 and q[-1] == 0: q.pop()
    while len(remainder) > 1 and remainder[-1] == 0: remainder.pop()

    steps.append({"type": "finish", "q": q.copy(), "remainder": remainder.copy(),
                   "d": d, "u_norm": u_norm.copy(), "base": base})
    return steps

# ──────────────────────────  SCENE  ───────────────────────────────────────────

# Layout constants for Vertical (Mobile) Screen
GRID_CELL_W = 0.55
GRID_CELL_H = 0.75
GRID_FONT_SCALE = 0.7
LABEL_SCALE = 0.55
MAIN_LAYOUT_X = 0.0
MAIN_LAYOUT_Y = -0.7
LABEL_TO_INDEX_GAP = 0.2
V_TO_Q_GAP = 0.9
Q_LABEL_LEFT_GAP = 0.4
ENABLE_BORROW_CARRY_PANEL = False
OPS_CENTER_X = 0.0
OPS_D3_Y = 2.2
OPS_D4_Y = 1.55

# Badge-relative spacing for top explanation blocks
BADGE_D3_GAP = 0.18
BADGE_D4_GAP = 0.18
BADGE_D7_GAP = 0.14



# Color palette — harmonious, modern
C_BG_ACCENT   = "#1a1a2e"
C_GRID_U      = "#4361ee"
C_GRID_V      = "#39FF14"
C_GRID_Q      = "#f72585"
C_HIGHLIGHT_Y = "#ffc300"
C_HIGHLIGHT_R = "#ef233c"
C_WINDOW_U    = "#8ecae6"
C_CARRY       = "#f77f00"
C_SURPLUS     = "#06d6a0"
C_FORMULA     = "#a8dadc"
C_STEP        = "#e0aaff"
C_DIM         = "#6c757d"

# Digit-specific colors (brighter than grid border, for readability)
C_DIGIT_U     = "#00f5ff"  # cyan neon
C_DIGIT_V     = "#39FF14"  # bright violet
C_DIGIT_Q     = "#ff2d9b"  # magenta neon


class DivisionScene(Scene):

    # ─── Grid builder ────────────────────────────────────────────────────────
    def build_grid(self, arr, label_tex, grid_color, reverse=True, digit_color=WHITE):
        """Return (whole_group, cells_VGroup) where each cell = VGroup(box, tex)."""
        label = Tex(label_tex).scale(LABEL_SCALE).set_color(grid_color)
        cells = VGroup()
        order = reversed(arr) if reverse else arr
        base_val = getattr(self, "base_val", 10)
        for x in (list(order)):
            box = Rectangle(width=GRID_CELL_W, height=GRID_CELL_H,
                            stroke_color=grid_color, stroke_width=2, fill_color=grid_color, fill_opacity=0.1)
            token = digit_to_symbol(x) if isinstance(x, int) and 0 <= x < base_val else str(x)
            t = Tex(token).scale(GRID_FONT_SCALE).set_color(digit_color)
            if t.get_width() > GRID_CELL_W * 0.85:
                t.scale((GRID_CELL_W * 0.85) / t.get_width())
            t.move_to(box.get_center())
            cells.add(VGroup(box, t))
        cells.arrange(RIGHT, buff=0)

        # Gray index row above the cells for easier digit-position tracking.
        idx_order = list(reversed(range(len(arr)))) if reverse else list(range(len(arr)))
        idx_labels = VGroup()
        for i, idx in enumerate(idx_order):
            idx_t = Tex(str(idx)).scale(0.32).set_color(C_DIM)
            # Keep index attached to its cell even if cells are later re-aligned.
            idx_t.add_updater(lambda m, cell=cells[i]: m.move_to(cell[0].get_top() + UP * 0.16))
            idx_t.move_to(cells[i][0].get_top() + UP * 0.16)
            idx_labels.add(idx_t)

        cells_with_index = VGroup(cells, idx_labels)
        group = VGroup(label, cells_with_index).arrange(RIGHT, buff=0.4)
        return group, cells

    # ─── Step badge ──────────────────────────────────────────────────────────
    def update_step_badge(self, text, color=C_STEP):
        new_badge = Text(text, font_size=20, color=color)
        new_badge.to_edge(UP, buff=0.25)
        anims = []
        if self.step_badge is not None:
            anims.append(FadeOut(self.step_badge))
        anims.append(FadeIn(new_badge))
        self.play(*anims, run_time=0.5)
        self.step_badge = new_badge

    # ─── Construct ───────────────────────────────────────────────────────────
    def construct(self):
        u_str = U_VALUE.strip().upper()
        v_str = V_VALUE.strip().upper()
        base_val = BASE_VALUE
        base_display = str(base_val)
        self.base_val = base_val

        u = [int(c, base_val) for c in reversed(u_str)]
        v = [int(c, base_val) for c in reversed(v_str)]

        self.step_badge = None

        # ── Phase 0: Title card ──────────────────────────────────────────────
        title = Text("Knuth Algorithm D", font_size=36, color=WHITE, weight=BOLD)
        subtitle = Text("Big Integer Division", font_size=20, color=C_DIM)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.6)

        problem = Text(
            f"{u_str} ÷ {v_str} = ?"
        ).scale(0.8).next_to(title_group, DOWN, buff=0.6).set_color(C_HIGHLIGHT_Y)

        base_number = Tex(
            rf"\text{{Base }} B = {base_display}"
        ).scale(0.8).next_to(problem, DOWN, buff=0.4).set_color(C_SURPLUS)

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(problem, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(base_number, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5 * WAIT_SCALE)
        self.play(FadeOut(VGroup(title_group, problem, base_number)), run_time=0.8)

        # ── Compute steps ────────────────────────────────────────────────────
        steps = knuth_algorithm_d_steps(u, v, base=base_val)
        n = len(v)
        m = len(u) - n

        # ── Persistent state ─────────────────────────────────────────────────
        u_grp = None   # whole group for U_norm
        u_cells = None  # cells VGroup
        v_grp = None
        v_cells = None
        q_grp = None
        q_cells = None
        main_grids = None
        division_lines = None
        gen_formula_mobj = None
        d3_result_mobj = None
        d4_work_mobj = None
        d3_subtract_mobj = None
        d3_result_digit_map = None
        u_window_mobj = None

        # Side-panel values (Tex mobj references)
        carry_val = None
        surplus_val = None
        carry_box = None
        surplus_box = None
        side_panel = None
        panel_step_mobj = None
        v_norm_value_num = digits_le_to_int(v, base_val)

        # ── Process steps ────────────────────────────────────────────────────
        for step in steps:

            # ═══════════════════  NORMALIZE  ═══════════════════════════════
            if step["type"] == "normalize":
                self.update_step_badge(f"D1  Normalize")
                v_norm_value_num = digits_le_to_int(step["v_norm"], base_val)
                
                # ── Phase 1: Show original U and V ────────────────────────────
                u_orig_grp, u_orig_cells = self.build_grid(step["u_orig"], r"U", C_GRID_U, digit_color=C_DIGIT_U)
                v_orig_grp, v_orig_cells = self.build_grid(step["v_orig"], r"V", C_GRID_V, digit_color=C_DIGIT_V)
                
                u_orig_grp.next_to(self.step_badge, DOWN, buff=0.5).set_x(-2)
                v_orig_grp.next_to(u_orig_grp, DOWN, buff=0.5)
                v_orig_cells.align_to(u_orig_cells, LEFT)
                v_orig_grp[0].next_to(v_orig_cells, LEFT, buff=0.4)
                
                self.play(FadeIn(u_orig_grp, shift=DOWN * 0.3), run_time=0.8)
                self.play(FadeIn(v_orig_grp, shift=DOWN * 0.3), run_time=0.8)
                self.wait(2 * WAIT_SCALE)
                
                # ── Phase 2: Check if normalization needed ──────────────────
                d_val = step['d']
                v_msb = step["v_orig"][-1]
                base_val = base_val  # Should be 10
                threshold = base_val // 2
                needs_normalize = d_val > 1
                
                check_text = Tex(
                    rf"v_{{n-1}} = {digit_to_symbol(v_msb)} \stackrel{{?}}{{\geq}} B/2 = {int_to_base_str(threshold, base_val)}",
                    color=C_HIGHLIGHT_Y
                ).scale(0.7)
                check_text.next_to(u_orig_grp, RIGHT, buff=1.0)
                self.play(FadeIn(check_text, shift=LEFT * 0.6), run_time=0.7)
                status_text = None
                d_formula = None
                if needs_normalize:
                    status_text = Text(
                        "Need normalization",
                        font_size=18,
                        color=C_HIGHLIGHT_R
                    )
                    status_text.next_to(check_text, DOWN, buff=0.3).set_x(2)
                    self.play(FadeIn(status_text, shift=LEFT * 0.6), run_time=0.7)
                    self.wait(0.5 * WAIT_SCALE)

                    # ── Phase 3: Calculate d and show formula step-by-step ───
                    denom_sum = v_msb + 1
                    d_formula_title = Tex(r"\text{D1: Calculate multiplier } d \text{ to scale up } V", color=C_DIM).scale(0.65)
                    d_formula_1 = Tex(r"d = \left\lfloor \frac{B}{v_{n-1} + 1} \right\rfloor", color=C_FORMULA).scale(0.7)
                    d_formula_2 = Tex(rf"= \left\lfloor \frac{{{base_val}}}{{{v_msb} + 1}} \right\rfloor", color=C_FORMULA).scale(0.7)
                    d_formula_3 = Tex(rf"= \left\lfloor \frac{{{base_val}}}{{{denom_sum}}} \right\rfloor", color=C_FORMULA).scale(0.7)
                    d_formula_4 = Tex(rf"= {d_val}", color=C_HIGHLIGHT_Y).scale(0.75)

                    d_calc_group = VGroup(d_formula_1, d_formula_2, d_formula_3, d_formula_4).arrange(RIGHT, buff=0.15)
                    d_full_group = VGroup(d_formula_title, d_calc_group).arrange(DOWN, buff=0.25)
                    d_full_group.next_to(status_text, DOWN, buff=0.6).set_x(2)
                    d_formula = d_full_group  # for later FadeOut

                    self.play(FadeIn(d_formula_title, shift=UP * 0.1), run_time=0.5)
                    self.play(FadeIn(d_formula_1, shift=UP * 0.1), run_time=0.6)
                    self.wait(0.5)
                    self.play(FadeIn(d_formula_2, shift=LEFT * 0.1), run_time=0.5)
                    self.wait(0.5)
                    self.play(FadeIn(d_formula_3, shift=LEFT * 0.1), run_time=0.5)
                    self.wait(0.5)
                    self.play(FadeIn(d_formula_4, shift=LEFT * 0.1), run_time=0.7)

                    self.wait(2.2 * WAIT_SCALE)
                    self.play(FadeOut(VGroup(check_text, status_text, d_formula)), run_time=0.5)
                else:
                    self.wait(0.8 * WAIT_SCALE)
                    self.play(FadeOut(check_text), run_time=0.4)
                
                u_norm_grp, u_norm_cells = self.build_grid(step["u_norm"], r"U_{norm}", C_GRID_U, digit_color=C_DIGIT_U)
                v_norm_grp, v_norm_cells = self.build_grid(step["v_norm"], r"V_{norm}", C_GRID_V, digit_color=C_DIGIT_V)
                
                u_norm_grp.next_to(self.step_badge, DOWN, buff=0.5).set_x(2)
                v_norm_grp.next_to(u_norm_grp, DOWN, buff=0.5)
                v_norm_cells.align_to(u_norm_cells, LEFT)
                v_norm_grp[0].next_to(v_norm_cells, LEFT, buff=0.4)
                
                if needs_normalize:
                    # Show transformation arrows and equations only when needed.
                    u_orig_str = digits_to_str(step["u_orig"], base_val)
                    u_norm_str = digits_to_str(step["u_norm"][:len(step["u_orig"])], base_val)
                    v_orig_str = digits_to_str(step["v_orig"], base_val)
                    v_norm_str = digits_to_str(step["v_norm"][:len(step["v_orig"])], base_val)
                    u_transform = VGroup(
                        Tex(u_orig_str, color=C_DIGIT_U).scale(0.7),
                        Tex(r"\times", color=C_FORMULA).scale(0.7),
                        Tex(str(d_val), color=C_HIGHLIGHT_Y).scale(0.7),
                        Tex(r"=", color=C_FORMULA).scale(0.7),
                        Tex(u_norm_str, color=C_DIGIT_U).scale(0.7),
                    ).arrange(RIGHT, buff=0.2)
                    u_transform.next_to(u_orig_grp, RIGHT, buff=1.0)

                    v_transform = VGroup(
                        Tex(v_orig_str, color=C_DIGIT_V).scale(0.7),
                        Tex(r"\times", color=C_FORMULA).scale(0.7),
                        Tex(str(d_val), color=C_HIGHLIGHT_Y).scale(0.7),
                        Tex(r"=", color=C_FORMULA).scale(0.7),
                        Tex(v_norm_str, color=C_DIGIT_V).scale(0.7),
                    ).arrange(RIGHT, buff=0.2)
                    v_transform.next_to(v_orig_grp, RIGHT, buff=1.0)

                    self.play(
                        FadeIn(u_transform, shift=UP * 0.2),
                        FadeIn(v_transform, shift=UP * 0.2),
                        run_time=0.8
                    )
                    self.wait(2 * WAIT_SCALE)

                    # Fade out originals and equations, show final normalized grids
                    self.play(
                        FadeOut(VGroup(u_orig_grp, v_orig_grp, u_transform, v_transform)),
                        run_time=0.6
                    )
                else:
                    self.play(FadeOut(VGroup(u_orig_grp, v_orig_grp)), run_time=0.5)
                
                # Build final grids using long-division layout:
                # U on the left, V on the right, Q under V.
                u_grp, u_cells = self.build_grid(step["u_norm"], r"U_{norm}", C_GRID_U, digit_color=C_DIGIT_U)
                v_grp, v_cells = self.build_grid(step["v_norm"], r"V_{norm}", C_GRID_V, digit_color=C_DIGIT_V)

                q_init = ["-"] * (m + 1)
                q_grp, q_cells = self.build_grid(q_init, r"Q", C_GRID_Q, reverse=True, digit_color=C_DIGIT_Q)

                # Right column: V over Q.
                q_grp.next_to(v_grp, DOWN, buff=V_TO_Q_GAP)
                q_cells.align_to(v_cells, LEFT)
                q_grp[0].next_to(q_cells, LEFT, buff=Q_LABEL_LEFT_GAP)

                right_column = VGroup(v_grp, q_grp)
                u_grp.next_to(right_column, LEFT, buff=1.1)
                u_cells.align_to(v_cells, UP)
                u_grp[0].next_to(u_grp[1], UP, buff=LABEL_TO_INDEX_GAP)
                u_grp[0].set_x(u_cells.get_center()[0])
                v_grp[0].next_to(v_grp[1], UP, buff=LABEL_TO_INDEX_GAP)
                v_grp[0].set_x(v_cells.get_center()[0])
                u_grp[0].align_to(v_grp[0], UP)

                main_grids = VGroup(u_grp, right_column)
                main_grids.set_y(MAIN_LAYOUT_Y)
                # Keep the number columns (U, V, Q) balanced around scene center.
                core_digits = VGroup(u_cells, v_cells, q_cells)
                main_grids.shift(RIGHT * (MAIN_LAYOUT_X - core_digits.get_center()[0]))

                # Division separators similar to school long-division notation.
                sep_x = (u_cells.get_right()[0] + v_cells.get_left()[0]) / 2
                top_y = max(u_cells.get_top()[1], v_cells.get_top()[1], q_cells.get_top()[1]) + 0.22
                bot_y = min(u_cells.get_bottom()[1], v_cells.get_bottom()[1], q_cells.get_bottom()[1]) - 0.18
                vertical_divider = Line(
                    [sep_x, top_y, 0],
                    [sep_x, bot_y, 0],
                    color=C_FORMULA,
                    stroke_width=2,
                )

                h_y = (v_cells.get_bottom()[1] + q_cells.get_top()[1]) / 2
                h_left = sep_x + 0.05
                h_right = max(v_cells.get_right()[0], q_cells.get_right()[0]) + 0.24
                horizontal_divider = Line(
                    [h_left, h_y, 0],
                    [h_right, h_y, 0],
                    color=C_FORMULA,
                    stroke_width=2,
                )
                division_lines = VGroup(vertical_divider, horizontal_divider)

                # ── Side panel (Right side) ─ Borrow & Subtract ──────────────
                if ENABLE_BORROW_CARRY_PANEL:
                    carry_label = Text("borrow", font_size=14, color=C_CARRY)
                    carry_box = Rectangle(width=0.7, height=0.7, stroke_color=C_CARRY,
                                          stroke_width=2, fill_color=C_CARRY, fill_opacity=0.08)
                    carry_val = Tex("0").scale(0.6).set_color(C_CARRY).move_to(carry_box)
                    carry_unit = VGroup(carry_label, VGroup(carry_box, carry_val)).arrange(DOWN, buff=0.15)

                    surplus_label = Text("subtract", font_size=14, color=C_SURPLUS)
                    surplus_box = Rectangle(width=0.7, height=0.7, stroke_color=C_SURPLUS,
                                            stroke_width=2, fill_color=C_SURPLUS, fill_opacity=0.08)
                    surplus_val = Tex("0").scale(0.6).set_color(C_HIGHLIGHT_Y).move_to(surplus_box)
                    surplus_unit = VGroup(surplus_label, VGroup(surplus_box, surplus_val)).arrange(DOWN, buff=0.15)

                    registers_grp = VGroup(carry_unit, surplus_unit).arrange(RIGHT, buff=0.6)
                    side_panel = registers_grp
                    side_panel.next_to(main_grids, DOWN, buff=0.35)
                    side_panel.set_x(main_grids.get_center()[0])
                else:
                    side_panel = None
                    carry_val = None
                    surplus_val = None
                    carry_box = None
                    surplus_box = None
                    panel_step_mobj = None

                # ── Verification ─────────────────────────────────────────────
                verify_text = Tex(
                    rf"v_{{n-1}}' = {digit_to_symbol(step['v_norm'][-1])} \geq B/2 = {int_to_base_str(threshold, base_val)} \quad \checkmark",
                    color=C_SURPLUS
                ).scale(0.65)
                verify_text.next_to(main_grids, UP, buff=0.25)
                verify_text.set_x(0)

                normalize_anims = [
                    FadeIn(u_grp, shift=DOWN * 0.3),
                    FadeIn(v_grp, shift=DOWN * 0.3),
                    FadeIn(q_grp, shift=DOWN * 0.3),
                    ShowCreation(division_lines),
                ]
                if side_panel is not None:
                    normalize_anims.append(FadeIn(side_panel, shift=DOWN * 0.2))
                self.play(*normalize_anims, run_time=1.0)
                self.play(FadeIn(verify_text, shift=UP * 0.2), run_time=0.6)
                self.wait(2 * WAIT_SCALE)
                self.play(FadeOut(verify_text), run_time=0.4)

            # ═══════════════════  ESTIMATE q̂  ═════════════════════════════
            elif step["type"] == "estimate_q_hat":
                j = step["j"]
                self.update_step_badge(f"D3  Estimate q̂  (j = {j})")

                u_vis_1 = len(u_cells) - 1 - step["u_idx_1"]
                u_vis_2 = len(u_cells) - 1 - step["u_idx_2"]
                v_vis   = len(v_cells) - 1 - step["v_idx"]

                # D3 uses only two leading U cells: u[j+n], u[j+n-1]
                d3_cells = [u_cells[u_vis_1], u_cells[u_vis_2]]

                # Display the window being examined
                window_label = Text(f"D3 (j={j})", font_size=14, color=C_DIM)
                window_values = Tex(
                    rf"[u_{{j+n}},u_{{j+n-1}}] = {step['numerator_str']}"
                ).scale(0.65).set_color(C_DIGIT_U)
                window_display = VGroup(window_label, window_values).arrange(
                    DOWN, buff=0.1
                )
                window_display.next_to(self.step_badge, DOWN, buff=BADGE_D3_GAP)
                window_display.set_x(self.step_badge.get_x())

                # Formula: ⌊ numerator / v_first ⌋ = q_hat
                d3_numerator = Tex(str(step["numerator_str"])).set_color(C_GRID_U)
                d3_denominator = Tex(digit_to_symbol(step["v_val_first"])).set_color(C_GRID_V)
                d3_frac_line = Line(LEFT, RIGHT, color=C_FORMULA).set_width(max(d3_numerator.get_width(), d3_denominator.get_width()) + 0.2)
                d3_frac = VGroup(d3_numerator, d3_frac_line, d3_denominator).arrange(DOWN, buff=0.1)

                eq = VGroup(
                    Tex(r"\hat{q}").set_color(C_GRID_Q),
                    Tex(r"=").set_color(C_FORMULA),
                    Tex(r"\lfloor\ ").set_color(C_FORMULA),
                    d3_frac,
                    Tex(r"\ \rfloor").set_color(C_FORMULA),
                    Tex(r"=").set_color(C_FORMULA),
                    Tex(digit_to_symbol(step["q_hat"])).set_color(C_GRID_Q),
                ).arrange(RIGHT, buff=0.15).scale(0.85)
                eq.next_to(window_display, DOWN, buff=0.3)
                eq.set_x(self.step_badge.get_x())

                d3_eq_tag = Text("D3:", font_size=14, color=C_STEP)
                d3_eq_tag.next_to(eq, UP, buff=0.12)

                # Generic formula
                new_gen = Tex(
                    r"\text{D3: }\hat{q} = \min\left( \left\lfloor \frac{u_{j+n} \cdot B + u_{j+n-1}}{v_{n-1}} \right\rfloor ,\; B-1 \right)",
                    color=C_FORMULA,
                    tex_to_color_map={
                        r"\hat{q}": C_GRID_Q,
                        r"u_{j+n}": C_GRID_U,
                        r"u_{j+n-1}": C_GRID_U,
                        r"v_{n-1}": C_GRID_V,
                    }
                ).scale(0.65)
                new_gen.next_to(eq, DOWN, buff=0.15)
                new_gen.set_x(self.step_badge.get_x())

                gen_anims = []
                if gen_formula_mobj is not None:
                    gen_anims.append(FadeOut(gen_formula_mobj))
                gen_anims.append(FadeIn(new_gen))
                if d4_work_mobj is not None:
                    gen_anims.append(FadeOut(d4_work_mobj))
                    d4_work_mobj = None
                if d3_result_mobj is not None:
                    gen_anims.append(FadeOut(d3_result_mobj))

                # Light-blue window highlight for current U segment [j..j+n].
                window_cells_full = []
                for idx in range(step["j"] + n, step["j"] - 1, -1):
                    vis_idx = len(u_cells) - 1 - idx
                    if 0 <= vis_idx < len(u_cells):
                        window_cells_full.append(u_cells[vis_idx])
                new_u_window = None
                if window_cells_full:
                    new_u_window = SurroundingRectangle(
                        VGroup(*window_cells_full),
                        color=C_WINDOW_U,
                        buff=0.06,
                        stroke_width=3,
                    )
                    new_u_window.set_fill(C_WINDOW_U, opacity=0.12)
                    if u_window_mobj is not None:
                        gen_anims.append(FadeOut(u_window_mobj))

                # Highlight exactly 2 cells for D3.
                d3_highlights = [safe_highlight(cell, color=C_HIGHLIGHT_Y) for cell in d3_cells]

                anim_u_num = TransformFromCopy(VGroup(u_cells[u_vis_1][-1], u_cells[u_vis_2][-1]), d3_numerator)
                anim_v_den = TransformFromCopy(v_cells[v_vis][-1], d3_denominator)
                rest_eq = VGroup(eq[0], eq[1], eq[2], d3_frac_line, eq[4], eq[5], eq[6])

                self.play(
                    *gen_anims,
                    FadeIn(window_display, shift=UP * 0.2),
                    FadeIn(d3_eq_tag, shift=UP * 0.1),
                    *([FadeIn(new_u_window)] if new_u_window is not None else []),
                    run_time=0.7,
                )
                # Show the U window first, then 0.5s later show the yellow D3 highlights.
                self.wait(0.5)
                self.play(
                    *d3_highlights,
                    anim_u_num, anim_v_den,
                    FadeIn(rest_eq, shift=UP * 0.2),
                    run_time=0.9,
                )
                d3_frac.add(d3_numerator, d3_denominator) # Ensure they are formally part of frac 
                eq.add(d3_frac) # Ensure frac is fully attached to eq
                gen_formula_mobj = new_gen
                d3_result_mobj = VGroup(window_display, eq, d3_eq_tag)
                if new_u_window is not None:
                    u_window_mobj = new_u_window

                self.wait(1.2 * WAIT_SCALE_D)

            # ═══════════════════  INTERACTION HIGHLIGHT  ══════════════════
            elif step["type"] == "interaction_highlight":
                # Highlight is synchronized with D4 summary in interaction_update.
                continue

            # ═══════════════════  INTERACTION UPDATE  ═════════════════════
            elif step["type"] == "interaction_update":
                # Show D4 block right after the first window highlight.
                show_compact_d4 = step["v_idx"] == 0

                window_context = None
                d4_summary = None
                new_gen = None
                gen_anims = []

                if show_compact_d4:
                    window_cells = []
                    for idx in range(step["j"] + n, step["j"] - 1, -1):
                        vis_idx = len(u_cells) - 1 - idx
                        if 0 <= vis_idx < len(u_cells):
                            window_cells.append(u_cells[vis_idx])
                    window_value_num = digits_be_to_int(step["window_digits"], base_val)
                    window_value_str = int_to_base_str(window_value_num, base_val)
                    subtract_value = window_value_num - step["q_hat"] * v_norm_value_num
                    subtract_value_str = int_to_base_str(subtract_value, base_val)
                    v_norm_value_str = int_to_base_str(v_norm_value_num, base_val)
                    q_hat_str = digit_to_symbol(step["q_hat"])

                    d4_window_label = Text(f"D4 (j={step['j']})", font_size=14, color=C_DIM)
                    d4_window_values = Tex(
                        rf"U_w = {window_value_str}"
                    ).scale(0.65).set_color(C_DIGIT_U)
                    d4_window_display = VGroup(d4_window_label, d4_window_values).arrange(
                        DOWN, buff=0.2
                    )

                    d4_eq = VGroup(
                        Tex(r"U_w").set_color(C_GRID_U),
                        Tex(r"=").set_color(C_FORMULA),
                        Tex(window_value_str).set_color(C_DIGIT_U),
                        Tex(r"-").set_color(C_FORMULA),
                        Tex(q_hat_str).set_color(C_GRID_Q),
                        Tex(r"\times").set_color(C_FORMULA),
                        Tex(v_norm_value_str).set_color(C_GRID_V),
                        Tex(r"=").set_color(C_FORMULA),
                        Tex(subtract_value_str).set_color(C_SURPLUS),
                    ).arrange(RIGHT, buff=0.15).scale(0.8)
                    d4_eq.next_to(d4_window_display, DOWN, buff=0.3)

                    d4_eq_tag = Text("D4:", font_size=14, color=C_STEP)
                    d4_eq_tag.next_to(d4_eq, UP, buff=0.12)

                    d4_gen = Tex(
                        r"\text{D4: }U_w \leftarrow U_w - \hat{q}\cdot V",
                        color=C_FORMULA,
                        tex_to_color_map={
                            r"U_w": C_GRID_U,
                            r"\hat{q}": C_GRID_Q,
                            r"V": C_GRID_V,
                        }
                    ).scale(0.56)
                    d4_gen.next_to(d4_eq, DOWN, buff=0.15)

                    d4_summary = VGroup(d4_window_display, d4_eq, d4_eq_tag, d4_gen)
                    # Keep D4 sharing the same start position as D3 (top-aligned).
                    if d3_result_mobj is not None:
                        d4_summary.align_to(d3_result_mobj, UP)
                        d4_summary.set_x(d3_result_mobj.get_x())
                    else:
                        d4_summary.next_to(self.step_badge, DOWN, buff=BADGE_D4_GAP)
                        d4_summary.set_x(self.step_badge.get_x())
                    d4_window_display.set_x(self.step_badge.get_x())
                    d4_eq.set_x(self.step_badge.get_x())
                    d4_eq_tag.next_to(d4_eq, UP, buff=0.12)
                    d4_gen.next_to(d4_eq, DOWN, buff=0.15)

                    # Keep U_w value hidden first, then reveal via TransformFromCopy.
                    d4_eq[2].set_opacity(0)
                    d4_eq_rest = VGroup(
                        d4_eq[0], d4_eq[1], d4_eq[3], d4_eq[4], d4_eq[5], d4_eq[6], d4_eq[7], d4_eq[8]
                    )

                    if d4_work_mobj is not None:
                        gen_anims.append(FadeOut(d4_work_mobj))

                    # Long-division style subtraction row under U: (q̂ * V) shifted by j.
                    partial_product_num = step["q_hat"] * v_norm_value_num
                    partial_digits_rev = list(int_to_base_str(partial_product_num, base_val))[::-1]  # LSD -> MSD
                    subtract_row_y = u_cells[0][0].get_bottom()[1] - 0.32

                    sub_digits = VGroup()
                    used_vis = []
                    for offset, ch in enumerate(partial_digits_rev):
                        idx = step["j"] + offset
                        vis_idx = len(u_cells) - 1 - idx
                        if 0 <= vis_idx < len(u_cells):
                            digit_tex = Tex(ch).scale(0.62).set_color(C_HIGHLIGHT_Y)
                            digit_tex.move_to(
                                [u_cells[vis_idx][0].get_center()[0], subtract_row_y, 0]
                            )
                            sub_digits.add(digit_tex)
                            used_vis.append(vis_idx)

                    minus_sign = None
                    subtract_line = None
                    result_digits = VGroup()
                    result_digit_map = {}
                    result_sign = None
                    result_digits_rev = list(int_to_base_str(abs(subtract_value), base_val))[::-1]
                    result_row_y = subtract_row_y - 0.36
                    result_vis_used = []
                    for offset, ch in enumerate(result_digits_rev):
                        idx = step["j"] + offset
                        vis_idx = len(u_cells) - 1 - idx
                        if 0 <= vis_idx < len(u_cells):
                            d_tex = Tex(ch).scale(0.62).set_color(C_SURPLUS)
                            d_tex.move_to([u_cells[vis_idx][0].get_center()[0], result_row_y, 0])
                            result_digits.add(d_tex)
                            result_digit_map[vis_idx] = d_tex
                            result_vis_used.append(vis_idx)

                    if used_vis:
                        span_vis = used_vis + result_vis_used if result_vis_used else used_vis
                        left_vis = min(span_vis)
                        right_vis = max(span_vis)
                        minus_sign = Tex(r"-").scale(0.7).set_color(C_HIGHLIGHT_Y)
                        minus_sign.move_to(
                            [u_cells[left_vis][0].get_left()[0] - 0.18, subtract_row_y, 0]
                        )
                        line_y = subtract_row_y - 0.2
                        subtract_line = Line(
                            [u_cells[left_vis][0].get_left()[0] - 0.06, line_y, 0],
                            [u_cells[right_vis][0].get_right()[0] + 0.06, line_y, 0],
                            color=C_HIGHLIGHT_Y,
                            stroke_width=2,
                        )
                        if subtract_value < 0:
                            result_sign = Tex(r"-").scale(0.68).set_color(C_SURPLUS)
                            result_sign.move_to(
                                [u_cells[left_vis][0].get_left()[0] - 0.18, result_row_y, 0]
                            )

                    row_items = [sub_digits, result_digits]
                    if minus_sign is not None:
                        row_items.append(minus_sign)
                    if subtract_line is not None:
                        row_items.append(subtract_line)
                    if result_sign is not None:
                        row_items.append(result_sign)
                    new_subtract_row = VGroup(*row_items)

                    if d3_subtract_mobj is not None:
                        gen_anims.append(FadeOut(d3_subtract_mobj))
                    d3_result_digit_map = result_digit_map

                if show_compact_d4:
                    source_digits = VGroup(*[cell[-1] for cell in window_cells])
                    # D3 -> D4 sequential transition: hide D3 first, then show D4.
                    pre_d4_anims = list(gen_anims)
                    if d3_result_mobj is not None:
                        pre_d4_anims.append(FadeOut(d3_result_mobj))
                        d3_result_mobj = None
                    if gen_formula_mobj is not None:
                        pre_d4_anims.append(FadeOut(gen_formula_mobj))
                        gen_formula_mobj = None
                    if pre_d4_anims:
                        self.play(*pre_d4_anims, run_time=0.35)

                    self.play(
                        FadeIn(d4_window_display, shift=UP * 0.2),
                        FadeIn(d4_eq_tag, shift=UP * 0.1),
                        FadeIn(d4_eq_rest, shift=UP * 0.2),
                        FadeIn(d4_gen, shift=UP * 0.1),
                        run_time=0.55,
                    )
                    self.play(
                        TransformFromCopy(source_digits, d4_eq[2]),
                        d4_eq[2].animate.set_opacity(1),
                        run_time=0.6,
                    )
                    self.play(
                        FadeIn(new_subtract_row, shift=UP * 0.08),
                        run_time=0.45,
                    )

                    d4_work_mobj = d4_summary
                    d3_subtract_mobj = new_subtract_row

                # Live register update: show actual subtract term and actual borrow.
                if ENABLE_BORROW_CARRY_PANEL and carry_box is not None and surplus_box is not None:
                    subtract_term = step["q_hat"] * step["v_val"] + step["old_carry"]
                    borrow_term = step["new_carry"]

                    panel_step_new = VGroup(
                        Tex(
                            rf"\text{{subtract}} = {step['q_hat']}\times {step['v_val']} + {step['old_carry']} = {subtract_term}",
                            color=C_HIGHLIGHT_Y,
                        ).scale(0.5),
                        Tex(
                            rf"\text{{borrow}} = {borrow_term}",
                            color=C_CARRY,
                        ).scale(0.5),
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
                    panel_step_new.next_to(side_panel, UP, buff=0.12)
                    panel_step_new.set_x(side_panel.get_center()[0])

                    explain_anims = []
                    if panel_step_mobj is None:
                        explain_anims.append(FadeIn(panel_step_new, shift=UP * 0.08))
                    else:
                        explain_anims.append(ReplacementTransform(panel_step_mobj, panel_step_new))

                    # Visual link: D4 equation drives borrow/subtract registers.
                    d4_source = None
                    if d4_work_mobj is not None and len(d4_work_mobj) > 1:
                        d4_source = d4_work_mobj[1]
                    elif d4_summary is not None and len(d4_summary) > 1:
                        d4_source = d4_summary[1]

                    link_anims = []
                    if d4_source is not None:
                        d4_flash = ShowCreationThenFadeOut(
                            SurroundingRectangle(d4_source, color=C_FORMULA, buff=0.06, stroke_width=3),
                            run_time=0.35,
                        )
                        borrow_link = ShowCreationThenFadeOut(
                            CurvedArrow(
                                d4_source.get_bottom() + LEFT * 0.35,
                                carry_box.get_top() + UP * 0.02,
                                angle=-TAU / 6,
                                color=C_CARRY,
                                stroke_width=3,
                            ),
                            run_time=0.35,
                        )
                        subtract_link = ShowCreationThenFadeOut(
                            CurvedArrow(
                                d4_source.get_bottom() + RIGHT * 0.35,
                                surplus_box.get_top() + UP * 0.02,
                                angle=TAU / 6,
                                color=C_HIGHLIGHT_Y,
                                stroke_width=3,
                            ),
                            run_time=0.35,
                        )
                        link_anims.extend([d4_flash, borrow_link, subtract_link])

                    carry_flash = ShowCreationThenFadeOut(
                        SurroundingRectangle(carry_box, color=C_CARRY, buff=0.05, stroke_width=3),
                        run_time=0.35,
                    )
                    subtract_flash = ShowCreationThenFadeOut(
                        SurroundingRectangle(surplus_box, color=C_HIGHLIGHT_Y, buff=0.05, stroke_width=3),
                        run_time=0.35,
                    )
                    self.play(*explain_anims, *link_anims, carry_flash, subtract_flash, run_time=0.45)

                    new_carry_tex = Tex(str(borrow_term)).scale(0.6).set_color(C_CARRY).move_to(carry_box)
                    new_surplus_tex = Tex(str(subtract_term)).scale(0.6).set_color(C_HIGHLIGHT_Y).move_to(surplus_box)
                    self.play(
                        FadeOut(carry_val), FadeIn(new_carry_tex),
                        FadeOut(surplus_val), FadeIn(new_surplus_tex),
                        run_time=0.25,
                    )
                    carry_val = new_carry_tex
                    surplus_val = new_surplus_tex
                    panel_step_mobj = panel_step_new

                # Keep U unchanged during D4. U is replaced at subtract/add-back step.
                self.wait(0.15 * WAIT_SCALE_D)

            # ═══════════════════  SUBTRACT / ADD-BACK  ════════════════════
            elif step["type"] in ("subtract", "add_back"):
                q_hat = step["q_hat"]
                j = step["j"]

                # Keep a visible q_hat token so we can animate it flying into Q[j].
                q_hat_fly_token = None
                q_hat_source = None
                if d4_work_mobj is not None and len(d4_work_mobj) > 1 and len(d4_work_mobj[1]) > 4:
                    q_hat_source = d4_work_mobj[1][4]
                elif d3_result_mobj is not None and len(d3_result_mobj) > 1 and len(d3_result_mobj[1]) >= 7:
                    q_hat_source = d3_result_mobj[1][6] # Note: eq has 7 elements now: q_hat, =, \lfloor, frac, \rfloor, =, result
                if q_hat_source is not None:
                    q_hat_fly_token = q_hat_source.copy()
                    self.add(q_hat_fly_token)

                fade_temp = []
                if d4_work_mobj is not None:
                    fade_temp.append(FadeOut(d4_work_mobj))
                    d4_work_mobj = None
                if u_window_mobj is not None:
                    fade_temp.append(FadeOut(u_window_mobj))
                    u_window_mobj = None
                if gen_formula_mobj is not None:
                    fade_temp.append(FadeOut(gen_formula_mobj))
                    gen_formula_mobj = None
                if fade_temp:
                    self.play(*fade_temp, run_time=0.25)

                if step["type"] == "add_back":
                    self.update_step_badge(f"D6  Add-back  (j = {j})")
                else:
                    self.update_step_badge(f"D5  Set q[{j}] = {q_hat}")

                if step["type"] == "add_back":
                    prev_q_hat = q_hat + 1
                    add_back_title = Text(
                        "q_hat overestimated -> add back V",
                        font_size=18,
                        color=C_HIGHLIGHT_R,
                    )
                    qhat_prefix = Tex(r"\hat{q}:", color=C_GRID_Q).scale(0.62)
                    old_q_tex = Tex(digit_to_symbol(prev_q_hat), color=C_GRID_Q).scale(0.68)
                    eq_tex = Tex("=", color=C_FORMULA).scale(0.62)
                    new_q_tex = Tex(digit_to_symbol(q_hat), color=C_GRID_Q).scale(0.68)
                    add_back_q_row = VGroup(qhat_prefix, old_q_tex, eq_tex, new_q_tex).arrange(
                        RIGHT, buff=0.12, aligned_edge=DOWN
                    )
                    old_q_strike = Line(
                        old_q_tex.get_corner(UL),
                        old_q_tex.get_corner(DR),
                        color=C_HIGHLIGHT_R,
                        stroke_width=4,
                    )
                    add_back_q = VGroup(add_back_q_row, old_q_strike)
                    v_norm_value_str = int_to_base_str(v_norm_value_num, base_val)
                    add_back_u = Tex(
                        rf"U_w \leftarrow U_w + V\;(= +{v_norm_value_str})",
                        color=C_FORMULA,
                        tex_to_color_map={
                            r"U_w": C_GRID_U,
                            r"V": C_GRID_V,
                            r"\hat{q}": C_GRID_Q,
                        }
                    ).scale(0.58)
                    add_back_info = VGroup(add_back_title, add_back_q, add_back_u).arrange(
                        DOWN, aligned_edge=LEFT, buff=0.08
                    )
                    add_back_info.next_to(self.step_badge, DOWN, buff=0.2)
                    add_back_info.set_x(self.step_badge.get_x())

                    u_window_cells = []
                    for idx in range(j + n - 1, j - 1, -1):
                        vis_idx = len(u_cells) - 1 - idx
                        if 0 <= vis_idx < len(u_cells):
                            u_window_cells.append(u_cells[vis_idx])

                    v_window_cells = []
                    for i in range(n - 1, -1, -1):
                        vis_idx = len(v_cells) - 1 - i
                        if 0 <= vis_idx < len(v_cells):
                            v_window_cells.append(v_cells[vis_idx])

                    add_back_anims = [FadeIn(add_back_info, shift=UP * 0.1)]
                    temp_mobjs = [add_back_info]

                    if u_window_cells:
                        u_window_box = SurroundingRectangle(
                            VGroup(*u_window_cells),
                            color=C_HIGHLIGHT_R,
                            buff=0.06,
                            stroke_width=3,
                        )
                        add_back_anims.append(ShowCreation(u_window_box))
                        temp_mobjs.append(u_window_box)
                    else:
                        u_window_box = None

                    if v_window_cells:
                        v_window_box = SurroundingRectangle(
                            VGroup(*v_window_cells),
                            color=C_GRID_V,
                            buff=0.06,
                            stroke_width=3,
                        )
                        add_back_anims.append(ShowCreation(v_window_box))
                        temp_mobjs.append(v_window_box)
                    else:
                        v_window_box = None

                    if u_window_box is not None and v_window_box is not None:
                        add_back_arrow = CurvedArrow(
                            v_window_box.get_left() + DOWN * 0.02,
                            u_window_box.get_right() + DOWN * 0.02,
                            angle=-TAU / 6,
                            color=C_SURPLUS,
                            stroke_width=3,
                        )
                        add_back_anims.append(ShowCreation(add_back_arrow))
                        temp_mobjs.append(add_back_arrow)

                    self.play(*add_back_anims, run_time=0.7)
                    self.wait(0.6 * WAIT_SCALE_D + 2.0)
                    self.play(FadeOut(VGroup(*temp_mobjs)), run_time=0.3)

                # Sync U grid
                _, new_u_cells = self.build_grid(step["u_norm"], r"U_{norm}", C_GRID_U)
                # Position new cells to match old ones
                for i in range(len(u_cells)):
                    new_u_cells[i][-1].move_to(u_cells[i][0].get_center())

                # Animate replacing U: transform subtraction-result digits under U into new U digits.
                fades = []
                for i in range(len(u_cells)):
                    fades.append(FadeOut(u_cells[i][-1]))
                    if d3_result_digit_map is not None and i in d3_result_digit_map:
                        fades.append(TransformFromCopy(d3_result_digit_map[i], new_u_cells[i][-1]))
                    else:
                        fades.append(FadeIn(new_u_cells[i][-1]))
                self.play(*fades, run_time=0.8)
                for i in range(len(u_cells)):
                    new_u = new_u_cells[i][-1]
                    u_cells[i].add(new_u)

                if d3_subtract_mobj is not None:
                    self.play(FadeOut(d3_subtract_mobj), run_time=0.25)
                    d3_subtract_mobj = None
                if panel_step_mobj is not None:
                    self.play(FadeOut(panel_step_mobj), run_time=0.2)
                    panel_step_mobj = None
                d3_result_digit_map = None

                # Update Q cell
                q_vis = len(q_cells) - 1 - j
                old_q_cell = q_cells[q_vis]
                new_q_t = Tex(digit_to_symbol(q_hat)).scale(GRID_FONT_SCALE).set_color(C_GRID_Q)
                new_q_t.move_to(old_q_cell[0].get_center())

                if q_hat_fly_token is not None:
                    self.play(
                        FadeOut(old_q_cell[-1]),
                        Transform(q_hat_fly_token, new_q_t),
                        run_time=0.7,
                    )
                    old_q_cell.add(q_hat_fly_token)
                else:
                    self.play(FadeOut(old_q_cell[-1]), FadeIn(new_q_t), run_time=0.6)
                    old_q_cell.add(new_q_t)

                # Reset carry/subtract registers for next iteration (if panel enabled).
                if ENABLE_BORROW_CARRY_PANEL and carry_box is not None and surplus_box is not None:
                    new_carry_tex = Tex("0").scale(0.6).set_color(C_CARRY).move_to(carry_box)
                    new_surplus_tex = Tex("0").scale(0.6).set_color(C_HIGHLIGHT_Y).move_to(surplus_box)
                    self.play(
                        FadeOut(carry_val), FadeIn(new_carry_tex),
                        FadeOut(surplus_val), FadeIn(new_surplus_tex),
                        run_time=0.5,
                    )
                    carry_val = new_carry_tex
                    surplus_val = new_surplus_tex

                self.wait(0.8 * WAIT_SCALE)

            # ═══════════════════  FINISH  ═════════════════════════════════
            elif step["type"] == "finish":
                q_arr = step["q"]
                r_arr = step["remainder"]
                d_val = step["d"]
                base_val = step["base"]
                q_int = digits_le_to_int(q_arr, base_val)
                v_int = digits_le_to_int(v, base_val)
                r_int = digits_le_to_int(r_arr, base_val)
                u_int = digits_le_to_int(u, base_val)
                q_str = int_to_base_str(q_int, base_val)
                r_str = int_to_base_str(r_int, base_val)
                u_str_base = int_to_base_str(u_int, base_val)

                # Decimal interpretation of the raw input text (if valid),
                # used for the B10 row shown to learners.
                dec_input_ok = u_str.isdigit() and v_str.isdigit() and int(v_str) != 0
                if dec_input_ok:
                    u_dec_input = int(u_str)
                    v_dec_input = int(v_str)
                    q_dec_input, r_dec_input = divmod(u_dec_input, v_dec_input)
                else:
                    u_dec_input = None
                    v_dec_input = None
                    q_dec_input = None
                    r_dec_input = None


                # ── Phase 1: Close quotient loop before unnormalize ────────
                self.update_step_badge(f"Loop done  Q = {q_str}")

                # Highlight all Q cells
                q_highlights = [safe_highlight(q_cells[i], color=C_GRID_Q) for i in range(len(q_cells))]
                self.play(*q_highlights, run_time=1.0)
                self.wait(0.5 * WAIT_SCALE)


                # Hide D3/D4 overlays before showing D7 block to avoid overlap.
                pre_d7_fade = []
                if d4_work_mobj is not None:
                    pre_d7_fade.append(FadeOut(d4_work_mobj))
                    d4_work_mobj = None
                if d3_result_mobj is not None:
                    pre_d7_fade.append(FadeOut(d3_result_mobj))
                    d3_result_mobj = None
                if pre_d7_fade:
                    self.play(*pre_d7_fade, run_time=0.3)

                # ── Phase 2: D8 Unnormalize (Redesigned) ───────────────
                self.update_step_badge(f"D8  Unnormalize  (d = {d_val})")

                # Get the cells corresponding to the last n digits of U_norm
                rem_source_cells = []
                for idx in range(n - 1, -1, -1):
                    vis_idx = len(u_cells) - 1 - idx
                    if 0 <= vis_idx < len(u_cells):
                        rem_source_cells.append(u_cells[vis_idx])

                rem_window_box = None
                if rem_source_cells:
                    rem_window_box = SurroundingRectangle(
                        VGroup(*rem_source_cells),
                        color=C_SURPLUS,
                        buff=0.08,
                        stroke_width=4,
                    )
                    rem_window_box.set_fill(C_SURPLUS, opacity=0.12)

                # Show title formula
                unnorm_formula = Tex(
                    r"\text{D8: }r = \frac{U_{rem}}{d}",
                    color=C_FORMULA,
                    tex_to_color_map={
                        r"r": C_SURPLUS,
                        r"U_{rem}": C_GRID_U,
                        r"d": C_HIGHLIGHT_Y,
                    }
                ).scale(0.65)
                unnorm_formula.next_to(self.step_badge, DOWN, buff=0.25)
                unnorm_formula.set_x(0)

                # Specific computation formula
                # Note: step["u_norm"] is little-endian. We need to display MSD first.
                u_norm_display = digits_to_str(step["u_norm"][:n], base_val)[::-1] # digits_to_str returns little-endian string, we need reverse for display
                rem_digits = step["u_norm"][:n]
                u_norm_val = digits_le_to_int(rem_digits, base_val)
                u_norm_display = int_to_base_str(u_norm_val, base_val)

                numerator = Tex(u_norm_display).set_color(C_GRID_U)
                denominator = Tex(str(d_val)).set_color(C_HIGHLIGHT_Y)
                frac_line = Line(LEFT, RIGHT, color=C_FORMULA).set_width(max(numerator.get_width(), denominator.get_width()) + 0.2)
                
                frac_group = VGroup(numerator, frac_line, denominator).arrange(DOWN, buff=0.1)

                unnorm_eq = VGroup(
                    Tex(r"r").set_color(C_SURPLUS),
                    Tex(r"=").set_color(C_FORMULA),
                    frac_group,
                    Tex(r"=").set_color(C_FORMULA),
                    Tex(r_str).set_color(C_SURPLUS),
                ).arrange(RIGHT, buff=0.15).scale(0.85)
                unnorm_eq.next_to(unnorm_formula, DOWN, buff=0.25)
                unnorm_eq.set_x(0)
                
                # Align equation parts for sequential reveal
                eq_left = VGroup(unnorm_eq[0], unnorm_eq[1])
                eq_u = numerator
                eq_div = VGroup(frac_line, denominator)
                eq_res = VGroup(unnorm_eq[3], unnorm_eq[4])

                # Animate:
                # 1. Fade in the D8 formula title and the empty box
                self.play(FadeIn(unnorm_formula, shift=UP * 0.1), run_time=0.6)
                if rem_window_box is not None:
                    self.play(FadeIn(rem_window_box), run_time=0.4)
                self.wait(WAIT_SCALE)
                
                # 2. Fade in `r = `
                self.play(FadeIn(eq_left, shift=RIGHT * 0.1), run_time=0.5)
                
                # 3. Pull digits from U grid to form the U_norm_display (numerator)
                if rem_source_cells:
                    source_mobs = VGroup(*[c[-1] for c in rem_source_cells])
                    self.play(TransformFromCopy(source_mobs, eq_u), run_time=0.8)
                else:
                    self.play(FadeIn(eq_u), run_time=0.8)
                self.wait(0.5 * WAIT_SCALE)
                
                # 4. Highlight `d` requirement and fade in fraction line & denominator
                self.play(FadeIn(eq_div, shift=LEFT * 0.1), run_time=0.5)
                self.wait(WAIT_SCALE)
                
                # 5. Show final result 
                self.play(FadeIn(eq_res, shift=UP * 0.1), run_time=0.6)
                self.wait(3 * WAIT_SCALE)

                fade_items = [unnorm_formula, unnorm_eq]
                if rem_window_box is not None:
                    fade_items.append(rem_window_box)
                self.play(FadeOut(VGroup(*fade_items)), run_time=0.4)

                # ── Phase 3: Clear and show final result ──────────────────
                fade_targets = [side_panel, self.step_badge,
                                u_grp, v_grp, q_grp, division_lines,
                                carry_val, surplus_val,
                                d3_result_mobj, d4_work_mobj, d3_subtract_mobj, u_window_mobj, gen_formula_mobj,
                                panel_step_mobj]
                self.play(*[FadeOut(m) for m in fade_targets if m is not None], run_time=0.8)
                self.step_badge = None

                done_badge = Text("Done!", font_size=28, color=C_STEP)
                done_badge.to_edge(UP, buff=0.4).set_x(0)

                # Result card
                div_label = Text(f"{u_str_base} ÷ {v_str}", font_size=28, color=WHITE)
                eq_sign = Tex(r"=").scale(1.0).set_color(C_FORMULA)

                if base_val != 10:
                    q_dec_display = q_dec_input if dec_input_ok else q_int
                    q_result_dec = Text(
                        f"{q_dec_display} (B10)",
                        font_size=20,
                        color=C_DIM,
                    )
                    q_result_base = Text(
                        f"{q_str} (B{base_val})",
                        font_size=30,
                        color=C_DIGIT_Q,
                        weight=BOLD,
                    )
                    q_result = VGroup(q_result_dec, q_result_base).arrange(
                        DOWN, aligned_edge=LEFT, buff=0.08
                    )
                else:
                    q_result = Text(q_str, font_size=36, color=C_DIGIT_Q, weight=BOLD)

                top_row = VGroup(div_label, eq_sign, q_result).arrange(RIGHT, buff=0.3)

                r_label = Text("Remainder:", font_size=20, color=C_DIM)

                if base_val != 10:
                    r_dec_display = r_dec_input if dec_input_ok else r_int
                    r_value_dec = Text(
                        f"{r_dec_display} (B10)",
                        font_size=18,
                        color=C_DIM,
                    )
                    r_value_base = Text(
                        f"{r_str} (B{base_val})",
                        font_size=26,
                        color=C_SURPLUS,
                        weight=BOLD,
                    )
                    r_value = VGroup(r_value_dec, r_value_base).arrange(
                        DOWN, aligned_edge=LEFT, buff=0.08
                    )
                else:
                    r_value = Text(r_str, font_size=28, color=C_SURPLUS, weight=BOLD)

                remainder_row = VGroup(r_label, r_value).arrange(RIGHT, buff=0.2)

                result_group = VGroup(top_row, remainder_row).arrange(DOWN, buff=0.5)
                result_group.set_x(0).set_y(0.3)

                underline = Line(
                    result_group.get_corner(DL) + DOWN * 0.15 + LEFT * 0.1,
                    result_group.get_corner(DR) + DOWN * 0.15 + RIGHT * 0.1,
                    color=C_HIGHLIGHT_Y, stroke_width=2,
                )

                # Verification equation: q × v + r = u ✓
                verify_sum = q_int * v_int + r_int
                verify_ok = verify_sum == u_int
                verify_mark = r"\checkmark" if verify_ok else r"\times"
                verify_mark_color = "#00ff88" if verify_ok else C_HIGHLIGHT_R

                verify_eq_base = VGroup(
                    Tex(rf"\text{{(B{base_val})}}").set_color(C_DIM),
                    Tex(q_str).set_color(C_DIGIT_Q),
                    Tex(r"\times").set_color(C_FORMULA),
                    Tex(v_str).set_color(C_DIGIT_V),
                    Tex(r"+").set_color(C_FORMULA),
                    Tex(r_str).set_color(C_SURPLUS),
                    Tex(r"=").set_color(C_FORMULA),
                    Tex(int_to_base_str(verify_sum, base_val)).set_color(C_HIGHLIGHT_Y),
                    Tex(verify_mark).set_color(verify_mark_color),
                ).arrange(RIGHT, buff=0.15).scale(0.7)

                if base_val != 10:
                    if dec_input_ok:
                        verify_sum_dec = q_dec_input * v_dec_input + r_dec_input
                        verify_ok_dec = verify_sum_dec == u_dec_input
                    else:
                        verify_sum_dec = verify_sum
                        verify_ok_dec = verify_ok
                    verify_mark_dec = r"\checkmark" if verify_ok_dec else r"\times"
                    verify_mark_dec_color = "#00ff88" if verify_ok_dec else C_HIGHLIGHT_R

                    verify_eq_dec = VGroup(
                        Tex(r"\text{(B10)}").set_color(C_DIM),
                        Tex(str(q_dec_input if dec_input_ok else q_int)).set_color(C_DIGIT_Q),
                        Tex(r"\times").set_color(C_FORMULA),
                        Tex(str(v_dec_input if dec_input_ok else v_int)).set_color(C_DIGIT_V),
                        Tex(r"+").set_color(C_FORMULA),
                        Tex(str(r_dec_input if dec_input_ok else r_int)).set_color(C_SURPLUS),
                        Tex(r"=").set_color(C_FORMULA),
                        Tex(str(verify_sum_dec)).set_color(C_HIGHLIGHT_Y),
                        Tex(verify_mark_dec).set_color(verify_mark_dec_color),
                    ).arrange(RIGHT, buff=0.15).scale(0.62)
                    verify_eq = VGroup(verify_eq_dec, verify_eq_base).arrange(
                        DOWN, aligned_edge=LEFT, buff=0.12
                    )
                else:
                    verify_eq = verify_eq_base

                verify_eq.next_to(underline, DOWN, buff=0.5).set_x(0)

                self.play(FadeIn(done_badge, shift=DOWN * 0.2), run_time=0.6)
                self.play(
                    FadeIn(top_row, shift=UP * 0.3),
                    run_time=0.8,
                )
                self.play(
                    FadeIn(remainder_row, shift=UP * 0.2),
                    ShowCreation(underline),
                    run_time=0.8,
                )
                self.play(FadeIn(verify_eq, shift=UP * 0.2), run_time=0.8)
                self.wait(3 * WAIT_SCALE)
