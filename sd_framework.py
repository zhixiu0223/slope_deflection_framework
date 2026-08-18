import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from abc import ABC, abstractmethod
from IPython.display import Markdown, display

sp.init_printing()


# ============================================================
# 共用工具：桿件彎矩沿長度的分布 (含均佈載重 w 的一般化版本)
# ============================================================
def member_moment_curve(s, length, w, M_i, M_j):
    """
    計算桿件內部彎矩沿桿長的分布 M(s)，s 為由 i 端起算的局部座標 (0~length)。
    - 無側向載重 (w=0)：退化為 i, j 兩端值的線性內插 (柱、無載重梁適用)
    - 有均佈載重 w (力/長度)：抵滿足 M(0)=M_i, M(L)=M_j 邊界條件的拋物線
      (由 d²M/ds² = w 積分兩次求得)，可正確反映跨中彎矩，而不是被兩端值
      的直線內插蓋掉 (這對兩端彎矩接近正負對稱、但跨中另有較大彎矩的
      受均佈載重梁尤其重要)。
    """
    C1 = (M_j - M_i - 0.5 * w * length**2) / length
    return M_i + C1 * s + 0.5 * w * s**2


def member_shear_curve(s, length, w, M_i, M_j):
    """
    member_moment_curve 的對應剪力函式: V(s) = dM/ds = C1 + w*s
    (跟彎矩用同一個 C1，兩者必須自洽——這也是為什麼前幾輪都用剪力
    去反查彎矩圖畫法對不對的原因：M(s) 和 V(s) 本來就是同一個 C1
    推出來的，不會不一致)
    """
    C1 = (M_j - M_i - 0.5 * w * length**2) / length
    return C1 + w * s


def member_offset_curve(x0, y0, x1, y1, s, m_values, scale):
    """
    通用的桿件內力圖偏移座標計算，取代過去每個Case各自手寫的x/y偏移公式
    （柱一套、梁又一套，還常常寫錯方向）。

    這個函式畫出來的圖是「拉力彎矩圖」(Tension-Side Bending Moment
    Diagram)：偏移方向就是該處實際受拉的那一側，不是單純套一個數學
    座標正負號——已經用最單純無爭議的案例（懸臂梁，全長已知受拉側
    唯一）驗證過 anastruct 本身就是這樣畫的，我們的規則是照anastruct
    的實際輸出反推校準出來的，跟它一致。這也是為什麼看這張圖就能
    直接判斷配筋位置，不用再心算正負號對應哪一側。

    規則: 偏移方向 = 沿著桿件「近端(x0,y0)→遠端(x1,y1)」前進方向，
    逆時針轉90度，正值往這個方向偏移。這個規則套用在水平桿件（近端
    到遠端由左到右）會自動算出「正值往上偏移」，套用在垂直桿件（近端
    到遠端由下到上）會自動算出「正值往左偏移」——這對任意角度的桿件
    都適用，包括未來斜屋頂剛架(S-01)需要的斜桿件。

    參數:
      x0,y0,x1,y1: 桿件近端、遠端的座標
      s: 沿桿件長度的局部座標陣列 (0~length)
      m_values: 對應每個s的彎矩或剪力值 (通常是 member_moment_curve
                或 member_shear_curve 的輸出)
      scale: 縮放比例
    回傳: (x, y) 畫圖用座標陣列
    """
    length = np.hypot(x1 - x0, y1 - y0)
    dx, dy = (x1 - x0) / length, (y1 - y0) / length
    perp_x, perp_y = -dy, dx  # 逆時針90度
    frac = s / length
    base_x = x0 + frac * (x1 - x0)
    base_y = y0 + frac * (y1 - y0)
    return base_x + perp_x * m_values * scale, base_y + perp_y * m_values * scale


# ============================================================
# 策略介面 (Strategy Interface)
# ============================================================
class SlopeDeflectionProblem(ABC):
    """
    傾角變位法問題的策略介面。
    每一種結構模型（單層側移剛架、二層重力剛架...）只需要繼承這個類別，
    把「模型特有」的部分實作出來；共用的「步驟1~6」解題流程交給
    SlopeDeflectionSolver（Template Method）負責，輸出格式統一比照
    手寫詳解的呈現方式。
    """

    @abstractmethod
    def get_unknowns(self) -> dict:
        """回傳未知位移量的 sympy 符號，例如 {'theta_B': ...}"""

    @abstractmethod
    def describe(self) -> str:
        """題目文字敘述 (Markdown)：結構、幾何、材料、載重、邊界條件，用於步驟1。
        不含自由度選取的說明——那部分獨立在 describe_dof()。"""

    @abstractmethod
    def describe_dof(self) -> str:
        """
        自由度(未知位移量)選取的說明 (Markdown)，用於步驟1。跟 describe()
        分開成獨立方法，是因為這一步是整個傾角變位法最容易出錯、也最該
        覆核的地方——自由度選錯或漏掉一個，後面所有方程式都會建立在錯誤
        的基礎上，整題就全錯了，值得在輸出裡獨立成一個顯眼的區塊，
        不要被埋沒在結構描述裡面。
        """

    @abstractmethod
    def draw_geometry(self, ax):
        """畫結構幾何圖 (圖1)，用於步驟1"""

    @abstractmethod
    def build_moment_equations(self) -> dict:
        """回傳桿端彎矩符號運算式 {'M_{AB}': expr, ...}，用於步驟2"""

    @abstractmethod
    def build_equilibrium_equations(self, moments: dict) -> list:
        """
        回傳平衡方程式，用於步驟3。格式為 list[tuple[str, sp.Eq]]：
        每一條方程式搭配一句說明它是哪個節點/桿件、哪一種平衡條件
        (例如 "節點B力矩平衡 ΣM_B=0"、"C端邊界條件(滾支承) M_CB=0"、
        "整體水平力平衡 ΣFx=0")，求解器會把說明跟方程式一起印出來，
        不再只丟一堆沒有上下文的裸方程式。
        """

    def compute_reactions(self, moments_val: dict) -> dict:
        """(可選) 由彎矩回代算支承反力/軸力，用於步驟5。預設不計算。"""
        return {}

    @abstractmethod
    def draw_bmd(self, ax, moments_val: dict):
        """畫彎矩圖 (圖2)，用於步驟6"""

    def draw_sfd(self, ax, moments_val: dict) -> bool:
        """
        (可選) 畫剪力圖 (SFD)，用於步驟6。若模型有實作，回傳 True 並把圖
        畫進傳入的 ax；預設不提供 (回傳 False)，求解器會印出提示而不出圖。
        """
        return False

    def draw_tension_side(self, ax, moments_val: dict) -> bool:
        """
        (可選) 在結構圖上直接標註每個桿端的受拉/受壓側 (拉力彎矩圖的
        文字版對照)，若模型有實作，回傳 True 並把圖畫進傳入的 ax；
        預設不提供 (回傳 False)。適合搭配 member_offset_curve 的偏移
        方向來自動判斷: 偏移方向那一側 = 受拉側 (已用懸臂梁這種答案
        唯一的案例驗證過 anastruct 真的是這樣畫的)。
        """
        return False

    def draw_deformed_shape(self, ax, moments_val: dict, solution: dict) -> bool:
        """
        (可選) 在同一張圖上疊加「原始結構 + 變形後形狀」。若模型有實作，
        回傳 True 並把圖畫進傳入的 ax；預設不提供 (回傳 False)。

        做法：對每根桿件，用拉力側 M(s) 轉成材料力學 sagging 慣例
        (M_sag=-M_hog)，積分兩次 EI*u''=M_sag 得到「桿件局部座標系
        正方向」(近端->遠端逆時針轉90度) 的橫向位移，邊界條件依各桿件
        的支承/連接方式而定 (case-specific，沒辦法通用化)。**算出來的
        u(s) 一定要再套 member_offset_curve 轉成畫圖座標，不能直接當
        全域x或y用**——這是實際踩過的坑：柱子的近端->遠端方向是垂直的，
        逆時針轉90度後的「正方向」其實是全域-x，直接套全域+x會整個
        鏡像顛倒(已用anastruct的show_displacement()實際畫圖座標逐點
        驗證過，修正後精確吻合)。
        """
        return False

    def teaching_breakdown(self, moments_val: dict, reactions: dict, solution: dict) -> list:
        """
        (可選) 回傳這個模型的「教學詳解 + 評分要點」分解，用於步驟8。
        每個小題是一個 dict，需要以下 key：
          - title:         小題標題 (str)
          - problem:       題目敘述 (str)
          - concept:       概念解析 (str)
          - formula:       公式引用 (str, 可含 LaTeX)
          - substitution:  帶入數據說明 (str)
          - answer:        詳細參考答案 (str, 可含 LaTeX)
          - keywords:       關鍵字/chunk 列表 (list[str])
          - grading:        評分要點列表 (list[tuple[str, int]])，每項是
                            (要點敘述, 配分)
        預設回傳空列表 (不提供)，求解器會印出提示而不出教學詳解——
        這是刻意設計成可選的，因為每題的概念解析、配分是需要針對該
        Case 手動設計的教學內容，不是所有 Case 一開始就要準備好。
        """
        return []


# ============================================================
# Template Method：共用的「步驟1~6」解題骨架
# ============================================================
class SlopeDeflectionSolver:
    """
    通用傾角變位法求解器 (Template Method)。
    計算內容全部委託給傳入的 SlopeDeflectionProblem（Strategy），
    這個類別只負責固定不變的六步驟框架與統一格式的美化輸出。
    """

    def __init__(self, problem: SlopeDeflectionProblem):
        self.problem = problem

    @staticmethod
    def _step_header(n, title):
        print("\n" + "=" * 60)
        print(f"【步驟 {n}】{title}")
        print("=" * 60)

    def _solve_core(self):
        """純計算，不印任何東西：算出 moments、平衡方程式、解、回代結果、反力。
        solve_and_report() 跟 print_teaching_handout() 共用這段，避免兩邊各算一次
        還可能算出不一樣結果的風險。"""
        p = self.problem
        moments = p.build_moment_equations()
        labeled_eqs = p.build_equilibrium_equations(moments)
        eqs = [eq for _, eq in labeled_eqs]
        unknowns = p.get_unknowns()
        sol = sp.solve(eqs, tuple(unknowns.values()))
        moments_val = {name: float(expr.subs(sol)) for name, expr in moments.items()}
        reactions = p.compute_reactions(moments_val)
        return moments, labeled_eqs, unknowns, sol, moments_val, reactions

    @staticmethod
    def _annotate_tension_note(ax):
        """
        在彎矩圖上加一行小提示，說明這張圖是拉力側繪製慣例——用英文避免
        matplotlib預設字型(DejaVu Sans)缺中文字產生的警告(之前踩過這個坑，
        中文標題會在Colab印出一長串UserWarning)。詳細的中文說明放在
        print_teaching_handout()的Markdown文字裡，那邊走的是Markdown/HTML
        渲染，沒有這個字型限制。
        """
        ax.text(0.5, -0.08, 'Bending moment diagram drawn on the tension side',
                transform=ax.transAxes, ha='center', fontsize=8.5,
                color='dimgray', style='italic')

    def _print_teaching_breakdown(self, moments_val, reactions, sol):
        """渲染 teaching_breakdown() 的內容 (題目/概念解析/公式引用/帶入數據/
        參考答案/關鍵字/評分要點)。solve_and_report() 的步驟8跟
        print_teaching_handout() 共用這段渲染邏輯，回傳 True/False 代表這個
        model 有沒有提供內容。"""
        p = self.problem
        breakdown = p.teaching_breakdown(moments_val, reactions, sol)
        if not breakdown:
            return False
        total_points = 0
        for i, item in enumerate(breakdown, 1):
            display(Markdown(f"### 第{i}小題：{item['title']}"))
            display(Markdown(f"**題目**：{item['problem']}"))
            display(Markdown(f"**概念解析**：{item['concept']}"))
            display(Markdown(f"**公式引用**：\n\n{item['formula']}"))
            display(Markdown(f"**帶入數據**：{item['substitution']}"))
            display(Markdown(f"**詳細參考答案**：\n\n{item['answer']}"))
            display(Markdown(f"**關鍵字/chunk**：{', '.join(item['keywords'])}"))
            pts_sum = sum(pts for _, pts in item['grading'])
            grading_lines = "\n".join(f"- {desc}（{pts}分）" for desc, pts in item['grading'])
            display(Markdown(f"**評分要點**（本小題共 {pts_sum} 分）：\n\n{grading_lines}"))
            total_points += pts_sum
        display(Markdown(f"---\n**本題總分：{total_points} 分**"))
        return True

    def print_teaching_handout(self):
        """
        產生一份可以直接複製當教學講義用的輸出，只有三塊、沒有步驟編號、
        沒有中間的符號方程式/平衡方程式這些過程 (那些留在 solve_and_report()
        裡)：
          1. 結構受力圖
          2. 教學詳解與評分要點 (原本步驟8的內容)
          3. 剪力圖(SFD) + 彎矩圖(BMD)
        適合放在 solve_and_report() 那個 cell 的下一個 cell，單獨執行、
        單獨截圖/複製，不用夾雜求解過程。
        """
        p = self.problem
        moments, labeled_eqs, unknowns, sol, moments_val, reactions = self._solve_core()

        display(Markdown("## 1. 結構受力圖與自由度"))
        display(Markdown(p.describe()))
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        p.draw_geometry(ax1)
        plt.show()
        display(Markdown(
            "**⚠️ 自由度選取**（這一步選錯或漏掉，後面所有方程式都會建立在"
            "錯誤基礎上、整題全錯，是最需要覆核的一步）：\n\n" + p.describe_dof()
        ))

        display(Markdown("## 2. 教學詳解與評分要點"))
        has_breakdown = self._print_teaching_breakdown(moments_val, reactions, sol)
        if not has_breakdown:
            print("(此模型尚未提供教學詳解)")

        display(Markdown("## 3. 剪力圖 (SFD) 與彎矩圖 (BMD)"))
        fig_sfd, ax_sfd = plt.subplots(figsize=(8, 5))
        has_sfd = p.draw_sfd(ax_sfd, moments_val)
        if has_sfd:
            plt.show()
        else:
            plt.close(fig_sfd)
            print("(此模型尚未實作剪力圖，略過)")

        fig2, ax2 = plt.subplots(figsize=(8, 6))
        p.draw_bmd(ax2, moments_val)
        self._annotate_tension_note(ax2)
        plt.show()
        plt.close('all')

        display(Markdown(
            "## 4. 拉力彎矩圖對照（受拉/受壓側標註）\n\n"
            "本專案之彎矩圖採構件拉力側繪製。\n\n"
            "彎矩正負號仍依局部座標系與構件端力約定定義；圖形所在側則"
            "代表實際截面的拉力側，而非單純由正負號決定。\n\n"
            "已用最單純無爭議的案例(懸臂梁)驗證過 anastruct 本身就是這樣"
            "畫的，不是我們自己認定的。這裡額外把受拉/受壓標成文字，"
            "方便直接核對。"
        ))
        fig_t, ax_t = plt.subplots(figsize=(8, 7))
        has_tension = p.draw_tension_side(ax_t, moments_val)
        if has_tension:
            plt.show()
        else:
            plt.close(fig_t)
            print("(此模型尚未實作拉力側標註圖，略過)")

        display(Markdown(
            "## 5. 變形圖對照（原始結構 vs 變形後形狀）\n\n"
            "灰色虛線是原始結構，藍色實線是變形後形狀（放大顯示，方便肉眼"
            "比對）。這是從彎矩圖本身反推出來的，不是重新用矩陣位移法算——"
            "已用 anastruct 的 `show_displacement()` 逐點比對過畫圖座標。"
        ))
        fig_d, ax_d = plt.subplots(figsize=(8, 7))
        has_deformed = p.draw_deformed_shape(ax_d, moments_val, sol)
        if has_deformed:
            plt.show()
        else:
            plt.close(fig_d)
            print("(此模型尚未實作變形圖，略過)")

    def solve_and_report(self):
        p = self.problem

        # ---------------- 步驟1：題目與幾何 ----------------
        self._step_header(1, "題目定義、幾何/材料參數與自由度標示")
        display(Markdown("**① 結構定義、幾何與邊界條件**"))
        display(Markdown(p.describe()))
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        p.draw_geometry(ax1)
        plt.show()
        display(Markdown(
            "**② ⚠️ 自由度選取**（這一步選錯或漏掉，後面所有方程式都會建立在"
            "錯誤基礎上、整題全錯，是最需要覆核的一步）：\n\n" + p.describe_dof()
        ))

        # ---------------- 步驟2：桿端彎矩方程式 ----------------
        self._step_header(2, "寫出桿端彎矩方程式")
        display(Markdown(
            "**① 公式引用**（傾角變位法一般式，對任何桿件 i→j 都適用，跟結構種類無關）：\n\n"
            r"$$M_{ij} = \frac{2EI}{L}\left(2\theta_i + \theta_j - 3\psi\right) + FEM_{ij}$$"
            "\n\n其中 $\\theta_i,\\theta_j$ 為兩端轉角，$\\psi=\\Delta/L$ 為側移角"
            "（無側移時 $\\psi=0$），$FEM_{ij}$ 為固定端彎矩(依載重種類查表)。"
        ))
        moments, labeled_eqs, unknowns, sol, moments_val, reactions = self._solve_core()
        display(Markdown(
            "**② 代入本題的邊界條件、跨長與載重**，得到每根桿件的具體算式："
        ))
        for name, expr in moments.items():
            display(sp.Eq(sp.Symbol(name), expr))

        # ---------------- 步驟3：平衡方程式 ----------------
        self._step_header(3, "建立平衡方程式")
        display(Markdown("**平衡方程式**（每條方程式對應哪個節點/桿件、哪一種平衡條件）："))
        for label, eq in labeled_eqs:
            display(Markdown(f"- {label}"))
            display(eq)

        # ---------------- 步驟4：解聯立方程式 ----------------
        self._step_header(4, "求解聯立方程式 (未知位移量)")
        display(Markdown("**位移求解結果：**"))
        for name, sym in unknowns.items():
            display(sp.Eq(sp.Symbol(name), sol[sym]))

        # ---------------- 步驟5：回代求彎矩與反力 ----------------
        self._step_header(5, "計算真實桿端彎矩與反力")
        display(Markdown("**最終桿端彎矩計算結果 (kN·m)：**"))
        for name, val in moments_val.items():
            print(f"{name} = {val:.3f} kN·m")

        if reactions:
            print()
            for name, val in reactions.items():
                print(f"-> {name} = {val:.3f}")

        # ---------------- 步驟6：剪力圖 (SFD) ----------------
        self._step_header(6, "繪製剪力圖 (SFD)")
        fig_sfd, ax_sfd = plt.subplots(figsize=(8, 5))
        has_sfd = p.draw_sfd(ax_sfd, moments_val)
        if has_sfd:
            plt.show()
        else:
            plt.close(fig_sfd)
            print("(此模型尚未實作剪力圖，略過)")

        # ---------------- 步驟7：彎矩圖 (BMD) ----------------
        self._step_header(7, "繪製彎矩圖 (BMD)")
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        p.draw_bmd(ax2, moments_val)
        self._annotate_tension_note(ax2)
        plt.show()
        plt.close('all')

        # 教學詳解與評分要點已移到 print_teaching_handout()，這裡不再重複
        # (solve_and_report() 專注在「手算過程」，教學詳解是另一種呈現方式)

        return {"moments": moments_val, "reactions": reactions, "solution": sol}
