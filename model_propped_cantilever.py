import numpy as np
import sympy as sp


class PropChedCantileverProblem:
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
        ax.text(L / 2, -0.9, r'$\theta_B$', color='purple', fontsize=13, ha='center')
        ax.annotate('', xy=(L - 0.3, -0.75), xytext=(L + 0.3, -0.75),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.5',
                                     color='purple', lw=2))
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
        return [eq1]

    def compute_reactions(self, moments_val):
        # 已用 anastruct 驗證: R_A=5wL/8 (固定端), R_B=3wL/8 (滾支承)
        L, w = self.L, self.w
        R_A = 5 * w * L / 8
        R_B = 3 * w * L / 8
        return {'R_A (kN, 固定端反力)': R_A, 'R_B (kN, 滾支承反力)': R_B}

    def draw_bmd(self, ax, moments_val):
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
