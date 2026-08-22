import numpy as np
import sympy as sp

from sd_framework import SlopeDeflectionProblem


class TwoStorySwayFrameProblem(SlopeDeflectionProblem):
    """
    Case-06：二層剛架 + 側移 (Two-Story Sway Frame)
    跟Case-05同樣的拓樸(A,F底層固定; B,E一樓; C,D屋頂)，但這次承受水平
    載重(P1在一樓樓板高度、P2在屋頂高度)，不對稱，會側移。

    **這是比Case-04(單層側移)更嚴謹的做法**：二層樓不對稱側移時，
    每一層樓各自有一個側移角(ψ1、ψ2，層間位移不一定相同)，不能只用
    一個共用的ψ——這樣總共 4個轉角 + 2個側移角 = 6個未知數，比
    ROADMAP原本規劃的4個更嚴謹、更真實對應二層剛架側移的物理行為。

    所有柱子統一「由下往上」定義近端/遠端(近端=下方，跟Case-04一致)——
    這點特別要注意跟Case-05不一樣：Case-05的柱ED是「由上往下」定義
    (近端=D在上方)，那個案例因為無側移(ψ=0)所以不影響結果，但這裡有
    側移，近遠端方向沒統一的話ψ的正負號會搞混，所以Case-06全部改成
    統一由下往上。

    FEM慣例：近端負、遠端正，跟Case-01~05統一。梁上可選擇加均佈載重
    w1、w2(預設0)，可以疊加組合載重(側移+跨間載重)。
    """

    def __init__(self, H1=4.0, H2=3.5, L=6.0, P1=15.0, P2=10.0,
                 w1=0.0, w2=0.0, EI_numeric=15000.0):
        self.H1, self.H2, self.L = H1, H2, L
        self.P1, self.P2, self.w1, self.w2 = P1, P2, w1, w2
        self.EI = sp.Symbol('EI', positive=True, real=True)
        (self.theta_B, self.theta_C, self.theta_D, self.theta_E,
         self.psi1, self.psi2) = sp.symbols(
            'theta_B theta_C theta_D theta_E psi1 psi2', real=True)
        self.EI_numeric = EI_numeric

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B, '\\theta_C': self.theta_C,
                '\\theta_D': self.theta_D, '\\theta_E': self.theta_E,
                '\\psi_1': self.psi1, '\\psi_2': self.psi2}

    def describe(self):
        w_desc = ""
        if self.w1:
            w_desc += f"，**一樓梁均佈載重** $w_1={self.w1}$ kN/m"
        if self.w2:
            w_desc += f"，**屋頂梁均佈載重** $w_2={self.w2}$ kN/m"
        return (f"**一樓層高** $H_1={self.H1}$ m，**二樓層高** $H_2={self.H2}$ m，"
                f"**跨度** $L={self.L}$ m\n\n"
                f"**一樓樓板水平力** $P_1={self.P1}$ kN，"
                f"**屋頂水平力** $P_2={self.P2}$ kN{w_desc}\n\n"
                f"**邊界條件：** A、F兩端固定 ($\\theta_A=\\theta_F=0$)")

    def describe_dof(self):
        return (f"水平力 P1、P2 讓構架側移，而且**兩層樓的側移量不一定"
                f"相同**——不能只用一個共用的側移角(那是單層剛架Case-04"
                f"的做法)，二層樓要各自設一個側移角：$\\psi_1=\\Delta_1/H_1$"
                f"(一樓層間側移角)、$\\psi_2=\\Delta_2/H_2$(二樓層間側移角，"
                f"$\\Delta_2$ 是C、D相對於B、E的相對側移量，不是C、D的絕對"
                f"側移)。加上四個節點轉角 $\\theta_B,\\theta_C,\\theta_D,"
                f"\\theta_E$，共 **6個未知位移量**——這是本Case的關鍵、也是"
                f"跟Case-04(只有1個ψ)、Case-05(4個轉角但無側移)最大的"
                f"差異：兩者的特性這裡同時出現。\n\n"
                f"對應**六條方程式**：四個節點力矩平衡(ΣM_B=ΣM_C=ΣM_D="
                f"ΣM_E=0) + 兩條樓層剪力平衡(每一層樓的柱子剪力總和要"
                f"跟該層樓「以上」所有水平力平衡)。")

    def draw_geometry(self, ax):
        H1, H2, L, P1, P2 = self.H1, self.H2, self.L, self.P1, self.P2
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
        if w1:
            for xx in np.linspace(0.3, L - 0.3, 7):
                ax.annotate('', xy=(xx, H1 + 0.05), xytext=(xx, H1 + 0.4),
                            arrowprops=dict(arrowstyle='->', color='crimson', lw=1.0))
            ax.text(L / 2, H1 + 0.55, f'$w_1={w1}$ kN/m', color='crimson', ha='center', fontsize=8)
        if w2:
            for xx in np.linspace(0.3, L - 0.3, 7):
                ax.annotate('', xy=(xx, Htot + 0.05), xytext=(xx, Htot + 0.4),
                            arrowprops=dict(arrowstyle='->', color='crimson', lw=1.0))
            ax.text(L / 2, Htot + 0.55, f'$w_2={w2}$ kN/m', color='crimson', ha='center', fontsize=8)

        # 水平力: 畫在節點左邊、比節點高一點，箭頭指入節點(避免跟同一側的
        # DOF箭頭/文字擠在同一個高度)
        ax.annotate('', xy=(0.0, H1 + 0.35), xytext=(-1.1, H1 + 0.35),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.2))
        ax.text(-1.2, H1 + 0.35, f'$P_1={P1}$', color='red', ha='right', va='center', fontsize=10)
        ax.annotate('', xy=(0.0, Htot + 0.35), xytext=(-1.1, Htot + 0.35),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.2))
        ax.text(-1.2, Htot + 0.35, f'$P_2={P2}$', color='red', ha='right', va='center', fontsize=10)

        # DOF箭頭: 統一順時針、黑色粗體，放在節點外側
        for x, y, name, side in [(0, H1, r'$\theta_B$', -1), (0, Htot, r'$\theta_C$', -1),
                                   (L, Htot, r'$\theta_D$', 1), (L, H1, r'$\theta_E$', 1)]:
            if side < 0:
                x_far, x_near = x - 1.5, x - 0.9
            else:
                x_far, x_near = x + 1.5, x + 0.9
            xytext_x, xy_x = (x_far, x_near) if side < 0 else (x_near, x_far)
            ax.annotate('', xy=(xy_x, y), xytext=(xytext_x, y),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                         color='black', lw=1.6))
            ax.text(x_far + 0.4 * side, y, name, color='black', fontweight='bold',
                    fontsize=10, ha='right' if side < 0 else 'left', va='center')

        # psi1, psi2 側移角標示: 水平箭頭, 畫在跨中
        mid_x = L / 2
        ax.annotate('', xy=(mid_x + 0.6, H1 / 2), xytext=(mid_x - 0.6, H1 / 2),
                    arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.6))
        ax.text(mid_x, H1 / 2 + 0.25, r'$\psi_1=\Delta_1/H_1$', color='darkorange',
                fontsize=9, ha='center')
        ax.annotate('', xy=(mid_x + 0.6, H1 + H2 / 2), xytext=(mid_x - 0.6, H1 + H2 / 2),
                    arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.6))
        ax.text(mid_x, H1 + H2 / 2 + 0.25, r'$\psi_2=\Delta_2/H_2$', color='darkorange',
                fontsize=9, ha='center')

        ax.set_xlim(-2.6, L + 2.6)
        ax.set_ylim(-1, Htot + 1.3)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: Two-Story Sway Frame — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, H1, H2, L, w1, w2 = self.EI, self.H1, self.H2, self.L, self.w1, self.w2
        thB, thC, thD, thE = self.theta_B, self.theta_C, self.theta_D, self.theta_E
        psi1, psi2 = self.psi1, self.psi2
        FEM_BE, FEM_EB = -w1 * L**2 / 12, w1 * L**2 / 12
        FEM_CD, FEM_DC = -w2 * L**2 / 12, w2 * L**2 / 12
        return {
            'M_{AB}': 2 * EI / H1 * (thB - 3 * psi1),
            'M_{BA}': 2 * EI / H1 * (2 * thB - 3 * psi1),
            'M_{FE}': 2 * EI / H1 * (thE - 3 * psi1),
            'M_{EF}': 2 * EI / H1 * (2 * thE - 3 * psi1),
            'M_{BC}': 2 * EI / H2 * (2 * thB + thC - 3 * psi2),
            'M_{CB}': 2 * EI / H2 * (thB + 2 * thC - 3 * psi2),
            'M_{ED}': 2 * EI / H2 * (2 * thE + thD - 3 * psi2),
            'M_{DE}': 2 * EI / H2 * (thE + 2 * thD - 3 * psi2),
            'M_{BE}': 2 * EI / L * (2 * thB + thE) + FEM_BE,
            'M_{EB}': 2 * EI / L * (thB + 2 * thE) + FEM_EB,
            'M_{CD}': 2 * EI / L * (2 * thC + thD) + FEM_CD,
            'M_{DC}': 2 * EI / L * (thC + 2 * thD) + FEM_DC,
        }

    def build_equilibrium_equations(self, moments):
        H1, H2, P1, P2 = self.H1, self.H2, self.P1, self.P2
        eq1 = sp.Eq(moments['M_{BA}'] + moments['M_{BC}'] + moments['M_{BE}'], 0)
        eq2 = sp.Eq(moments['M_{CB}'] + moments['M_{CD}'], 0)
        eq3 = sp.Eq(moments['M_{DC}'] + moments['M_{DE}'], 0)
        eq4 = sp.Eq(moments['M_{EF}'] + moments['M_{ED}'] + moments['M_{EB}'], 0)
        eq5 = sp.Eq((moments['M_{AB}'] + moments['M_{BA}']) / H1 +
                     (moments['M_{FE}'] + moments['M_{EF}']) / H1 + P1 + P2, 0)
        eq6 = sp.Eq((moments['M_{BC}'] + moments['M_{CB}']) / H2 +
                     (moments['M_{ED}'] + moments['M_{DE}']) / H2 + P2, 0)
        return [
            ("節點 B 力矩平衡 ΣM_B=0 M_BA+M_BC+M_BE=0", eq1),
            ("節點 C 力矩平衡 ΣM_C=0 M_CB+M_CD=0", eq2),
            ("節點 D 力矩平衡 ΣM_D=0 M_DC+M_DE=0", eq3),
            ("節點 E 力矩平衡 ΣM_E=0 M_EF+M_ED+M_EB=0", eq4),
            ("一樓層剪力平衡（一樓以上所有水平力P1+P2要跟一樓兩柱剪力平衡）"
             " (M_AB+M_BA)/H1+(M_FE+M_EF)/H1+P1+P2=0", eq5),
            ("二樓層剪力平衡（只有屋頂P2在二樓層之上）"
             " (M_BC+M_CB)/H2+(M_ED+M_DE)/H2+P2=0", eq6),
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
            (0, 0, 0, H1, H1, 0.0, mv['M_{AB}'], mv['M_{BA}']),
            (0, H1, 0, Htot, H2, 0.0, mv['M_{BC}'], mv['M_{CB}']),
            (0, H1, L, H1, L, self.w1, mv['M_{BE}'], mv['M_{EB}']),
            (0, Htot, L, Htot, L, self.w2, mv['M_{CD}'], mv['M_{DC}']),
            (L, H1, L, Htot, H2, 0.0, mv['M_{ED}'], mv['M_{DE}']),
            (L, 0, L, H1, H1, 0.0, mv['M_{FE}'], mv['M_{EF}']),
        ]
        all_x, all_y = [0, L], [0, Htot]
        for x0, y0, x1, y1, length, w_load, m_near, m_far in members:
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

        scale = 100
        s_AB = np.linspace(0, H1, 60)
        u_AB = transverse_u(s_AB, -mv['M_{AB}'], mv['M_{BA}'], H1, 0.0, u0=0, up0=0)
        s_FE = np.linspace(0, H1, 60)
        u_FE = transverse_u(s_FE, -mv['M_{FE}'], mv['M_{EF}'], H1, 0.0, u0=0, up0=0)

        x_AB, y_AB = member_offset_curve(0, 0, 0, H1, s_AB, u_AB, scale)
        x_FE, y_FE = member_offset_curve(L, 0, L, H1, s_FE, u_FE, scale)

        # 二樓柱: 近端B(遠端已知u=柱頂實際偏移量, 用一樓柱算出來的頂端座標接上去)
        x_B_actual, y_B_actual = x_AB[-1], y_AB[-1]
        x_E_actual, y_E_actual = x_FE[-1], y_FE[-1]

        s_BC = np.linspace(0, H2, 60)
        u_BC = transverse_u(s_BC, -mv['M_{BC}'], mv['M_{CB}'], H2, 0.0, u0=0, up0=0)
        s_ED = np.linspace(0, H2, 60)
        u_ED = transverse_u(s_ED, -mv['M_{ED}'], mv['M_{DE}'], H2, 0.0, u0=0, up0=0)
        x_BC, y_BC = member_offset_curve(x_B_actual, y_B_actual, x_B_actual, y_B_actual + H2,
                                          s_BC, u_BC, scale)
        x_ED, y_ED = member_offset_curve(x_E_actual, y_E_actual, x_E_actual, y_E_actual + H2,
                                          s_ED, u_ED, scale)
        x_C_actual, y_C_actual = x_BC[-1], y_BC[-1]
        x_D_actual, y_D_actual = x_ED[-1], y_ED[-1]

        s_BE = np.linspace(0, L, 100)
        u_BE = transverse_u(s_BE, -mv['M_{BE}'], mv['M_{EB}'], L, self.w1, u0=0, up0=-thB)
        x_BE, y_BE = member_offset_curve(x_B_actual, y_B_actual, x_E_actual, y_E_actual,
                                          s_BE, u_BE, scale)

        s_CD = np.linspace(0, L, 100)
        u_CD = transverse_u(s_CD, -mv['M_{CD}'], mv['M_{DC}'], L, self.w2, u0=0, up0=-thC)
        x_CD, y_CD = member_offset_curve(x_C_actual, y_C_actual, x_D_actual, y_D_actual,
                                          s_CD, u_CD, scale)

        ax.plot([0, 0], [0, Htot], '--', color='gray', lw=1.5, label='Original Structure')
        ax.plot([L, L], [0, Htot], '--', color='gray', lw=1.5)
        ax.plot([0, L], [H1, H1], '--', color='gray', lw=1.5)
        ax.plot([0, L], [Htot, Htot], '--', color='gray', lw=1.5)
        for xs, ys in [(x_AB, y_AB), (x_FE, y_FE), (x_BC, y_BC), (x_ED, y_ED),
                       (x_BE, y_BE), (x_CD, y_CD)]:
            ax.plot(xs, ys, 'b-', lw=2)

        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)

        ax.set_xlim(-2, L + 3)
        ax.set_ylim(-1, Htot + 1.5)
        ax.set_aspect('equal')
        ax.set_title(f'Two-Story Sway Frame: Original vs Deformed Shape (x{scale} scale)')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=1)
        ax.grid(True, linestyle='--', alpha=0.4)
        return True
