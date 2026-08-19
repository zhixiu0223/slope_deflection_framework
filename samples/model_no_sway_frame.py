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

    def __init__(self, H=4.0, L=6.0, w=24.0, EI_numeric=15000.0):
        self.H, self.L, self.w = H, L, w
        self.EI = sp.Symbol('EI', positive=True, real=True)
        self.EI_numeric = EI_numeric  # 只用在變形圖的實際撓度計算
        self.theta_B, self.theta_C = sp.symbols('theta_B theta_C', real=True)

    @classmethod
    def from_interactive_input(cls):
        """互動輸入版本：Colab、純Linux終端機、VSCode都能用(只靠input())。"""
        from sd_framework import prompt_for_params
        params = prompt_for_params([
            ('H', '柱高(m)', 4.0, float),
            ('L', '梁跨度(m)', 6.0, float),
            ('w', '梁上均佈載重(kN/m)', 24.0, float),
            ('EI_numeric', 'EI數值(只影響變形圖大小,不影響彎矩/剪力)', 15000.0, float),
        ])
        return cls(**params)

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
        # theta_B, theta_C: 正值=順時針、負值=逆時針，箭頭方向要對應
        # (θ_B算出來是正值=順時針，θ_C是負值=逆時針，已用matplotlib實際
        # 渲染測試確認rad=-0.5畫出來是順時針、rad=+0.5是逆時針——
        # 之前這裡的rad符號搞反了，畫成θ_B逆時針、θ_C順時針，跟實際解出來
        # 的正負號對不上，這次修正)
        # theta_B, theta_C: 兩個都統一假設「順時針為正」畫箭頭方向——這是
        # 傾角變位法設未知數的標準做法，不能因為已經算出θ_C是負值(逆時針)
        # 就反過來畫成逆時針箭頭，那樣等於用答案去畫題目，失去「先假設
        # 正方向、算完看正負號才知道實際方向」這個核心邏輯。複雜結構在
        # 算之前根本不知道誰順誰逆，兩個箭頭都畫順時針才是正確的起始假設；
        # 算出來是正值代表真的是順時針，負值代表實際上是逆時針。
        ax.annotate('', xy=(0.35, H + 0.35), xytext=(-0.35, H + 0.35),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(0, H + 0.75, r'$\theta_B$', color='purple', fontsize=12, ha='center')
        ax.annotate('', xy=(L + 0.35, H + 0.35), xytext=(L - 0.35, H + 0.35),
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
        FEM_BC = -w * L**2 / 12
        FEM_CB = w * L**2 / 12
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
        from sd_framework import member_shear_curve, member_offset_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.02

        ax.plot([0, 0], [0, H], 'k-', lw=3, label='Frame Structure')
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)

        # 統一規則：偏移方向 = 沿「近端->遠端」前進方向逆時針轉90度，
        # 柱、梁都用同一個 member_offset_curve，不再各自手寫x/y公式
        # (已用anastruct實際畫圖座標精確驗證過，見對話記錄)
        s1 = np.linspace(0, H, 100)
        v1 = member_shear_curve(s1, H, 0.0, -m_ab, m_ba)
        x1, y1 = member_offset_curve(0, 0, 0, H, s1, v1, scale)
        ax.plot(x1, y1, 'b-', lw=2, label='SFD')
        ax.fill(np.append(x1, [0, 0]), np.append(y1, [H, 0]), color='blue', alpha=0.15)

        s2 = np.linspace(0, L, 200)
        v2 = member_shear_curve(s2, L, w, -m_bc, m_cb)
        x2, y2 = member_offset_curve(0, H, L, H, s2, v2, scale)
        ax.plot(x2, y2, 'b-', lw=2)
        ax.fill(np.append(x2, [L, 0]), np.append(y2, [H, H]), color='blue', alpha=0.15)

        # 柱CD: 近端D(L,0) -> 遠端C(L,H)，跟AB統一方向(由下往上)
        s3 = np.linspace(0, H, 100)
        v3 = member_shear_curve(s3, H, 0.0, -m_dc, m_cd)
        x3, y3 = member_offset_curve(L, 0, L, H, s3, v3, scale)
        ax.plot(x3, y3, 'b-', lw=2)
        ax.fill(np.append(x3, [L, L]), np.append(y3, [H, 0]), color='blue', alpha=0.15)

        ax.axhline(0, color='gray', lw=0.5, zorder=0)
        ax.axhline(H, color='gray', lw=0.5, zorder=0)
        for xx, yy, val, ha in [(x1[0], y1[0], v1[0], 'right'), (x1[-1], y1[-1], v1[-1], 'right'),
                                 (x2[0], y2[0], v2[0], 'left'), (x2[-1], y2[-1], v2[-1], 'right'),
                                 (x3[0], y3[0], v3[0], 'left'), (x3[-1], y3[-1], v3[-1], 'left')]:
            ax.text(xx, yy, f'{val:.1f}', color='darkblue', fontsize=8, ha=ha)

        ax.set_xlim(-3, L + 3)
        ax.set_ylim(-1, H + 2)
        ax.set_aspect('equal')
        ax.set_title('Figure: Shear Force Diagram (SFD) [kN]')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')
        return True

    def draw_tension_side(self, ax, moments_val):
        H, L = self.H, self.L
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']

        ax.plot([0, 0], [0, H], 'k-', lw=4)
        ax.plot([0, L], [H, H], 'k-', lw=4)
        ax.plot([L, L], [H, 0], 'k-', lw=4)

        # (x, y, 近端->遠端方向dx,dy, 該處physical值) -- physical值的正負
        # 決定偏移方向 = 受拉側，這是跟 member_offset_curve 完全一致的
        # 判斷方式，只是這裡直接標文字不畫曲線
        labels = [
            (0, 0, 0, 1, -m_ab),
            (0, H, 0, 1, m_ba),
            (0, H, 1, 0, -m_bc),
            (L, H, 1, 0, m_cb),
            (L, 0, 0, 1, -m_dc),
            (L, H, 0, 1, m_cd),
        ]
        for x, y, dx, dy, val in labels:
            perp_x, perp_y = -dy, dx
            sign = 1 if val > 0 else -1
            tx, ty = x + perp_x * sign * 0.9, y + perp_y * sign * 0.9
            cx, cy = x - perp_x * sign * 0.9, y - perp_y * sign * 0.9
            ax.annotate('TENSION', xy=(x, y), xytext=(tx, ty), color='red',
                        fontsize=9, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='->', color='red'))
            ax.annotate('compression', xy=(x, y), xytext=(cx, cy), color='blue',
                        fontsize=8, ha='center',
                        arrowprops=dict(arrowstyle='->', color='blue', alpha=0.6))
            ax.text(x, y - 0.35 if y == 0 else y + 0.35, f'M={val:.0f}',
                    fontsize=8, ha='center', color='black')

        m_mid = m_bc - self.w * self.L**2 / 8  # 跨中(均佈載重下，兩端同值的簡化式)
        ax.annotate('TENSION (bottom)', xy=(L / 2, H), xytext=(L / 2, H - 1.0),
                    color='red', fontsize=9, fontweight='bold', ha='center',
                    arrowprops=dict(arrowstyle='->', color='red'))

        ax.set_xlim(-2.5, L + 2.5)
        ax.set_ylim(-1.5, H + 2)
        ax.set_aspect('equal')
        ax.set_title('Figure: Tension/Compression Side by Member')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_deformed_shape(self, ax, moments_val, solution):
        from sd_framework import member_offset_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']

        EI_val = self.EI_numeric

        def transverse_u(s_arr, M_i, M_j, length, w_load, u0, up0):
            """
            解析公式直接算橫向位移(不用sympy符號積分——手機瀏覽器版Colab
            對sympy積分這種比較吃運算量的cell容易出現渲染卡頓、需要多按
            一次才畫得出來的狀況，改成純數值運算後這個問題就消失了)。
            M_sag(s) = -(M_i + C1*s + 0.5*w*s^2)，對s積分兩次的解析解：
              u'(s) = up0 + (1/EI)*[-M_i*s - C1*s^2/2 - w*s^3/6]
              u(s)  = u0 + up0*s + (1/EI)*[-M_i*s^2/2 - C1*s^3/6 - w*s^4/24]
            已跟sympy版本逐點比對過，數值差在浮點誤差範圍內(<1e-16)。
            """
            C1 = (M_j - M_i - 0.5 * w_load * length**2) / length
            return (u0 + up0 * s_arr + (1.0 / EI_val) *
                    (-M_i * s_arr**2 / 2 - C1 * s_arr**3 / 6 - w_load * s_arr**4 / 24))

        theta_B = float(solution[self.theta_B].subs(self.EI, EI_val))
        # 本Case用「近端負、遠端正」的FEM慣例(跟Case-01/02的「近端正、遠端負」
        # 相反)，這是刻意選擇的、傾角變位法仍然順時針為正——但這個選擇連帶
        # 讓「畫變形圖時哪一端要negate」也整套反過來，已用anastruct的
        # show_displacement()實際畫圖座標逐點測試過(先單獨測梁、再單獨測柱、
        # 確認規則一致後才接上來)，用兩種可能各自代入比對才找到正確答案，
        # 不是直接套用原本Case-01/02的規則：
        #   近端要negate、遠端直接用(不negate)——跟原本Case-01/02完全相反
        #   邊界條件用的theta也要negate(-theta_B，不是theta_B本身)
        scale = 80
        s_col = np.linspace(0, H, 100)
        s_beam = np.linspace(0, L, 100)

        # 柱AB: 近端A(固定,u=0,u'=0) -> 遠端B
        u_AB = transverse_u(s_col, -m_ab, m_ba, H, 0.0, u0=0, up0=0)
        # 梁BC: 近端B(u=0,u'=-theta_B已知,連續節點) -> 遠端C
        u_BC = transverse_u(s_beam, -m_bc, m_cb, L, w, u0=0, up0=-theta_B)
        # 柱CD: 近端D(固定,u=0,u'=0) -> 遠端C
        u_CD = transverse_u(s_col, -m_dc, m_cd, H, 0.0, u0=0, up0=0)

        x_AB, y_AB = member_offset_curve(0, 0, 0, H, s_col, u_AB, scale)
        x_BC, y_BC = member_offset_curve(0, H, L, H, s_beam, u_BC, scale)
        x_CD, y_CD = member_offset_curve(L, 0, L, H, s_col, u_CD, scale)

        ax.plot([0, 0], [0, H], '--', color='gray', lw=2, label='Original Structure')
        ax.plot([0, L], [H, H], '--', color='gray', lw=2)
        ax.plot([L, L], [H, 0], '--', color='gray', lw=2)
        ax.plot(x_AB, y_AB, 'b-', lw=2.5, label=f'Deformed Shape (x{scale} scale)')
        ax.plot(x_BC, y_BC, 'b-', lw=2.5)
        ax.plot(x_CD, y_CD, 'b-', lw=2.5)

        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)

        ax.set_xlim(-2, L + 2)
        ax.set_ylim(-1, H + 1.5)
        ax.set_aspect('equal')
        ax.set_title('No-Sway Frame: Original vs Deformed Shape')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve, member_offset_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.025

        ax.plot([0, 0], [0, H], 'k-', lw=3, label='Frame Structure')
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)

        s1 = np.linspace(0, H, 200)
        m1 = member_moment_curve(s1, H, 0.0, -m_ab, m_ba)
        x1, y1 = member_offset_curve(0, 0, 0, H, s1, m1, scale)
        ax.plot(x1, y1, 'r--', lw=2, label='BMD')
        ax.fill(np.append(x1, [0, 0]), np.append(y1, [H, 0]), color='red', alpha=0.15)

        s2 = np.linspace(0, L, 200)
        m2 = member_moment_curve(s2, L, w, -m_bc, m_cb)
        x2, y2 = member_offset_curve(0, H, L, H, s2, m2, scale)
        ax.plot(x2, y2, 'r--', lw=2)
        ax.fill(np.append(x2, [L, 0]), np.append(y2, [H, H]), color='red', alpha=0.15)

        s3 = np.linspace(0, H, 200)
        m3 = member_moment_curve(s3, H, 0.0, -m_dc, m_cd)
        x3, y3 = member_offset_curve(L, 0, L, H, s3, m3, scale)
        ax.plot(x3, y3, 'r--', lw=2)
        ax.fill(np.append(x3, [L, L]), np.append(y3, [H, 0]), color='red', alpha=0.15)

        ax.axhline(0, color='gray', lw=0.5, zorder=0)
        ax.axhline(H, color='gray', lw=0.5, zorder=0)

        ax.text(x1[0], y1[0], f'{m1[0]:.1f}', color='darkred', fontsize=8, ha='right', va='top')
        ax.text(x1[-1], y1[-1], f'{m1[-1]:.1f}', color='darkred', fontsize=8, ha='right', va='bottom')
        ax.text(x2[0], y2[0], f'{m2[0]:.1f}', color='darkred', fontsize=8, ha='left', va='bottom')
        ax.text(x2[-1], y2[-1], f'{m2[-1]:.1f}', color='darkred', fontsize=8, ha='right', va='bottom')
        ax.text(x3[-1], y3[-1], f'{m3[-1]:.1f}', color='darkred', fontsize=8, ha='left', va='bottom')
        ax.text(x3[0], y3[0], f'{m3[0]:.1f}', color='darkred', fontsize=8, ha='left', va='top')

        self._label_interior_extremum_xy(ax, 0, H, L, H, w, -m_bc, m_cb, scale)

        ax.set_xlim(-4, L + 4)
        ax.set_ylim(-1, H + 3)
        ax.set_aspect('equal')
        ax.set_title('Figure: Bending Moment Diagram (BMD) [kN·m]')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')

    @staticmethod
    def _label_interior_extremum_xy(ax, x0, y0, x1, y1, w, M_i, M_j, scale):
        from sd_framework import member_offset_curve
        if w == 0:
            return
        length = np.hypot(x1 - x0, y1 - y0)
        C1 = (M_j - M_i - 0.5 * w * length**2) / length
        s_star = -C1 / w
        if 0 < s_star < length:
            m_star = M_i + C1 * s_star + 0.5 * w * s_star**2
            xs, ys = member_offset_curve(x0, y0, x1, y1, np.array([s_star]),
                                          np.array([m_star]), scale)
            ax.text(xs[0], ys[0] - 0.3, f'{m_star:.1f}\n(x={s_star:.2f}m)',
                    color='darkred', ha='center', fontweight='bold', fontsize=9)
