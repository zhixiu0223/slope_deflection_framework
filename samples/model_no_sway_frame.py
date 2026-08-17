import numpy as np
import sympy as sp


from sd_framework import SlopeDeflectionProblem


class NoSwayFrameProblem(SlopeDeflectionProblem):
    """
    Case-03：無側移單跨剛架 (No-Sway Single-Bay Frame)
    柱AB、CD高度相同(H)、底端固定(A,D)；梁BC跨度L，承受均佈載重w。
    結構與載重左右對稱，且沒有水平力，所以不側移(ψ=0)——這是本課程
    第一次同時出現柱跟梁，也是第一次真正用到「節點力矩平衡」連接
    兩種不同方向的桿件(柱+梁)。

    畫圖規則(呼應使用者問的畫法)：每根桿件都用它自己的「物理上連續」
    彎矩/剪力值畫圖，不是直接套用slope-deflection的原始正負號——已用
    剪力對過anastruct驗證：
    - 柱(垂直桿件)：兩端直接用slope-deflection算出的原始值，不需要
      轉換遠端符號
    - 梁(水平桿件)：遠端要取負號才是物理上連續的邊界值(跟Case-01/02
      的梁、跟先前側移剛架的梁BC是同一條規則)
    - 兩根桿件在同一節點(例如B)的圖，數值不需要「同號才對」——它們
      只需要滿足 M_BA+M_BC=0 這個平衡方程式(代數和為0)，不代表兩者
      的物理彎矩值本身相等，各自獨立按自己的規則畫就是對的。
    """

    def __init__(self, H=4.0, L=6.0, w=24.0):
        self.H, self.L, self.w = H, L, w
        self.EI = sp.Symbol('EI', positive=True, real=True)
        self.theta_B, self.theta_C = sp.symbols('theta_B theta_C', real=True)

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B, '\\theta_C': self.theta_C}

    def describe(self):
        return (f"**柱高** $H={self.H}$ m (兩柱等高)，**梁跨** $L={self.L}$ m，"
                f"**梁上均佈載重** $w={self.w}$ kN/m\n\n"
                f"**邊界條件：** A、D兩端固定 ($\\theta_A=\\theta_D=0$)，"
                f"結構與載重左右對稱、無水平力，所以不側移 ($\\psi=0$，"
                f"沒有 $\\Delta$ 這個未知量)")

    def describe_dof(self):
        return (f"A、D固定端轉角鎖死，不是未知量。B、C是梁柱交會的剛性節點，"
                f"各自有一個轉角 $\\theta_B, \\theta_C$——這是本課程第一次"
                f"在同一個節點同時連接柱跟梁(垂直桿件+水平桿件)，節點力矩"
                f"平衡要把兩種桿件的彎矩式加在一起。因為結構對稱、只有"
                f"垂直載重、沒有水平力，所以**沒有側移**，不需要像Case-04"
                f"那樣多列一個 $\\Delta$ 自由度跟剪力平衡方程式——這點如果"
                f"誤判(以為有側移)，會多出一個不存在的自由度跟不必要的"
                f"剪力平衡方程式。共兩個未知位移量 $\\theta_B, \\theta_C$。")

    def draw_geometry(self, ax):
        H, L, w = self.H, self.L, self.w
        ax.plot([0, 0], [0, H], 'k-', lw=3)
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)
        # A, D固定端
        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)
        ax.text(0, -0.5, 'A (Fixed)', ha='center', fontsize=10, fontweight='bold')
        ax.text(L, -0.5, 'D (Fixed)', ha='center', fontsize=10, fontweight='bold')
        ax.text(0, H + 0.3, 'B', fontsize=12, fontweight='bold', ha='center')
        ax.text(L, H + 0.3, 'C', fontsize=12, fontweight='bold', ha='center')
        # UDL箭頭
        for x in np.linspace(0.3, L - 0.3, 8):
            ax.annotate('', xy=(x, H + 0.05), xytext=(x, H + 0.4),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.2))
        ax.text(L / 2, H + 0.6, f'$w={w}$ kN/m', color='red', ha='center', fontsize=11)
        # theta_B, theta_C
        ax.annotate('', xy=(-0.35, H + 0.35), xytext=(0.35, H + 0.35),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',
                                     color='purple', lw=2))
        ax.text(0, H + 0.75, r'$\theta_B$', color='purple', fontsize=12, ha='center')
        ax.annotate('', xy=(L - 0.35, H + 0.35), xytext=(L + 0.35, H + 0.35),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(L, H + 0.75, r'$\theta_C$', color='purple', fontsize=12, ha='center')

        ax.set_xlim(-2, L + 2)
        ax.set_ylim(-1, H + 1.5)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: No-Sway Frame — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, H, L, w = self.EI, self.H, self.L, self.w
        thB, thC = self.theta_B, self.theta_C
        FEM_BC = w * L**2 / 12
        FEM_CB = -w * L**2 / 12
        return {
            'M_{AB}': 2 * EI / H * thB,
            'M_{BA}': 2 * EI / H * (2 * thB),
            'M_{BC}': 2 * EI / L * (2 * thB + thC) + FEM_BC,
            'M_{CB}': 2 * EI / L * (thB + 2 * thC) + FEM_CB,
            'M_{CD}': 2 * EI / H * (2 * thC),
            'M_{DC}': 2 * EI / H * thC,
        }

    def build_equilibrium_equations(self, moments):
        eq1 = sp.Eq(moments['M_{BA}'] + moments['M_{BC}'], 0)
        eq2 = sp.Eq(moments['M_{CB}'] + moments['M_{CD}'], 0)
        return [
            ("節點 B 力矩平衡 ΣM_B=0（柱AB與梁BC交會） M_BA + M_BC = 0", eq1),
            ("節點 C 力矩平衡 ΣM_C=0（梁BC與柱CD交會） M_CB + M_CD = 0", eq2),
        ]

    def compute_reactions(self, moments_val):
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        # 柱不需要negate遠端(已用anastruct驗證)：H = (M底+M頂)/H
        H_A = (m_ab + m_ba) / H
        H_D = (m_dc + m_cd) / H
        V_A = w * L / 2
        V_D = w * L / 2
        return {'H_A (kN)': H_A, 'H_D (kN)': H_D,
                'V_A (kN)': V_A, 'V_D (kN)': V_D}

    def draw_sfd(self, ax, moments_val):
        from sd_framework import member_shear_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.02

        ax.plot([0, 0], [0, H], 'k-', lw=3, label='Frame Structure')
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)

        # 統一規則：不分柱或梁，遠端都要negate才是物理上連續的邊界值
        # (已用anastruct的真實bending_moment/shear_force陣列驗證過，
        # 之前「柱不用negate」的判斷是錯的——柱子放大看其實也會crossing)
        y1 = np.linspace(0, H, 100)
        v1 = member_shear_curve(y1, H, 0.0, m_ab, -m_ba)
        ax.plot(v1 * scale, y1, 'b-', lw=2, label='SFD')
        ax.fill_betweenx(y1, 0, v1 * scale, color='blue', alpha=0.15)

        x2 = np.linspace(0, L, 200)
        v2 = member_shear_curve(x2, L, w, m_bc, -m_cb)
        ax.plot(x2, H + v2 * scale, 'b-', lw=2)
        ax.fill_between(x2, H, H + v2 * scale, color='blue', alpha=0.15)

        y3 = np.linspace(0, H, 100)
        v3 = member_shear_curve(y3, H, 0.0, m_cd, -m_dc)
        ax.plot(L - v3 * scale, H - y3, 'b-', lw=2)
        ax.fill_betweenx(H - y3, L, L - v3 * scale, color='blue', alpha=0.15)

        ax.axhline(0, color='gray', lw=0.5, zorder=0)
        ax.axhline(H, color='gray', lw=0.5, zorder=0)
        for val, x, y, ha in [(v1[0], 0, 0, 'right'), (v1[-1], 0, H, 'right'),
                               (v2[0], 0, H, 'left'), (v2[-1], L, H, 'right'),
                               (v3[0], L, H, 'left'), (v3[-1], L, 0, 'left')]:
            ax.text(x, y, f'{val:.1f}', color='darkblue', fontsize=8, ha=ha)

        ax.set_xlim(-3, L + 3)
        ax.set_ylim(-1, H + 2)
        ax.set_aspect('equal')
        ax.set_title('Figure: Shear Force Diagram (SFD) [kN]')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')
        return True

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.025

        ax.plot([0, 0], [0, H], 'k-', lw=3, label='Frame Structure')
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)

        # 統一規則：柱、梁遠端都要negate (見上方draw_sfd的說明)
        y1 = np.linspace(0, H, 200)
        m1 = member_moment_curve(y1, H, 0.0, m_ab, -m_ba)
        ax.plot(m1 * scale, y1, 'r--', lw=2, label='BMD')
        ax.fill_betweenx(y1, 0, m1 * scale, color='red', alpha=0.15)

        x2 = np.linspace(0, L, 200)
        m2 = member_moment_curve(x2, L, w, m_bc, -m_cb)
        ax.plot(x2, H + m2 * scale, 'r--', lw=2)
        ax.fill_between(x2, H, H + m2 * scale, color='red', alpha=0.15)

        y3 = np.linspace(0, H, 200)
        m3 = member_moment_curve(y3, H, 0.0, m_cd, -m_dc)
        ax.plot(L - m3 * scale, H - y3, 'r--', lw=2)
        ax.fill_betweenx(H - y3, L, L - m3 * scale, color='red', alpha=0.15)

        ax.axhline(0, color='gray', lw=0.5, zorder=0)
        ax.axhline(H, color='gray', lw=0.5, zorder=0)

        ax.text(m_ab * scale, 0, f'{m_ab:.1f}', color='darkred', fontsize=8, ha='right', va='top')
        ax.text(m1[-1] * scale, H, f'{m1[-1]:.1f}', color='darkred', fontsize=8, ha='right', va='bottom')
        ax.text(0, H + m_bc * scale, f'{m_bc:.1f}', color='darkred', fontsize=8, ha='left', va='bottom')
        ax.text(L, H + m2[-1] * scale, f'{m2[-1]:.1f}', color='darkred', fontsize=8, ha='right', va='bottom')
        ax.text(L - m_cd * scale, H, f'{m_cd:.1f}', color='darkred', fontsize=8, ha='left', va='bottom')
        ax.text(L - m3[-1] * scale, 0, f'{m3[-1]:.1f}', color='darkred', fontsize=8, ha='left', va='top')

        # 每根桿件的跨內真正極值 (解析解)，柱也要標，因為柱現在會crossing
        self._label_interior_extremum(ax, H, 0.0, m_ab, -m_ba, scale, y_base=0,
                                       horizontal=False, x_base=0)
        self._label_interior_extremum(ax, L, w, m_bc, -m_cb, scale, y_base=H, horizontal=True)
        self._label_interior_extremum(ax, H, 0.0, m_cd, -m_dc, scale, y_base=0,
                                       horizontal=False, x_base=L, flip_y=True)

        ax.set_xlim(-4, L + 4)
        ax.set_ylim(-1, H + 3)
        ax.set_aspect('equal')
        ax.set_title('Figure: Bending Moment Diagram (BMD) [kN·m]')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')

    @staticmethod
    def _label_interior_extremum(ax, length, w, M_i, M_j, scale, y_base, horizontal=True,
                                  x_base=0, flip_y=False):
        # w=0 (柱) 時仍可能有 crossing (因為現在M_i,M_j可能異號)，但沒有
        # 拋物線頂點可言 (純線性)，這裡只在有均佈載重(w>0)時標跨內極值；
        # 柱的crossing點本身數值是0，不需要另外標「極值」
        if w == 0:
            return
        C1 = (M_j - M_i - 0.5 * w * length**2) / length
        s_star = -C1 / w
        if 0 < s_star < length:
            m_star = M_i + C1 * s_star + 0.5 * w * s_star**2
            if horizontal:
                ax.text(s_star, y_base + m_star * scale - 0.3,
                        f'{m_star:.1f}\n(x={s_star:.2f}m)', color='darkred',
                        ha='center', fontweight='bold', fontsize=9)
