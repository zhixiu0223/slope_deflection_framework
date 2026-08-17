import numpy as np
import sympy as sp


from sd_framework import SlopeDeflectionProblem


class PropChedCantileverProblem(SlopeDeflectionProblem):
    """
    Case-01：一次靜不定梁 (Propped Cantilever Beam)
    A端固定 (theta_A=0)，B端滾支承 (M_BA=0，可自由轉動)，梁上承受均佈載重 w。

    這是整個課程最基本的起點：只有一個未知數 theta_B，用「M_BA=0」這個
    邊界條件取代之前用慣的「節點力矩平衡」，是後面所有 Case 的基礎。
    """

    def __init__(self, L=6.0, w=20.0):
        self.L, self.w = L, w
        self.EI = sp.Symbol('EI', positive=True, real=True)
        self.theta_B = sp.Symbol('theta_B', real=True)

    def get_unknowns(self):
        return {'\\theta_B': self.theta_B}

    def describe(self):
        return (f"**跨度** $L={self.L}$ m, **均佈載重** $w={self.w}$ kN/m\n\n"
                f"**邊界條件：** A端固定 ($\\theta_A=0$)，"
                f"B端滾支承 ($M_{{BA}}=0$，可自由轉動、垂直方向受限)\n\n"
                f"**自由度分析：** 只有一個未知位移量 $\\theta_B$ —— "
                f"這是最基本的一次靜不定結構，是本課程的第一個 Case")

    def draw_geometry(self, ax):
        L = self.L
        ax.plot([0, L], [0, 0], 'k-', lw=4)
        # A端固定 (畫斜線示意)
        ax.plot([0, 0], [-0.3, 0.3], 'k-', lw=3)
        for dy in np.linspace(-0.25, 0.25, 6):
            ax.plot([-0.15, 0], [dy - 0.15, dy], 'k-', lw=1)
        ax.text(0, -0.55, 'A (Fixed)', ha='center', fontsize=11, fontweight='bold')
        # B端滾支承 (畫圓圈+三角形示意)
        ax.plot(L, -0.12, 'o', color='white', mec='k', ms=14, mew=2)
        ax.plot([L - 0.25, L + 0.25], [-0.28, -0.28], 'k-', lw=2)
        ax.text(L, -0.55, 'B (Roller)', ha='center', fontsize=11, fontweight='bold')
        # 均佈載重箭頭
        for x in np.linspace(0.3, L - 0.3, 8):
            ax.annotate('', xy=(x, 0.05), xytext=(x, 0.45),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.3))
        ax.text(L / 2, 0.6, f'$w = {self.w}$ kN/m', color='red', ha='center', fontsize=11)
        ax.annotate('', xy=(L - 0.3, -0.75), xytext=(L + 0.3, -0.75),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
        ax.text(L, -1.05, r'$\theta_B$', color='purple', fontsize=13, ha='center')
        ax.set_xlim(-1.5, L + 1.5)
        ax.set_ylim(-1.3, 1.0)
        ax.set_aspect('equal')
        ax.set_title('Figure 1: Propped Cantilever Beam — Geometry, Load & DOF')
        ax.grid(True, linestyle='--', alpha=0.5)

    def build_moment_equations(self):
        EI, L, w = self.EI, self.L, self.w
        thB = self.theta_B
        FEM_AB = w * L**2 / 12
        FEM_BA = -w * L**2 / 12
        return {
            'M_{AB}': 2 * EI / L * thB + FEM_AB,
            'M_{BA}': 2 * EI / L * (2 * thB) + FEM_BA,
        }

    def build_equilibrium_equations(self, moments):
        # B端是滾支承，沒有彎矩傳遞，取代「節點力矩平衡」的邊界條件是 M_BA=0
        eq1 = sp.Eq(moments['M_{BA}'], 0)
        return [("B端邊界條件（滾支承不傳彎矩） M_BA = 0", eq1)]

    def compute_reactions(self, moments_val):
        # 已用 anastruct 驗證: R_A=5wL/8 (固定端), R_B=3wL/8 (滾支承)
        L, w = self.L, self.w
        R_A = 5 * w * L / 8
        R_B = 3 * w * L / 8
        return {'R_A (kN, 固定端反力)': R_A, 'R_B (kN, 滾支承反力)': R_B}

    def teaching_breakdown(self, moments_val, reactions, solution):
        L, w = self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        r_a = reactions['R_A (kN, 固定端反力)']
        r_b = reactions['R_B (kN, 滾支承反力)']
        FEM_AB, FEM_BA = w * L**2 / 12, -w * L**2 / 12
        C1 = (0 - m_ab - 0.5 * w * L**2) / L  # 剪力函數係數 (從A端起算)
        x_star = -C1 / w
        m_star = m_ab + C1 * x_star + 0.5 * w * x_star**2

        return [
            {
                'title': '列出桿端彎矩方程式',
                'problem': f'一根梁 A 端固定、B 端滾支承，跨度 L={L} m，'
                           f'承受均佈載重 w={w} kN/m，試以傾角變位法列出 '
                           r'$M_{AB}, M_{BA}$ 的表達式。',
                'concept': '固定端 θ_A=0，B 端轉角 θ_B 未知；沒有側移(ψ=0)。'
                           '均佈載重的固定端彎矩(FEM)近端正、遠端負，這是套用'
                           '一般式前要先查出來的兩個常數。',
                'formula': r'$M_{ij}=\frac{2EI}{L}(2\theta_i+\theta_j-3\psi)+FEM_{ij}, '
                           r'\quad FEM_{AB}=\frac{wL^2}{12},\ FEM_{BA}=-\frac{wL^2}{12}$',
                'substitution': f'L={L}, w={w} → FEM_AB=+{FEM_AB:.1f}, FEM_BA={FEM_BA:.1f}；'
                                r'$\theta_A=0, \psi=0$',
                'answer': (rf'$M_{{AB}}=\frac{{2EI}}{{{L}}}\theta_B+{FEM_AB:.1f}$'
                           rf', $M_{{BA}}=\frac{{2EI}}{{{L}}}(2\theta_B){FEM_BA:+.1f}$'),
                'keywords': ['傾角變位法一般式', 'FEM', '固定端彎矩', 'θ_A=0', 'ψ=0', '2EI/L'],
                'grading': [
                    ('寫出正確的一般式', 2),
                    ('FEM_AB, FEM_BA 正負號正確', 2),
                    ('正確代入 θ_A=0', 1),
                    ('最終兩式係數與常數項正確', 2),
                ],
            },
            {
                'title': '求解未知數 θ_B',
                'problem': '利用 B 端滾支承不能承受彎矩的邊界條件，求 θ_B。',
                'concept': '滾支承=鉸接、不傳遞彎矩，所以 M_BA=0 這個邊界條件本身'
                           '就是唯一需要的方程式(跟「節點力矩平衡」是同一類型的方程式，'
                           '只是這裡只接了一根桿件)。',
                'formula': r'$M_{BA}=0$',
                'substitution': f'代入第1小題的 M_BA 表達式',
                'answer': rf'$\theta_B=\dfrac{{{-FEM_BA:.1f}}}{{2EI/{L}}}=\dfrac{{90}}{{EI}}$',
                'keywords': ['邊界條件', 'M_BA=0', '滾支承不傳彎矩'],
                'grading': [
                    ('正確寫出邊界條件方程式', 2),
                    ('正確解出 θ_B', 2),
                ],
            },
            {
                'title': '回代求桿端彎矩數值',
                'problem': '將 θ_B 代回，求 M_AB、M_BA 的實際數值。',
                'concept': '這一步 EI 會自動消掉(因為 θ_B 本身跟 1/EI 成正比)，這是'
                           '靜不定結構用位移法求解的一個特徵——只要材料是均質的單一 EI，'
                           '最終彎矩值就跟 EI 大小無關，只跟相對剛度分布有關。',
                'formula': '直接代入第1小題的式子',
                'substitution': r'$\theta_B=90/EI$',
                'answer': rf'$M_{{AB}}={m_ab:.1f}$ kN·m，$M_{{BA}}={m_ba:.1f}$ kN·m',
                'keywords': ['EI消去', '回代', f'固定端彎矩={m_ab:.0f}'],
                'grading': [
                    (f'M_AB={m_ab:.1f} kN·m', 2),
                    (f'M_BA={m_ba:.1f} kN·m，且能說明這是邊界條件的直接結果', 2),
                ],
            },
            {
                'title': '求支承反力',
                'problem': '求 A、B 兩端的垂直反力 R_A、R_B。',
                'concept': '這是標準靜不定梁的固定端反力公式，可以用「先解剪力函數再'
                           '代入端點」的方式反推，也可以直接用標準propped cantilever'
                           '公式做交叉檢查。',
                'formula': r'$V(x)=\frac{M_{BA}-M_{AB}-\frac12wL^2}{L}+wx,\ R_A=-V(0),\ '
                           r'R_B=V(L)$；標準結果 $R_A=\frac{5wL}{8}, R_B=\frac{3wL}{8}$',
                'substitution': f'w={w}, L={L}',
                'answer': rf'$R_A=\dfrac{{5\times{w}\times{L}}}{{8}}={r_a:.1f}$ kN，'
                          rf'$R_B=\dfrac{{3\times{w}\times{L}}}{{8}}={r_b:.1f}$ kN',
                'keywords': ['5wL/8', '3wL/8', '剪力函數', 'ΣFy=0'],
                'grading': [
                    (f'R_A={r_a:.1f} kN', 2),
                    (f'R_B={r_b:.1f} kN', 2),
                    (f'驗證 R_A+R_B=wL={w*L:.0f}(交叉檢查習慣)', 1),
                ],
            },
            {
                'title': '找最大彎矩位置與數值(跨內)',
                'problem': '求梁跨內剪力等於零的位置，以及該處的彎矩值。',
                'concept': '彎矩極值必發生在剪力等於零處——這是內力圖最基本、也最'
                           '常考的關係，剪力圖跟彎矩圖能互相驗證就是靠這個。',
                'formula': r'$V(x)=0 \Rightarrow x^*=-C_1/w$；'
                           r'$M(x^*)=M_{AB}+C_1x^*+\frac12wx^{*2}$',
                'substitution': f'C1={C1:.1f}, w={w}',
                'answer': rf'$x^*={x_star:.2f}$ m，$M(x^*)={m_star:.1f}$ kN·m',
                'keywords': ['V=0', '彎矩極值', '拋物線頂點', f'{m_star:.1f} kN·m', f'x={x_star:.2f}m'],
                'grading': [
                    (f'正確用 V=0 求出 x*={x_star:.2f}m', 2),
                    (f'正確算出 M(x*)={m_star:.1f} kN·m', 2),
                    ('能說明此點是全跨最大彎矩，並與端點值比較何者較大用於設計', 1),
                ],
            },
        ]

    def draw_sfd(self, ax, moments_val):
        from sd_framework import member_shear_curve
        L, w = self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        scale = 0.02

        ax.plot([0, L], [0, 0], 'k-', lw=4, label='Beam')
        x = np.linspace(0, L, 200)
        v_line = member_shear_curve(x, L, w, m_ab, m_ba)
        ax.plot(x, v_line * scale, 'b-', lw=2, label='SFD (kN)')
        ax.fill_between(x, 0, v_line * scale, color='blue', alpha=0.15)

        ax.text(0, v_line[0] * scale - 0.25, f'{v_line[0]:.2f}', color='darkblue',
                ha='center', fontweight='bold')
        ax.text(L, v_line[-1] * scale + 0.25, f'{v_line[-1]:.2f}', color='darkblue',
                ha='center', fontweight='bold')
        # 剪力過零點 (彎矩極值所在位置，跟BMD的極值點是同一個x)
        i_zero = int(np.argmin(np.abs(v_line)))
        ax.plot(x[i_zero], 0, 'ko', ms=5)
        ax.text(x[i_zero], -0.35, f'V=0\nx={x[i_zero]:.2f}m', color='black',
                ha='center', fontsize=9)

        ax.set_xlim(-1, L + 1)
        ax.set_title('Figure: Shear Force Diagram (SFD) [kN]')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Shear offset (scaled)')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')
        return True

    def draw_bmd(self, ax, moments_val):
        from sd_framework import member_moment_curve
        L, w = self.L, self.w
        m_ab, m_ba = moments_val['M_{AB}'], moments_val['M_{BA}']
        scale = 0.03

        ax.plot([0, L], [0, 0], 'k-', lw=4, label='Beam')
        x = np.linspace(0, L, 200)
        # 梁上有均佈載重 -> 用拋物線；邊界值直接用兩端 raw 值即可
        # (這是唯一一根樑,沒有"遠端負號"問題 — 那個問題只出現在
        #  同一根水平桿件兩端都連著別的桿件、需要跟別人交界時；
        #  這裡B端本身就是M=0,不需要額外轉換,已用剪力對過anastruct)
        m_line = member_moment_curve(x, L, w, m_ab, m_ba)
        ax.plot(x, m_line * scale, 'r--', lw=2, label='BMD (kN·m)')
        ax.fill_between(x, 0, m_line * scale, color='red', alpha=0.15)

        ax.text(0, m_ab * scale - 0.3, f'{m_ab:.2f}', color='darkred',
                ha='center', fontweight='bold')
        ax.text(L, m_ba * scale - 0.3, f'{m_ba:.2f}', color='darkred',
                ha='center', fontweight='bold')
        # 找真正的極值點 (兩端彎矩不對稱時,極值不會剛好在跨中)
        i_peak = int(np.argmin(m_line))
        x_peak, m_peak = x[i_peak], m_line[i_peak]
        ax.text(x_peak, m_peak * scale - 0.3, f'{m_peak:.2f}\n(x={x_peak:.2f}m)',
                color='darkred', ha='center', fontweight='bold')

        ax.set_xlim(-1, L + 1)
        ax.set_title('Figure 2: Bending Moment Diagram (BMD) [kN·m]')
        ax.set_xlabel('X Position (m)')
        ax.set_ylabel('Moment offset (scaled)')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')
