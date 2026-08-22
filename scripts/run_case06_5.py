"""
Case-06.5 獨立驅動腳本——二層剛架 + 側移 + 梁均佈載重（組合載重）。

跟 Case-06 用同一個 model 類別 TwoStorySwayFrameProblem，只是 w1、w2
(梁上均佈載重) 預設不是 0。這個腳本存在的意義單純是「開箱即用，不用自己
加 --w1 --w2 參數」，邏輯上跟 run_case06.py --w1 24 --w2 18 是同一件事。

wget 抓下 sd_framework.py、model_two_story_sway.py、這個檔案這三個檔案
放同一個資料夾後，直接執行就能跑，不需要 Jupyter/Colab：

    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/sd_framework.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/samples/model_two_story_sway.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/scripts/run_case06_5.py
    python3 run_case06_5.py

三種輸入方式，用命令列參數控制:
  python3 run_case06_5.py                查看/使用預設值
  python3 run_case06_5.py --interactive  互動輸入每個參數(直接Enter用預設值)
  python3 run_case06_5.py --H1 4.5 --H2 4 --L 7 --P1 20 --P2 12 --w1 28 --w2 20
"""
import argparse

from sd_framework import SlopeDeflectionSolver, prompt_for_params
from model_two_story_sway import TwoStorySwayFrameProblem

DEFAULTS = {
    'H1': 4.0, 'H2': 3.5, 'L': 6.0,
    'P1': 15.0, 'P2': 10.0,
    'w1': 24.0, 'w2': 18.0,  # 跟run_case06.py唯一的差別: 這裡預設>0
    'EI': 15000.0,
}

PARAM_SPECS = [
    ('H1', '一樓層高 m', DEFAULTS['H1'], float),
    ('H2', '二樓層高 m', DEFAULTS['H2'], float),
    ('L', '跨度 m', DEFAULTS['L'], float),
    ('P1', '一樓樓板水平力 kN', DEFAULTS['P1'], float),
    ('P2', '屋頂水平力 kN', DEFAULTS['P2'], float),
    ('w1', '一樓梁均佈載重 kN/m', DEFAULTS['w1'], float),
    ('w2', '屋頂梁均佈載重 kN/m', DEFAULTS['w2'], float),
    ('EI', '撓曲勁度 kN·m^2 (只影響變形圖大小)', DEFAULTS['EI'], float),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description='Case-06.5 二層剛架+側移+梁均佈載重(組合載重) —— 傾角變位法求解')
    parser.add_argument('--interactive', action='store_true',
                         help='互動輸入每個參數(直接按Enter使用預設值)')
    parser.add_argument('--H1', type=float, default=None)
    parser.add_argument('--H2', type=float, default=None)
    parser.add_argument('--L', type=float, default=None)
    parser.add_argument('--P1', type=float, default=None)
    parser.add_argument('--P2', type=float, default=None)
    parser.add_argument('--w1', type=float, default=None)
    parser.add_argument('--w2', type=float, default=None)
    parser.add_argument('--EI', type=float, default=None)
    parser.add_argument('--no-handout', action='store_true',
                         help='只跑 solve_and_report() 手算過程，不額外印教學講義五張圖')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.interactive:
        params = prompt_for_params(PARAM_SPECS)
    else:
        params = {k: (getattr(args, k) if getattr(args, k) is not None else DEFAULTS[k])
                  for k in ('H1', 'H2', 'L', 'P1', 'P2', 'w1', 'w2', 'EI')}
        print("使用參數:", params,
              "  (加 --interactive 可以互動輸入，或用 --H1 --H2 --L --P1 --P2 --w1 --w2 --EI 直接指定)")

    problem = TwoStorySwayFrameProblem(H1=params['H1'], H2=params['H2'], L=params['L'],
                                        P1=params['P1'], P2=params['P2'],
                                        w1=params['w1'], w2=params['w2'],
                                        EI_numeric=params['EI'])
    solver = SlopeDeflectionSolver(problem)
    solver.solve_and_report()

    if not args.no_handout:
        solver.print_teaching_handout()


if __name__ == '__main__':
    main()
