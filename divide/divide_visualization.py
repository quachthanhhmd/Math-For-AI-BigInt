from manimlib import *

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

def knuth_algorithm_d_steps(u, v, base=10):
    steps = []
    
    u = u.copy()
    v = v.copy()
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
        "type": "normalize",
        "d": d,
        "u_norm": u_norm.copy(),
        "v_norm": v_norm.copy(),
    })
    
    for j in range(m, -1, -1):
        numerator = u_norm[j + n] * base + u_norm[j + n - 1]
        q_hat = numerator // v_norm[-1]
        r_hat = numerator % v_norm[-1]
        
        while q_hat == base or (q_hat * v_norm[-2] > base * r_hat + u_norm[j + n - 2]):
            q_hat -= 1
            r_hat += v_norm[-1]
            if r_hat >= base:
                break
                
        steps.append({
            "type": "estimate_q_hat",
            "j": j,
            "q_hat": q_hat,
            "numerator": numerator,
            "u_idx_1": j + n,
            "u_idx_2": j + n - 1,
            "v_idx": n - 1,
            "v_val_first": v_norm[-1]
        })
        
        carry = 0
        for i in range(n):
            steps.append({
                "type": "interaction_highlight",
                "u_idx": j + i,
                "v_idx": i
            })
            old_val = u_norm[j + i]
            v_val = v_norm[i]
            old_carry = carry
            temp = old_val - q_hat * v_val - old_carry
            u_norm[j + i] = temp % base
            carry = -(temp // base)
            steps.append({
                "type": "interaction_update",
                "u_idx": j + i,
                "v_idx": i,
                "old_val": old_val,
                "v_val": v_val,
                "q_hat": q_hat,
                "old_carry": old_carry,
                "new_carry": carry,
                "new_val": u_norm[j + i]
            })
                
        temp = u_norm[j + n] - carry
        
        if temp < 0:
            q_hat -= 1
            carry = 0
            for i in range(n):
                temp = u_norm[j + i] + v_norm[i] + carry
                u_norm[j + i] = temp % base
                carry = temp // base
            u_norm[j + n] += carry
            steps.append({
                "type": "add_back",
                "j": j,
                "u_norm": u_norm.copy(),
                "q_hat": q_hat
            })
        else:
            u_norm[j + n] = temp
            steps.append({
                "type": "subtract",
                "j": j,
                "u_norm": u_norm.copy(),
                "q_hat": q_hat
            })
            
        q[j] = q_hat
        
    remainder = []
    carry = 0
    for i in range(n - 1, -1, -1):
        temp = carry * base + u_norm[i]
        remainder.append(temp // d)
        carry = temp % d
    remainder.reverse()
    
    while len(q) > 1 and q[-1] == 0: q.pop()
    while len(remainder) > 1 and remainder[-1] == 0: remainder.pop()
    
    steps.append({
        "type": "finish",
        "q": q.copy(),
        "remainder": remainder.copy()
    })
    
    return steps

class DivisionScene(Scene):
    def construct(self):
        # We use a standard division 1234 / 56 as a demonstration
        u_str = "1234"
        v_str = "56"
        u = [int(c) for c in reversed(u_str)]
        v = [int(c) for c in reversed(v_str)]
        
        title = Text("Knuth Algorithm D Visualization").to_edge(UP)
        self.play(Write(title))
        
        u_text = Text(f"U (Số bị chia) = {u_str}")
        v_text = Text(f"V (Số chia)    = {v_str}")
        initial_group = VGroup(u_text, v_text).arrange(DOWN).next_to(title, DOWN, buff=1)
        
        self.play(FadeIn(initial_group))
        self.wait(1.5)
        
        steps = knuth_algorithm_d_steps(u, v)
        
        def get_array_mobj(arr, label_in):
            group = VGroup()
            if isinstance(label_in, str):
                label = Text(f"{label_in}: ")
            else:
                label = label_in
            
            label.scale(0.7)
            
            arr_group = VGroup()
            for x in reversed(arr):
                cell = VGroup()
                # Tạo một hình vuông đồng bộ cho từng ô
                box = Rectangle(width=0.7, height=1.0, color=BLUE)
                t = Tex(str(x))
                t.move_to(box.get_center())
                cell.add(box, t)
                arr_group.add(cell)
                
            # Đặt sát nhau bằng buff=0 để tạo giao diện lưới ngang
            arr_group.arrange(RIGHT, buff=0)
            
            group.add(label, arr_group)
            group.arrange(RIGHT, buff=0.5)
            return group, arr_group

        u_norm_mobj, u_arr = None, None
        v_norm_mobj, v_arr = None, None
        active_scene_group = VGroup()
        interaction_line = None
        gen_formula_mobj = None # Sẽ chứa công thức tổng quát phía dưới V_norm
        
        # Tạo Grid Panel cố định dọc bên trái cho Carry và Surplus (Dùng Tex cho giá trị)
        carry_label = Text("Carry:")
        carry_box = Rectangle(width=1.0, height=1.0, color=YELLOW)
        carry_val = Tex("0").move_to(carry_box.get_center())
        carry_group = VGroup(carry_label, VGroup(carry_box, carry_val)).arrange(RIGHT)
        
        surplus_label = Text("Surplus:")
        surplus_box = Rectangle(width=1.0, height=1.0, color=ORANGE)
        surplus_val = Tex("0").move_to(surplus_box.get_center())
        surplus_group = VGroup(surplus_label, VGroup(surplus_box, surplus_val)).arrange(RIGHT)
        
        side_panel = VGroup(carry_group, surplus_group).arrange(DOWN, buff=1.0).to_edge(RIGHT).shift(UP * 1.1)
        
        # Label hiển thị Cơ số B ở lề trái (Dùng Text để hỗ trợ tiếng Việt)
        base_label = Text("Cơ số (Base) B = 10").to_edge(LEFT).shift(UP * 1.1).set_color(BLUE).scale(0.8)
        
        for step in steps:
            if step["type"] == "normalize":
                u_norm_mobj, u_arr = get_array_mobj(step["u_norm"], Tex(r"U_{norm}"))
                v_norm_mobj, v_arr = get_array_mobj(step["v_norm"], Tex(r"V_{norm}"))
                
                new_scene_group = VGroup(u_norm_mobj, v_norm_mobj).arrange(DOWN, buff=1.5).move_to(UP * 1.1)
                
                self.play(FadeOut(initial_group))
                self.play(FadeIn(new_scene_group), FadeIn(side_panel), FadeIn(base_label))
                active_scene_group = new_scene_group
                self.wait(1.5)
                
            elif step["type"] == "estimate_q_hat":
                j = step["j"]
                
                u_vis_1 = len(u_arr) - 1 - step["u_idx_1"]
                u_vis_2 = len(u_arr) - 1 - step["u_idx_2"]
                v_vis = len(v_arr) - 1 - step["v_idx"]
                
                # Xây dựng công thức rời rạc (Atomic) để tránh lỗi broadcast shape và sai vị trí
                target_num = Tex(str(step['numerator'])).scale(1.2)
                target_den = Tex(str(step['v_val_first'])).scale(1.2)
                eq_parts = VGroup(
                    Tex(r"\lfloor").scale(1.2),
                    target_num,
                    Tex(r"/").scale(1.2),
                    target_den,
                    Tex(r"\rfloor").scale(1.2),
                    Tex(r"=").scale(1.2),
                    Tex(str(step['q_hat'])).scale(1.2)
                ).arrange(RIGHT, buff=0.2).next_to(side_panel, DOWN*1.5, buff=1.0)
                
                # Chuẩn bị bản sao để bay (points sẽ khớp vì đều là Tex)
                u1_copy = u_arr[u_vis_1][1].copy()
                u2_copy = u_arr[u_vis_2][1].copy()
                v1_copy = v_arr[v_vis][1].copy()
                
                # Thêm công thức tổng quát của bước ước lượng q_hat
                new_gen_formula = Tex(
                    r"\hat{q} = \min \left( \lfloor \frac{u_{j+n} B + u_{j+n-1}}{v_{n-1}} \rfloor, B-1 \right)"
                ).scale(0.8).next_to(v_norm_mobj, DOWN, buff=1.0)
                
                # Dùng FadeOut/FadeIn cho công thức tổng quát để tránh lỗi Shape Mismatch (ValueError)
                gen_anims = []
                if gen_formula_mobj is None:
                    gen_anims.append(FadeIn(new_gen_formula))
                else:
                    gen_anims.extend([FadeOut(gen_formula_mobj), FadeIn(new_gen_formula)])
                
                # Xác định các phần tĩnh của phương trình để hiện (trừ các số sẽ bay vào bằng ReplacementTransform)
                other_eq_parts = VGroup(*[p for p in eq_parts if p not in [target_num, target_den]])
                
                # Thực hiện bay và hiện dấu (Sử dụng Move-and-Fade để tránh tuyệt đối lỗi Shape Mismatch)
                self.play(
                    *gen_anims,
                    Indicate(u_arr[u_vis_1], color=YELLOW),
                    Indicate(u_arr[u_vis_2], color=YELLOW),
                    Indicate(v_arr[v_vis], color=YELLOW),
                    # Bay và mờ đi nguồn, đồng thời hiện đích
                    u1_copy.animate.move_to(target_num).set_opacity(0),
                    u2_copy.animate.move_to(target_num).set_opacity(0),
                    FadeIn(target_num),
                    v1_copy.animate.move_to(target_den).set_opacity(0),
                    FadeIn(target_den),
                    FadeIn(other_eq_parts),
                    run_time=1.5
                )
                gen_formula_mobj = new_gen_formula
                
                self.wait(1.5)
                self.play(FadeOut(eq_parts))
                
            elif step["type"] == "interaction_highlight":
                u_vis = len(u_arr) - 1 - step["u_idx"]
                v_vis = len(v_arr) - 1 - step["v_idx"]
                
                interaction_line = Line(u_arr[u_vis].get_bottom(), v_arr[v_vis].get_top(), color=RED)
                
                self.play(
                    Indicate(u_arr[u_vis][0], color=RED, scale_factor=1.1),
                    Indicate(v_arr[v_vis][0], color=RED, scale_factor=1.1),
                    ShowCreation(interaction_line),
                    run_time=1.5
                )
                
            elif step["type"] == "interaction_update":
                u_vis = len(u_arr) - 1 - step["u_idx"]
                v_vis = len(v_arr) - 1 - step["v_idx"]
                
                # Xây dựng công thức rời rạc (Atomic) để tránh lỗi shape mismatch
                t_val = step["old_val"] - step["q_hat"]*step["v_val"] - step["old_carry"]
                target_u = Tex(str(step["old_val"])).scale(0.9)
                target_v = Tex(str(step["v_val"])).scale(0.9)
                target_old_carry = Tex(str(step["old_carry"])).scale(0.9)
                target_result = Tex(str(t_val)).scale(0.9)
                
                parts = VGroup(
                    target_u,
                    Tex(r"-").scale(0.9),
                    Tex(str(step["q_hat"])).scale(0.9),
                    Tex(r"\times").scale(0.9),
                    target_v,
                    Tex(r"-").scale(0.9),
                    target_old_carry,
                    Tex(r"=").scale(0.9),
                    target_result
                ).arrange(RIGHT, buff=0.15).next_to(side_panel, DOWN, buff=1.0)
                
                # Bản sao bay từ Grid (U, V) và Panel (Carry)
                u_cell_copy = u_arr[u_vis][1].copy()
                v_cell_copy = v_arr[v_vis][1].copy()
                carry_val_copy = carry_val.copy() # Bay từ panel carry cũ
                
                # Chuẩn bị giá trị mới cho Panel (Dùng Tex)
                new_surplus_val_mobj = Tex(str(step['new_val'])).move_to(surplus_box.get_center())
                new_carry_val_mobj = Tex(str(step['new_carry'])).move_to(carry_box.get_center())
                
                # Thêm công thức tổng quát của bước trừ (D4)
                new_gen_formula = Tex(
                    r"u_{j+i} \leftarrow (u_{j+i} - \hat{q} \cdot v_i - c) \pmod{B}"
                ).scale(0.8).next_to(v_norm_mobj, DOWN, buff=1.0)
                
                # Dùng FadeOut/FadeIn cho công thức tổng quát để tránh lỗi Shape Mismatch (ValueError)
                gen_anims = []
                if gen_formula_mobj is None:
                    gen_anims.append(FadeIn(new_gen_formula))
                else:
                    gen_anims.extend([FadeOut(gen_formula_mobj), FadeIn(new_gen_formula)])
                
                # Xác định các phần tĩnh của phương trình để hiện
                other_parts = VGroup(*[p for p in parts if p not in [target_u, target_v, target_old_carry]])
                
                # Thực hiện bay và hiện dấu (Sử dụng Move-and-Fade để tránh lỗi Shape Mismatch)
                self.play(
                    *gen_anims,
                    u_cell_copy.animate.move_to(target_u).set_opacity(0),
                    FadeIn(target_u),
                    v_cell_copy.animate.move_to(target_v).set_opacity(0),
                    FadeIn(target_v),
                    carry_val_copy.animate.move_to(target_old_carry).set_opacity(0),
                    FadeIn(target_old_carry),
                    FadeIn(other_parts), # Hiện các dấu phép toán và biểu thức còn lại
                    run_time=1.5
                )
                gen_formula_mobj = new_gen_formula
                
                # Bước 2: Bay kết quả TỪ công thức RA LẠI bảng điều khiển
                # Tạo bản sao kết quả t_val để bay ra 2 hướng
                res_copy_1 = target_result.copy()
                res_copy_2 = target_result.copy()
                
                # Bay kết quả TỪ công thức RA LẠI bảng điều khiển (Dùng Move-and-Fade)
                self.play(
                    surplus_val.animate.set_opacity(0),
                    res_copy_1.animate.move_to(new_surplus_val_mobj).set_opacity(0),
                    FadeIn(new_surplus_val_mobj),
                    carry_val.animate.set_opacity(0),
                    res_copy_2.animate.move_to(new_carry_val_mobj).set_opacity(0),
                    FadeIn(new_carry_val_mobj),
                    run_time=1.5
                )
                
                # Cập nhật tham chiếu cho các lần sau
                surplus_val = new_surplus_val_mobj
                carry_val = new_carry_val_mobj
                
                # Cập nhật kết quả cuối cùng vào Grid U
                old_cell = u_arr[u_vis]
                box = old_cell[0]
                new_t = Tex(str(step["new_val"])).move_to(box.get_center())
                
                # Hiệu ứng đổi số trong lưới: Dùng FadeOut và FadeIn để tránh lỗi shape mismatch giữa các chữ số khác nhau
                animations = [
                    FadeOut(old_cell[1]),
                    FadeIn(new_t),
                    FadeOut(u_cell_copy),
                    FadeOut(v_cell_copy)
                ]
                if interaction_line is not None:
                    animations.append(FadeOut(interaction_line))
                    interaction_line = None
                
                self.play(*animations, run_time=1.5)
                # Cập nhật lại mảng submobjects của VGroup cell để các lần sau tham chiếu đúng
                old_cell.submobjects[1] = new_t 
                self.play(FadeOut(parts), run_time=1.5)
                
            elif step["type"] in ["subtract", "add_back"]:
                # To sync the whole visual array properly with the new u_norm just in case
                new_u_norm_mobj, new_u_arr = get_array_mobj(step["u_norm"], Tex(r"U_{norm}"))
                new_u_norm_mobj.move_to(u_norm_mobj.get_center())
                
                # Cập nhật Grid: Dùng FadeOut/FadeIn cho từng chữ số trong mảng
                fades = []
                for i in range(len(u_arr)):
                    fades.append(FadeOut(u_arr[i][1]))
                    fades.append(FadeIn(new_u_arr[i][1]))
                
                self.play(*fades, run_time=1.5)
                
                # Cập nhật tham chiếu cho u_arr[i][1] trong submobjects để các bước sau dùng đúng text đang hiển thị
                for i in range(len(u_arr)):
                    u_arr[i].submobjects[1] = new_u_arr[i][1]
                
                self.wait(1.5)
                
            elif step["type"] == "finish":
                q_str = "".join(str(x) for x in reversed(step['q']))
                r_str = "".join(str(x) for x in reversed(step['remainder']))
                ans_text = Text(f"Xong! Thương số Q = {q_str}, Số dư R = {r_str}").next_to(active_scene_group, DOWN, buff=1.5)
                ans_text.set_color(YELLOW)
                
                self.play(Write(ans_text))
                self.wait(4)
