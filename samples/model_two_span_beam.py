import numpy as np
import sympy as sp


from sd_framework import SlopeDeflectionProblem


class TwoSpanBeamProblem(SlopeDeflectionProblem):
    """
    Case-02：二次靜不定連續梁 (Two-Span Continuous Beam)
    A端固定 (theta_A=0)，B為中間滾支承 (連續、不釋放彎矩，theta_B 兩跨共用)，
    C為遠端滾支承 (M_CB=0)。AB跨、BC跨上各自承受均佈載重 w1、w2。

    本 Case 相對 Case-01 新增的概念：**中間節點的平衡方程式**
    (M_BA+M_BC=0，跟前面側移剛架、二層剛架的節點平衡是同一件事)，
    C端沿用 Case-01 學過的「邊界條件 M=0」。
    """

    def __init__(self, L1=5.0, L2=6.0, w1=15.0, w2=20.0):
        self.L1, self.L2, self.w1, self.w2 = L1, L2, w1, w2
        self.EI = sp.Symbol('EI', positive=True, real=True)
        self.theta_B, self.theta_C = sp.symbols('theta_B theta_C', real=True)

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B, '\\theta_C': self.theta_C}

    def describe(self):
        return (f"**AB跨** $L_1={self.L1}$ m ($w_1={self.w1}$ kN/m), "
                f"**BC跨** $L_2={self.L2}$ m ($w_2={self.w2}$ kN/m)\n\n"
                f"**邊界條件：** A端固定 ($\\theta_A=0$)，B為中間滾支承 "
                f"(連續，$\\theta_B$ 兩跨共用)，C為遠端滾支承 ($M_{{CB}}=0$)")

    def describe_dof(self):
        return (f"A端固定，$\\theta_A=0$，不是未知量；B是**連續**的中間支承"
                f"(不是鉸接釋放)，AB跨跟BC跨在B點共用**同一個**轉角 "
                f"$\\theta_B$——這裡如果誤把AB跨、BC跨各自設一個獨立轉角"
                f"(當成B是鉸接)，會多出一個不存在的自由度，方程式數量對不上；"
                f"C端是滾支承可自由轉動，$\\theta_C$ 是第二個未知量。"
                f"共兩個未知位移量 $\\theta_B, \\theta_C$——比 Case-01 多了一個"
                f"節點(B)，新增的是**中間節點力矩平衡** $M_{{BA}}+M_{{BC}}=0$。")

    def draw_geometry(self, ax):
        L1, L2, w1, w2 = self.L1, self.L2, self.w1, self.w2
        Ltot = L1 + L2
        ax.plot([0, Ltot], [0, 0], 'k-', lw=4)
        # A端固定
        ax.plot([0, 0], [-0.3, 0.3], 'k-', lw=3)
        for dy in np.linspace(-0.25, 0.25, 6):
            ax.plot([-0.15, 0], [dy - 0.15, dy], 'k-', lw=1)
        ax.text(0, -0.55, 'A (Fixed)', ha='center', fontsize=11, fontweight='bold')
        # B中間滾支承
        ax.plot(L1, -0.12, 'o', color='white', mec='k', ms=14, mew=2)
        ax.plot([L1 - 0.25, L1 + 0.25], [-0.28, -0.28], 'k-', lw=2)
        ax.text(L1, -0.55, 'B (Roller)', ha='center', fontsize=11, fontweight='bold')
        # C遠端滾支承
        ax.plot(Ltot, -0.12, 'o', color='white', mec='k', ms=14, mew=2)
        ax.plot([Ltot - 0.25, Ltot + 0.25], [-0.28, -0.28], 'k-', lw=2)
        ax.text(Ltot, -0.55, 'C (Roller)', ha='center', fontsize=11, fontweight='bold')
        # 均佈載重箭頭 (兩跨分開畫,數值不同)
        for x in np.linspace(0.3, L1 - 0.3, 6):
            ax.annotate('', xy=(x, 0.05), xytext=(x, 0.4),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.2))
        ax.text(L1 / 2, 0.55, f'$w_1={w1}$ kN/m', color='red', ha='center', fontsize=10)
        for x in np.linspace(L1 + 0.3, Ltot - 0.3, 7):
            ax.annotate('', xy=(x, 0.05), xytext=(x, 0.4),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.2))
        ax.text(L1 + L2 / 2, 0.55, f'$w_2={w2}$ kN/m', color='red', ha='center', fontsize=10)
        # theta_B, theta_C 標示 (箭頭跟文字對齊在同一位置)
        ax.annotate('', xy=(L1 - 0.3, -0.75), xytext=(L1 + 0.3, -0.75),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(L1, -1.05, r'$\theta_B$', color='purple', fontsize=13, ha='center')
        ax.annotate('', xy=(Ltot - 0.3, -0.75), xytext=(Ltot + 0.3, -0.75),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(Ltot, -1.05, r'$\theta_C$', color='purple', fontsize=13, ha='center')

        ax.set_xlim(-1.5, Ltot + 1.5)
        ax.set_ylim(-1.3, 1.0)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: Two-Span Continuous Beam — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, L1, L2, w1, w2 = self.EI, self.L1, self.L2, self.w1, self.w2
        thB, thC = self.theta_B, self.theta_C
        FEM_AB = w1 * L1**2 / 12
        FEM_BA = -w1 * L1**2 / 12
        FEM_BC = w2 * L2**2 / 12
        FEM_CB = -w2 * L2**2 / 12
        return {
            'M_{AB}': 2 * EI / L1 * thB + FEM_AB,
            'M_{BA}': 2 * EI / L1 * (2 * thB) + FEM_BA,
            'M_{BC}': 2 * EI / L2 * (2 * thB + thC) + FEM_BC,
            'M_{CB}': 2 * EI / L2 * (thB + 2 * thC) + FEM_CB,
        }

    def build_equilibrium_equations(self, moments):
        eq1 = sp.Eq(moments['M_{BA}'] + moments['M_{BC}'], 0)
        eq2 = sp.Eq(moments['M_{CB}'], 0)
        return [
            ("節點 B 力矩平衡 ΣM_B=0（AB跨與BC跨在B點交會，連續支承、無外加彎矩） "
             "M_BA + M_BC = 0", eq1),
            ("C端邊界條件（滾支承不傳彎矩） M_CB = 0", eq2),
        ]

    def compute_reactions(self, moments_val):
        from sd_framework import member_shear_curve
        L1, L2, w1, w2 = self.L1, self.L2, self.w1, self.w2
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        # 遠端要negate才是物理上連續的邊界值(已用剪力對過anastruct)
        V_ab_0 = member_shear_curve(0.0, L1, w1, m_ab, -m_ba)
        V_ab_L = member_shear_curve(L1, L1, w1, m_ab, -m_ba)
        V_bc_0 = member_shear_curve(0.0, L2, w2, m_bc, -m_cb)
        V_bc_L = member_shear_curve(L2, L2, w2, m_bc, -m_cb)
        R_A = -V_ab_0
        R_B = V_ab_L - V_bc_0
        R_C = V_bc_L
        return {'R_A (kN)': R_A, 'R_B (kN)': R_B, 'R_C (kN)': R_C}

    def draw_tension_side(self, ax, moments_val):
        L1, L2 = self.L1, self.L2
        Ltot = L1 + L2
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        ax.plot([0, Ltot], [0, 0], 'k-', lw=4)

        labels = [
            (0, m_ab),
            (L1, -m_ba),
            (L1, m_bc),
            (Ltot, -m_cb),
        ]
        for x, val in labels:
            sign = 1 if val > 0 else -1
            ax.annotate('TENSION', xy=(x, 0), xytext=(x, 0.7 * sign), color='red',
                        fontsize=9, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color='red'))
            ax.annotate('compression', xy=(x, 0), xytext=(x, -0.7 * sign), color='blue',
                        fontsize=8, ha='center',
                        arrowprops=dict(arrowstyle='->', color='blue', alpha=0.6))
            ax.text(x, 0.05 * (-sign) - (0.15 if sign > 0 else -0.15), f'M={val:.1f}',
                    fontsize=8, ha='center', color='black')

        ax.set_xlim(-1.5, Ltot + 1.5)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.set_title('Figure: Tension/Compression Side')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_deformed_shape(self, ax, moments_val, solution):
        import sympy as sp
        L1, L2, w1, w2 = self.L1, self.L2, self.w1, self.w2
        Ltot = L1 + L2
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        EI_val = 15000.0
        theta_B = float(solution[self.theta_B].subs(self.EI, EI_val))
        s = sp.Symbol('s')

        def transverse_u(M_i, M_j, length, w_load, u0, up0):
            C1 = (M_j - M_i - 0.5 * w_load * length**2) / length
            M_hog = M_i + C1 * s + 0.5 * w_load * s**2
            M_sag = -M_hog
            up = sp.integrate(M_sag / EI_val, s) + up0
            u_expr = sp.integrate(up, s) + u0
            return sp.lambdify(s, u_expr, 'numpy')

        # AB跨: 近端A(固定,u=0,u'=0) -> 遠端B, AB跨自己有均佈載重w1
        u_AB = transverse_u(m_ab, -m_ba, L1, w1, u0=0, up0=0)
        # BC跨: 近端B(u=0,u'=theta_B已知,連續節點) -> 遠端C, BC跨有均佈載重w2
        u_BC = transverse_u(m_bc, -m_cb, L2, w2, u0=0, up0=theta_B)

        scale = 80
        x1 = np.linspace(0, L1, 150)
        x2 = np.linspace(0, L2, 150)
        y1 = u_AB(x1) * scale
        y2 = u_BC(x2) * scale

        ax.plot([0, Ltot], [0, 0], '--', color='gray', lw=2, label='Original Beam')
        ax.plot(x1, y1, 'b-', lw=2.5, label=f'Deformed Shape (x{scale} scale)')
        ax.plot(L1 + x2, y2, 'b-', lw=2.5)

        # 支承符號 (A固定, B/C滾支承)
        ax.plot([0, 0], [-0.15, 0.15], 'k-', lw=3)
        for dy in np.linspace(-0.12, 0.12, 5):
            ax.plot([-0.08, 0], [dy - 0.08, dy], 'k-', lw=1)
        for x0, y0 in [(L1, y1[-1]), (Ltot, y2[-1])]:
            ax.plot(x0, y0 - 0.08, 'o', color='white', mec='k', ms=10, mew=1.5)
            ax.plot([x0 - 0.18, x0 + 0.18], [y0 - 0.18, y0 - 0.18], 'k-', lw=1.5)

        ax.set_xlim(-1.5, Ltot + 1.5)
        y_min = min(y1.min(), y2.min(), -0.5)
        ax.set_ylim(y_min - 0.4, 0.5)
        ax.set_aspect('equal')
        ax.set_title('Two-Span Beam: Original vs Deformed Shape')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
        ax.grid(True, linestyle='--', alpha=0.5)
        return True

    def draw_sfd(self, ax, moments_val):
        from sd_framework import member_shear_curve
        L1, L2, w1, w2 = self.L1, self.L2, self.w1, self.w2
        Ltot = L1 + L2
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        scale = 0.015

        ax.plot([0, Ltot], [0, 0], 'k-', lw=4, label='Beam')
        x1 = np.linspace(0, L1, 100)
        v1 = member_shear_curve(x1, L1, w1, m_ab, -m_ba)
        ax.plot(x1, v1 * scale, 'b-', lw=2, label='SFD (kN)')
        ax.fill_between(x1, 0, v1 * scale, color='blue', alpha=0.15)

        x2 = np.linspace(0, L2, 100)
        v2 = member_shear_curve(x2, L2, w2, m_bc, -m_cb)
        ax.plot(L1 + x2, v2 * scale, 'b-', lw=2)
        ax.fill_between(L1 + x2, 0, v2 * scale, color='blue', alpha=0.15)

        for x, y, val in [(0, v1[0], v1[0]), (L1, v1[-1], v1[-1]),
                          (L1, v2[0], v2[0]), (Ltot, v2[-1], v2[-1])]:
            ax.text(x, y * scale + (0.3 if val > 0 else -0.3), f'{val:.1f}',
                    color='darkblue', ha='center', fontweight='bold', fontsize=9)

        ax.axvline(L1, color='gray', lw=0.6, zorder=0)
        ax.set_xlim(-1, Ltot + 1)
        ax.set_title('Figure: Shear Force Diagram (SFD) [kN]')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Shear offset (scaled)')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')
        return True

    @staticmethod
    def _label_interior_extremum(ax, x_arr, m_arr, length, w, M_i, M_j, scale, x_offset):
        """
        用解析解找拋物線 M(s)=M_i+C1*s+0.5*w*s^2 的跨內真正極值 (頂點 s*=-C1/w)，
        只有 s* 落在 (0, length) 內才是真正的跨內極值才標註——如果落在跨外
        (或 w=0 沒有均佈載重、根本是直線)，代表這跨的極值就在端點，那裡已經
        各自標過了，不用再多標一個假的"跨內"標籤 (之前用陣列掃描+排除邊界
        margin 的做法，找到的常常只是margin邊緣的點，不是真正的極值，已改掉)。
        """
        if w == 0:
            return
        C1 = (M_j - M_i - 0.5 * w * length**2) / length
        s_star = -C1 / w
        if 0 < s_star < length:
            m_star = M_i + C1 * s_star + 0.5 * w * s_star**2
            ax.text(x_offset + s_star, m_star * scale + (0.3 if m_star > 0 else -0.3),
                    f'{m_star:.2f}\n(x={s_star:.2f}m)', color='darkred',
                    ha='center', fontweight='bold', fontsize=9)

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve
        L1, L2, w1, w2 = self.L1, self.L2, self.w1, self.w2
        Ltot = L1 + L2
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        scale = 0.025

        ax.plot([0, Ltot], [0, 0], 'k-', lw=4, label='Beam')

        x1 = np.linspace(0, L1, 200)
        # 遠端(B)要negate才是物理連續的邊界值 — 已用剪力驗證過 (見上方 compute_reactions)
        m1 = member_moment_curve(x1, L1, w1, m_ab, -m_ba)
        ax.plot(x1, m1 * scale, 'r--', lw=2, label='BMD (kN·m)')
        ax.fill_between(x1, 0, m1 * scale, color='red', alpha=0.15)

        x2 = np.linspace(0, L2, 200)
        m2 = member_moment_curve(x2, L2, w2, m_bc, -m_cb)
        ax.plot(L1 + x2, m2 * scale, 'r--', lw=2)
        ax.fill_between(L1 + x2, 0, m2 * scale, color='red', alpha=0.15)

        ax.text(0, m_ab * scale - 0.3, f'{m_ab:.2f}', color='darkred', ha='center', fontweight='bold')
        self._label_interior_extremum(ax, x1, m1, L1, w1, m_ab, -m_ba, scale, x_offset=0)
        self._label_interior_extremum(ax, x2, m2, L2, w2, m_bc, -m_cb, scale, x_offset=L1)
        ax.text(Ltot, m_cb * scale - 0.3, f'{m_cb:.2f}', color='darkred', ha='center', fontweight='bold')

        ax.axvline(L1, color='gray', lw=0.6, zorder=0)
        ax.set_xlim(-1, Ltot + 1)
        ax.set_title('Figure: Bending Moment Diagram (BMD) [kN·m]')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Moment offset (scaled)')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')
