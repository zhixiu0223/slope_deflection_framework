import numpy as np
import sympy as sp

from sd_framework import SlopeDeflectionProblem


class TwoStoryFrameProblem(SlopeDeflectionProblem):
    """
    Case-05：二層對稱剛架 (Two-Story Symmetric Frame)
    節點: A,F底層固定; B,E一樓樓板高度(H1); C,D屋頂高度(H1+H2)
    柱: AB(一樓左), FE(一樓右), BC(二樓左), ED(二樓右)
    梁: BE(一樓梁,均佈載重w1), CD(屋頂梁,均佈載重w2)

    結構對稱、載重對稱(w1、w2左右一致) -> 無側移(psi=0全部柱子)，
    4個未知數 theta_B, theta_C, theta_D, theta_E(不假設對稱關係，
    讓方程式自己解出來——解出來會自動呈現 theta_B=-theta_E,
    theta_C=-theta_D 這種鏡像關係，不用事先假設)。

    FEM慣例：近端負、遠端正(傳統教科書慣例)，跟Case-01~04.5統一。
    """

    def __init__(self, H1=4.0, H2=3.5, L=6.0, w1=24.0, w2=18.0, EI_numeric=15000.0):
        self.H1, self.H2, self.L, self.w1, self.w2 = H1, H2, L, w1, w2
        self.EI = sp.Symbol('EI', positive=True, real=True)
        (self.theta_B, self.theta_C, self.theta_D, self.theta_E) = sp.symbols(
            'theta_B theta_C theta_D theta_E', real=True)
        self.EI_numeric = EI_numeric

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B, '\\theta_C': self.theta_C,
                '\\theta_D': self.theta_D, '\\theta_E': self.theta_E}

    def describe(self):
        return (f"**一樓層高** $H_1={self.H1}$ m，**二樓層高** $H_2={self.H2}$ m，"
                f"**跨度** $L={self.L}$ m\n\n"
                f"**一樓梁均佈載重** $w_1={self.w1}$ kN/m，"
                f"**屋頂梁均佈載重** $w_2={self.w2}$ kN/m\n\n"
                f"**邊界條件：** A、F兩端固定 ($\\theta_A=\\theta_F=0$)")

    def describe_dof(self):
        return (f"結構左右對稱、載重也左右對稱(w1、w2都是左右一致的均佈載重)，"
                f"所以**整體無側移**(兩層樓的側移角都是0，不用額外設Δ這個"
                f"未知量)——這點跟Case-04(側移剛架)不同，反而更接近Case-03的"
                f"情況，只是多了一層樓、多了兩個轉角未知量。\n\n"
                f"四個梁柱交會的剛性節點 B、C、D、E 各自有一個轉角未知量，"
                f"**不假設對稱關係**(不預設 $\\theta_B=-\\theta_E$ 這種鏡像"
                f"關係)，讓四條節點力矩平衡方程式自己解出來——解出來的結果"
                f"會自然呈現這種鏡像對稱，這是驗證答案合理性的依據，不是"
                f"事先假設的捷徑。共 $\\theta_B,\\theta_C,\\theta_D,\\theta_E$ "
                f"四個未知位移量。")

    def draw_geometry(self, ax):
        H1, H2, L = self.H1, self.H2, self.L
        Htot = H1 + H2
        ax.plot([0, 0], [0, Htot], 'k-', lw=3)
        ax.plot([L, L], [0, Htot], 'k-', lw=3)
        ax.plot([0, L], [H1, H1], 'k-', lw=3)
        ax.plot([0, L], [Htot, Htot], 'k-', lw=3)
        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)
        ax.text(0, -0.5, 'A (Fixed)', ha='center', fontsize=9, fontweight='bold')
        ax.text(L, -0.5, 'F (Fixed)', ha='center', fontsize=9, fontweight='bold')
        for x, y, name in [(0, H1, 'B'), (L, H1, 'E'), (0, Htot, 'C'), (L, Htot, 'D')]:
            ax.text(x, y + 0.25, name, fontsize=11, fontweight='bold', ha='center')

        w1, w2 = self.w1, self.w2
        for xx in np.linspace(0.3, L - 0.3, 7):
            ax.annotate('', xy=(xx, H1 + 0.05), xytext=(xx, H1 + 0.45),
                        arrowprops=dict(arrowstyle='->', color='crimson', lw=1.1))
        ax.text(L / 2, H1 + 0.65, f'$w_1={w1}$ kN/m', color='crimson', ha='center', fontsize=9)
        for xx in np.linspace(0.3, L - 0.3, 7):
            ax.annotate('', xy=(xx, Htot + 0.05), xytext=(xx, Htot + 0.45),
                        arrowprops=dict(arrowstyle='->', color='crimson', lw=1.1))
        ax.text(L / 2, Htot + 0.65, f'$w_2={w2}$ kN/m', color='crimson', ha='center', fontsize=9)

        # DOF箭頭: 統一順時針、黑色粗體，放在節點外側(B,C在左邊外側; D,E在右邊外側)
        # 修正: 上一版side的正負號算反了，箭頭反而畫到構架內側、擠在一起，
        # 這次直接照Case-04已經驗證過的座標寫法(不共用公式，避免再算錯)
        for x, y, name, side in [(0, H1, r'$\theta_B$', -1), (0, Htot, r'$\theta_C$', -1),
                                   (L, Htot, r'$\theta_D$', 1), (L, H1, r'$\theta_E$', 1)]:
            if side < 0:  # 左側(B,C): 箭頭從外面(更遠)畫向裡面(靠近節點)
                x_far, x_near = x - 1.5, x - 0.9
            else:  # 右側(D,E): 箭頭從裡面(靠近節點)畫向外面(更遠)
                x_far, x_near = x + 1.5, x + 0.9
            xytext_x, xy_x = (x_far, x_near) if side < 0 else (x_near, x_far)
            ax.annotate('', xy=(xy_x, y), xytext=(xytext_x, y),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                         color='black', lw=1.6))
            ax.text(x_far + 0.4 * side, y, name, color='black', fontweight='bold',
                    fontsize=10, ha='right' if side < 0 else 'left', va='center')

        ax.set_xlim(-2.6, L + 2.6)
        ax.set_ylim(-1, Htot + 1.3)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: Two-Story Frame — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, H1, H2, L, w1, w2 = self.EI, self.H1, self.H2, self.L, self.w1, self.w2
        thB, thC, thD, thE = self.theta_B, self.theta_C, self.theta_D, self.theta_E
        FEM_BE, FEM_EB = -w1 * L**2 / 12, w1 * L**2 / 12
        FEM_CD, FEM_DC = -w2 * L**2 / 12, w2 * L**2 / 12
        return {
            'M_{AB}': 2 * EI / H1 * thB,
            'M_{BA}': 2 * EI / H1 * (2 * thB),
            'M_{BC}': 2 * EI / H2 * (2 * thB + thC),
            'M_{CB}': 2 * EI / H2 * (thB + 2 * thC),
            'M_{CD}': 2 * EI / L * (2 * thC + thD) + FEM_CD,
            'M_{DC}': 2 * EI / L * (thC + 2 * thD) + FEM_DC,
            'M_{DE}': 2 * EI / H2 * (2 * thD + thE),
            'M_{ED}': 2 * EI / H2 * (thD + 2 * thE),
            'M_{BE}': 2 * EI / L * (2 * thB + thE) + FEM_BE,
            'M_{EB}': 2 * EI / L * (thB + 2 * thE) + FEM_EB,
            'M_{EF}': 2 * EI / H1 * (2 * thE),
            'M_{FE}': 2 * EI / H1 * thE,
        }

    def build_equilibrium_equations(self, moments):
        eq1 = sp.Eq(moments['M_{BA}'] + moments['M_{BC}'] + moments['M_{BE}'], 0)
        eq2 = sp.Eq(moments['M_{CB}'] + moments['M_{CD}'], 0)
        eq3 = sp.Eq(moments['M_{DC}'] + moments['M_{DE}'], 0)
        eq4 = sp.Eq(moments['M_{EF}'] + moments['M_{ED}'] + moments['M_{EB}'], 0)
        return [
            ("節點 B 力矩平衡 ΣM_B=0（柱AB、柱BC、梁BE交會） M_BA+M_BC+M_BE=0", eq1),
            ("節點 C 力矩平衡 ΣM_C=0（柱BC與梁CD交會） M_CB+M_CD=0", eq2),
            ("節點 D 力矩平衡 ΣM_D=0（梁CD與柱ED交會） M_DC+M_DE=0", eq3),
            ("節點 E 力矩平衡 ΣM_E=0（柱FE、柱ED、梁BE交會） M_EF+M_ED+M_EB=0", eq4),
        ]

    def compute_reactions(self, moments_val):
        H1 = self.H1
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_fe, m_ef = moments_val['M_{FE}'], moments_val['M_{EF}']
        return {'H_A (kN)': (m_ab + m_ba) / H1, 'H_F (kN)': (m_fe + m_ef) / H1}

    def draw_sfd(self, ax, moments_val):
        from sd_framework import member_shear_curve, member_offset_curve
        H1, H2, L = self.H1, self.H2, self.L
        Htot = H1 + H2
        mv = moments_val
        scale = 0.04

        ax.plot([0, 0], [0, Htot], 'k-', lw=3, label='Frame Structure')
        ax.plot([L, L], [0, Htot], 'k-', lw=3)
        ax.plot([0, L], [H1, H1], 'k-', lw=3)
        ax.plot([0, L], [Htot, Htot], 'k-', lw=3)

        members = [
            ('AB', 0, 0, 0, H1, H1, 0.0, mv['M_{AB}'], mv['M_{BA}']),
            ('BC', 0, H1, 0, Htot, H2, 0.0, mv['M_{BC}'], mv['M_{CB}']),
            ('BE', 0, H1, L, H1, L, self.w1, mv['M_{BE}'], mv['M_{EB}']),
            ('CD', 0, Htot, L, Htot, L, self.w2, mv['M_{CD}'], mv['M_{DC}']),
            ('ED', L, H1, L, Htot, H2, 0.0, mv['M_{ED}'], mv['M_{DE}']),
            ('FE', L, 0, L, H1, H1, 0.0, mv['M_{FE}'], mv['M_{EF}']),
        ]
        all_x, all_y = [0, L], [0, Htot]
        for name, x0, y0, x1, y1, length, w_load, m_near, m_far in members:
            s = np.linspace(0, length, 150)
            v = member_shear_curve(s, length, w_load, -m_near, m_far)
            xs, ys = member_offset_curve(x0, y0, x1, y1, s, v, scale)
            ax.plot(xs, ys, 'b-', lw=1.8)
            ax.fill(np.append(xs, [x1, x0]), np.append(ys, [y1, y0]), color='blue', alpha=0.15)
            ax.text(xs[0], ys[0], f'{v[0]:.1f}', color='darkblue', fontsize=7)
            ax.text(xs[-1], ys[-1], f'{v[-1]:.1f}', color='darkblue', fontsize=7)
            all_x.extend(xs); all_y.extend(ys)

        all_x, all_y = np.array(all_x), np.array(all_y)
        pad_x = max(0.15 * (all_x.max() - all_x.min()), 1.0)
        pad_y = max(0.15 * (all_y.max() - all_y.min()), 0.5)
        ax.set_xlim(all_x.min() - pad_x, all_x.max() + pad_x)
        ax.set_ylim(all_y.min() - pad_y, all_y.max() + pad_y)
        ax.set_aspect('equal')
        ax.set_title('Figure: Shear Force Diagram (SFD) [kN]')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve, member_offset_curve
        H1, H2, L = self.H1, self.H2, self.L
        Htot = H1 + H2
        mv = moments_val
        scale = 0.045

        ax.plot([0, 0], [0, Htot], 'k-', lw=3, label='Frame Structure')
        ax.plot([L, L], [0, Htot], 'k-', lw=3)
        ax.plot([0, L], [H1, H1], 'k-', lw=3)
        ax.plot([0, L], [Htot, Htot], 'k-', lw=3)

        members = [
            (0, 0, 0, H1, H1, 0.0, mv['M_{AB}'], mv['M_{BA}']),
            (0, H1, 0, Htot, H2, 0.0, mv['M_{BC}'], mv['M_{CB}']),
            (0, H1, L, H1, L, self.w1, mv['M_{BE}'], mv['M_{EB}']),
            (0, Htot, L, Htot, L, self.w2, mv['M_{CD}'], mv['M_{DC}']),
            (L, H1, L, Htot, H2, 0.0, mv['M_{ED}'], mv['M_{DE}']),
            (L, 0, L, H1, H1, 0.0, mv['M_{FE}'], mv['M_{EF}']),
        ]
        all_x, all_y = [0, L], [0, Htot]
        for x0, y0, x1, y1, length, w_load, m_near, m_far in members:
            s = np.linspace(0, length, 200)
            m = member_moment_curve(s, length, w_load, -m_near, m_far)
            xs, ys = member_offset_curve(x0, y0, x1, y1, s, m, scale)
            ax.plot(xs, ys, 'r--', lw=1.8)
            ax.fill(np.append(xs, [x1, x0]), np.append(ys, [y1, y0]), color='red', alpha=0.15)
            ax.text(xs[0], ys[0], f'{m[0]:.1f}', color='darkred', fontsize=7)
            ax.text(xs[-1], ys[-1], f'{m[-1]:.1f}', color='darkred', fontsize=7)
            all_x.extend(xs); all_y.extend(ys)

            # 跨內極值(只有梁BE、CD這種有均佈載重的桿件才會在跨內出現極值，
            # 柱子沒有跨間載重、極值一定在端點，不用另外標)
            if w_load:
                i_peak = int(np.argmin(m)) if m[len(m) // 2] < 0 else int(np.argmax(m))
                s_peak = s[i_peak]
                offset = -14 if ys[i_peak] <= (y0 + y1) / 2 else 14
                ax.annotate(f'{m[i_peak]:.1f} (s={s_peak:.2f}m)',
                            xy=(xs[i_peak], ys[i_peak]), fontsize=7.5, color='darkred',
                            fontweight='bold', ha='center',
                            xytext=(0, offset), textcoords='offset points',
                            arrowprops=dict(arrowstyle='-', color='darkred', lw=0.6))

        all_x, all_y = np.array(all_x), np.array(all_y)
        pad_x = max(0.15 * (all_x.max() - all_x.min()), 1.0)
        pad_y = max(0.15 * (all_y.max() - all_y.min()), 0.5)
        ax.set_xlim(all_x.min() - pad_x, all_x.max() + pad_x)
        ax.set_ylim(all_y.min() - pad_y, all_y.max() + pad_y)
        ax.set_aspect('equal')
        ax.set_title('Figure: Bending Moment Diagram (BMD) [kN·m]')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_tension_side(self, ax, moments_val):
        H1, H2, L = self.H1, self.H2, self.L
        Htot = H1 + H2
        mv = moments_val
        ax.plot([0, 0], [0, Htot], 'k-', lw=4)
        ax.plot([L, L], [0, Htot], 'k-', lw=4)
        ax.plot([0, L], [H1, H1], 'k-', lw=4)
        ax.plot([0, L], [Htot, Htot], 'k-', lw=4)

        labels = [
            (0, 0, 0, 1, -mv['M_{AB}']), (0, H1, 0, 1, mv['M_{BA}']),
            (0, H1, 0, 1, -mv['M_{BC}']), (0, Htot, 0, 1, mv['M_{CB}']),
            (0, H1, 1, 0, -mv['M_{BE}']), (L, H1, 1, 0, mv['M_{EB}']),
            (0, Htot, 1, 0, -mv['M_{CD}']), (L, Htot, 1, 0, mv['M_{DC}']),
            (L, H1, 0, 1, -mv['M_{ED}']), (L, Htot, 0, 1, mv['M_{DE}']),
            (L, 0, 0, 1, -mv['M_{FE}']), (L, H1, 0, 1, mv['M_{EF}']),
        ]
        for x, y, dx, dy, val in labels:
            perp_x, perp_y = -dy, dx
            sign = 1 if val > 0 else -1
            tx, ty = x + perp_x * sign * 0.7, y + perp_y * sign * 0.7
            ax.annotate('T', xy=(x, y), xytext=(tx, ty), color='red',
                        fontsize=8, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color='red', lw=1))

        ax.set_xlim(-2, L + 2)
        ax.set_ylim(-1, Htot + 1)
        ax.set_aspect('equal')
        ax.set_title('Figure: Tension Side by Member (T=Tension)')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_deformed_shape(self, ax, moments_val, solution):
        from sd_framework import member_offset_curve
        H1, H2, L = self.H1, self.H2, self.L
        Htot = H1 + H2
        mv = moments_val
        EI_val = self.EI_numeric
        thB = float(solution[self.theta_B].subs(self.EI, EI_val))
        thC = float(solution[self.theta_C].subs(self.EI, EI_val))

        def transverse_u(s_arr, M_i, M_j, length, w_load, u0, up0):
            C1 = (M_j - M_i - 0.5 * w_load * length**2) / length
            return (u0 + up0 * s_arr + (1.0 / EI_val) *
                    (-M_i * s_arr**2 / 2 - C1 * s_arr**3 / 6 - w_load * s_arr**4 / 24))

        def two_point_bc_u(M_i, M_j, length, w_load):
            """給兩端都已知u=0(無側移)的柱子用: 不用theta, 直接解u(0)=u(length)=0"""
            C1 = (M_j - M_i - 0.5 * w_load * length**2) / length

            def particular(s):
                return (1.0 / EI_val) * (-M_i * s**2 / 2 - C1 * s**3 / 6 - w_load * s**4 / 24)
            up0 = -particular(length) / length
            s_arr = np.linspace(0, length, 60)
            return s_arr, transverse_u(s_arr, M_i, M_j, length, w_load, 0.0, up0)

        scale = 100
        s_AB, u_AB = two_point_bc_u(-mv['M_{AB}'], mv['M_{BA}'], H1, 0.0)
        s_BC, u_BC = two_point_bc_u(-mv['M_{BC}'], mv['M_{CB}'], H2, 0.0)
        s_ED, u_ED = two_point_bc_u(-mv['M_{ED}'], mv['M_{DE}'], H2, 0.0)
        s_FE, u_FE = two_point_bc_u(-mv['M_{FE}'], mv['M_{EF}'], H1, 0.0)

        s_BE = np.linspace(0, L, 100)
        u_BE = transverse_u(s_BE, -mv['M_{BE}'], mv['M_{EB}'], L, self.w1, u0=0, up0=-thB)
        s_CD = np.linspace(0, L, 100)
        u_CD = transverse_u(s_CD, -mv['M_{CD}'], mv['M_{DC}'], L, self.w2, u0=0, up0=-thC)

        x_AB, y_AB = member_offset_curve(0, 0, 0, H1, s_AB, u_AB, scale)
        x_BC, y_BC = member_offset_curve(0, H1, 0, Htot, s_BC, u_BC, scale)
        x_BE, y_BE = member_offset_curve(0, H1, L, H1, s_BE, u_BE, scale)
        x_CD, y_CD = member_offset_curve(0, Htot, L, Htot, s_CD, u_CD, scale)
        x_ED, y_ED = member_offset_curve(L, H1, L, Htot, s_ED, u_ED, scale)
        x_FE, y_FE = member_offset_curve(L, 0, L, H1, s_FE, u_FE, scale)

        ax.plot([0, 0], [0, Htot], '--', color='gray', lw=1.5, label='Original Structure')
        ax.plot([L, L], [0, Htot], '--', color='gray', lw=1.5)
        ax.plot([0, L], [H1, H1], '--', color='gray', lw=1.5)
        ax.plot([0, L], [Htot, Htot], '--', color='gray', lw=1.5)
        for xs, ys in [(x_AB, y_AB), (x_BC, y_BC), (x_BE, y_BE), (x_CD, y_CD), (x_ED, y_ED), (x_FE, y_FE)]:
            ax.plot(xs, ys, 'b-', lw=2)

        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)

        ax.set_xlim(-2, L + 2)
        ax.set_ylim(-1, Htot + 1.5)
        ax.set_aspect('equal')
        ax.set_title(f'Two-Story Frame: Original vs Deformed Shape (x{scale} scale)')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=1)
        ax.grid(True, linestyle='--', alpha=0.4)
        return True
