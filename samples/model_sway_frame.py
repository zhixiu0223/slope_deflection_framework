import numpy as np
import sympy as sp

from sd_framework import SlopeDeflectionProblem


class SwayFrameProblem(SlopeDeflectionProblem):
    """
    Case-04：側移單跨剛架 (Sway Single-Bay Frame)
    柱AB、CD高度相同(H)、底端固定(A,D)；梁BC跨度L；B點承受水平集中
    載重P，梁上可選擇加均佈載重w(預設0，即Case-04原本的題目；w>0時
    變成Case-04.5：梁均佈載重+側向力的組合載重題，實務上很常見的
    組合，柱身仍無側向載重)。跟Case-03(無側移)的差別：多了側移角Δ
    這個自由度、多了一條剪力平衡方程式(ΣFx=0)。

    FEM慣例：近端負、遠端正(傳統教科書慣例，順時針為正)，跟Case-01/02/03統一。
    w=0時FEM全部=0，這條慣例在數值上不受影響；w>0時梁的FEM才會真的用上。
    """

    def __init__(self, H=4.0, L=6.0, P=12.0, w=0.0, EI_numeric=15000.0):
        self.H, self.L, self.P, self.w = H, L, P, w
        self.EI = sp.Symbol('EI', positive=True, real=True)
        self.theta_B, self.theta_C, self.psi = sp.symbols('theta_B theta_C psi', real=True)
        self.EI_numeric = EI_numeric

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B, '\\theta_C': self.theta_C, '\\psi': self.psi}

    def describe(self):
        w_desc = (f"，**梁上均佈載重** $w={self.w}$ kN/m" if self.w else "，梁上無跨間載重(FEM=0)")
        return (f"**柱高** $H={self.H}$ m (兩柱等高)，**梁跨** $L={self.L}$ m，"
                f"**B點水平集中載重** $P={self.P}$ kN{w_desc}\n\n"
                f"**邊界條件：** A、D兩端固定 ($\\theta_A=\\theta_D=0$)，柱身無側向載重")

    def describe_dof(self):
        return (f"A、D固定端轉角鎖死，不是未知量。B、C是梁柱交會的剛性節點，"
                f"各自有一個轉角 $\\theta_B, \\theta_C$。因為有水平力P作用，"
                f"這次**不能假設無側移**——柱頂B、C會一起產生水平位移Δ，"
                f"多出第三個未知量：側移角 $\\psi=\\Delta/H$(兩柱等高，側移量"
                f"相同，共用同一個ψ)。共三個未知位移量 $\\theta_B, \\theta_C, \\psi$。"
                f"對應多一條**剪力平衡方程式**(整體水平方向 ΣFx=0)，這是跟"
                f"Case-03唯一的差別——如果誤判成無側移(漏掉ψ跟剪力平衡)，"
                f"方程式數量會跟未知數對不上。")

    def draw_geometry(self, ax):
        H, L, P = self.H, self.L, self.P
        ax.plot([0, 0], [0, H], 'k-', lw=3)
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)
        for x0 in (0, L):
            ax.plot([x0 - 0.15, x0 + 0.15], [-0.02, -0.02], 'k-', lw=3)
            for dx in np.linspace(-0.12, 0.12, 5):
                ax.plot([x0 + dx, x0 + dx - 0.1], [0, -0.2], 'k-', lw=1)
        ax.text(0, -0.5, 'A (Fixed)', ha='center', fontsize=10, fontweight='bold')
        ax.text(L, -0.5, 'D (Fixed)', ha='center', fontsize=10, fontweight='bold')
        ax.text(0, H + 0.3, 'B', fontsize=12, fontweight='bold', ha='center')
        ax.text(L, H + 0.3, 'C', fontsize=12, fontweight='bold', ha='center')

        w = self.w
        if w:
            for xx in np.linspace(0.3, L - 0.3, 7):
                ax.annotate('', xy=(xx, H + 0.05), xytext=(xx, H + 0.5),
                            arrowprops=dict(arrowstyle='->', color='crimson', lw=1.2))
            ax.text(L / 2, H + 0.75, f'$w={w}$ kN/m', color='crimson', ha='center', fontsize=10)

        # 水平力P (畫在B點, 指向+x)——往下移一點，避免跟梁線、UDL箭頭重疊
        ax.annotate('', xy=(1.0, H - 0.4), xytext=(0.0, H - 0.4),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
        ax.text(1.15, H - 0.4, f'$P={P}$ kN', color='red', ha='left', va='center', fontsize=11)

        # theta_B, theta_C: 統一順時針假設方向(跟Case-03同一原則)
        ax.annotate('', xy=(0.35, H + 0.9), xytext=(-0.35, H + 0.9),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(0, H + 1.3, r'$\theta_B$', color='purple', fontsize=12, ha='center')
        ax.annotate('', xy=(L + 0.35, H + 0.9), xytext=(L - 0.35, H + 0.9),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(L, H + 1.3, r'$\theta_C$', color='purple', fontsize=12, ha='center')

        # psi (側移角) 標示: 代表水平側移方向, 畫在梁跨中間下方(遠離其他標籤)，
        # 箭頭指向水平(+x), 跟P同方向
        mid_x = L / 2
        ax.annotate('', xy=(mid_x + 0.6, H / 2), xytext=(mid_x - 0.6, H / 2),
                    arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.8))
        ax.text(mid_x, H / 2 + 0.3, r'$\psi=\Delta/H$', color='darkorange', fontsize=10,
                ha='center')

        ax.set_xlim(-2.2, L + 2)
        ax.set_ylim(-1, H + 2)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: Sway Frame — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, H, L, w = self.EI, self.H, self.L, self.w
        thB, thC, psi = self.theta_B, self.theta_C, self.psi
        FEM_BC = -w * L**2 / 12
        FEM_CB = w * L**2 / 12
        return {
            'M_{AB}': 2 * EI / H * (thB - 3 * psi),
            'M_{BA}': 2 * EI / H * (2 * thB - 3 * psi),
            'M_{BC}': 2 * EI / L * (2 * thB + thC) + FEM_BC,
            'M_{CB}': 2 * EI / L * (thB + 2 * thC) + FEM_CB,
            'M_{CD}': 2 * EI / H * (2 * thC - 3 * psi),
            'M_{DC}': 2 * EI / H * (thC - 3 * psi),
        }

    def build_equilibrium_equations(self, moments):
        H, P = self.H, self.P
        eq1 = sp.Eq(moments['M_{BA}'] + moments['M_{BC}'], 0)
        eq2 = sp.Eq(moments['M_{CB}'] + moments['M_{CD}'], 0)
        eq3 = sp.Eq((moments['M_{AB}'] + moments['M_{BA}']) / H +
                     (moments['M_{DC}'] + moments['M_{CD}']) / H + P, 0)
        return [
            ("節點 B 力矩平衡 ΣM_B=0（柱AB與梁BC交會） M_BA + M_BC = 0", eq1),
            ("節點 C 力矩平衡 ΣM_C=0（梁BC與柱CD交會） M_CB + M_CD = 0", eq2),
            ("整體剪力平衡 ΣFx=0（水平力P跟兩柱剪力平衡，這是本Case比Case-03多出來的方程式）"
             " (M_AB+M_BA)/H + (M_DC+M_CD)/H + P = 0", eq3),
        ]

    def compute_reactions(self, moments_val):
        H = self.H
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        H_A = (m_ab + m_ba) / H
        H_D = (m_dc + m_cd) / H
        return {'H_A (kN)': H_A, 'H_D (kN)': H_D}

    def draw_sfd(self, ax, moments_val):
        from sd_framework import member_shear_curve, member_offset_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.05

        ax.plot([0, 0], [0, H], 'k-', lw=3, label='Frame Structure')
        ax.plot([0, L], [H, H], 'k-', lw=3)
        ax.plot([L, L], [H, 0], 'k-', lw=3)

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

        labels = [
            (0, 0, 0, 1, -m_ab),
            (0, H, 0, 1, m_ba),
            (0, H, 1, 0, -m_bc),
            (L, H, 1, 0, m_cb),
            (L, H, 0, 1, m_cd),
            (L, 0, 0, 1, -m_dc),
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
            ax.text(x, y - 0.35 if y == 0 else y + 0.35, f'M={val:.1f}',
                    fontsize=8, ha='center', color='black')

        ax.set_xlim(-2.5, L + 2.5)
        ax.set_ylim(-1.5, H + 2)
        ax.set_aspect('equal')
        ax.set_title('Figure: Tension/Compression Side by Member')
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_deformed_shape(self, ax, moments_val, solution):
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        EI_val = self.EI_numeric
        theta_B = float(solution[self.theta_B].subs(self.EI, EI_val))

        from sd_framework import member_offset_curve

        def transverse_u(s_arr, M_i, M_j, length, w_load, u0, up0):
            C1 = (M_j - M_i - 0.5 * w_load * length**2) / length
            return (u0 + up0 * s_arr + (1.0 / EI_val) *
                    (-M_i * s_arr**2 / 2 - C1 * s_arr**3 / 6 - w_load * s_arr**4 / 24))

        scale = 80
        s_col = np.linspace(0, H, 100)
        s_beam = np.linspace(0, L, 100)

        # 柱AB: 近端A(固定,u=0,u'=0) -> 遠端B。這次(有側移)不強制u(H)=0，
        # 讓它自然積分出來的值就是側移量Δ，跟Case-03(無側移)不一樣
        u_AB = transverse_u(s_col, -m_ab, m_ba, H, 0.0, u0=0, up0=0)
        # 梁BC: 近端B(u=0,u'=-theta_B已知,連續節點) -> 遠端C
        u_BC = transverse_u(s_beam, -m_bc, m_cb, L, w, u0=0, up0=-theta_B)
        # 柱CD: 近端D(固定,u=0,u'=0) -> 遠端C
        u_CD = transverse_u(s_col, -m_dc, m_cd, H, 0.0, u0=0, up0=0)

        x_AB, y_AB = member_offset_curve(0, 0, 0, H, s_col, u_AB, scale)

        # 梁BC的起點、終點要用柱頂「實際偏移後」的座標，不能假設柱頂還在
        # x=0/x=L——柱子有側移，頂端已經橫向偏移過去了(這是這次抓到的bug：
        # 梁原本固定用(0,H)->(L,H)當基準，沒有跟著柱頂的真實偏移量走，
        # 造成梁跟柱在B、C兩個節點對不起來、畫出來斷開)
        x_B_actual, y_B_actual = x_AB[-1], y_AB[-1]

        x_CD, y_CD = member_offset_curve(L, 0, L, H, s_col, u_CD, scale)
        x_C_actual, y_C_actual = x_CD[-1], y_CD[-1]

        x_BC, y_BC = member_offset_curve(x_B_actual, y_B_actual,
                                          x_C_actual, y_C_actual, s_beam, u_BC, scale)

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

        ax.set_xlim(-2, L + 3)
        ax.set_ylim(-1, H + 1.5)
        ax.set_aspect('equal')
        ax.set_title('Sway Frame: Original vs Deformed Shape')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        ax.grid(True, linestyle='--', alpha=0.4)
        return True

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve, member_offset_curve
        H, L, w = self.H, self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        m_bc, m_cb = moments_val['M_{BC}'], moments_val['M_{CB}']
        m_cd, m_dc = moments_val['M_{CD}'], moments_val['M_{DC}']
        scale = 0.06

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

        ax.set_xlim(-4, L + 4)
        ax.set_ylim(-1, H + 3)
        ax.set_aspect('equal')
        ax.set_title('Figure: Bending Moment Diagram (BMD) [kN·m]')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')
