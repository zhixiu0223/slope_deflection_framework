"""
Case-04 獨立驅動腳本——wget 抓下 sd_framework.py、model_sway_frame.py、
這個檔案這三個檔案放同一個資料夾後，直接執行就能跑，不需要 Jupyter/Colab：

    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/sd_framework.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/samples/model_sway_frame.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/scripts/run_case04.py
    python3 run_case04.py

在 Colab / Jupyter 裡直接 %run run_case04.py 或整段貼進 cell 也一樣能動
(sd_framework.py 會自動偵測環境，圖片在 notebook 顯示、在純終端機存檔)。

三種輸入方式，用命令列參數控制:
  python3 run_case04.py                查看/使用預設值
  python3 run_case04.py --interactive  互動輸入每個參數(直接Enter用預設值)
  python3 run_case04.py --H 5 --L 8 --P 20 --EI 20000   直接用命令列指定

想順便加梁上均佈載重(即Case-04.5)，直接加 --w 即可，不用另外的腳本：
  python3 run_case04.py --w 24
"""
import argparse

from sd_framework import SlopeDeflectionSolver, prompt_for_params
from model_sway_frame import SwayFrameProblem

DEFAULTS = {
    'H': 4.0,       # 柱高 (m)
    'L': 6.0,       # 梁跨 (m)
    'P': 12.0,      # B點水平集中載重 (kN)
    'w': 0.0,       # 梁上均佈載重 (kN/m)，預設0即Case-04原題；>0即Case-04.5
    'EI': 15000.0,  # 撓曲勁度 (kN·m^2)，只影響變形圖大小，不影響彎矩/剪力/反力
}

PARAM_SPECS = [
    ('H', '柱高 m', DEFAULTS['H'], float),
    ('L', '梁跨 m', DEFAULTS['L'], float),
    ('P', 'B點水平集中載重 kN', DEFAULTS['P'], float),
    ('w', '梁上均佈載重 kN/m (0=Case-04原題, >0=Case-04.5組合載重)', DEFAULTS['w'], float),
    ('EI', '撓曲勁度 kN·m^2 (只影響變形圖大小)', DEFAULTS['EI'], float),
]


def parse_args():
    parser = argparse.ArgumentParser(description='Case-04 側移單跨剛架 —— 傾角變位法求解')
    parser.add_argument('--interactive', action='store_true',
                         help='互動輸入每個參數(直接按Enter使用預設值)')
    parser.add_argument('--H', type=float, default=None, help=f'柱高 m (預設 {DEFAULTS["H"]})')
    parser.add_argument('--L', type=float, default=None, help=f'梁跨 m (預設 {DEFAULTS["L"]})')
    parser.add_argument('--P', type=float, default=None, help=f'B點水平集中載重 kN (預設 {DEFAULTS["P"]})')
    parser.add_argument('--w', type=float, default=None, help=f'梁上均佈載重 kN/m (預設 {DEFAULTS["w"]})')
    parser.add_argument('--EI', type=float, default=None, help=f'撓曲勁度 kN·m^2 (預設 {DEFAULTS["EI"]})')
    parser.add_argument('--no-handout', action='store_true',
                         help='只跑 solve_and_report() 手算過程，不額外印教學講義五張圖')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.interactive:
        params = prompt_for_params(PARAM_SPECS)
    else:
        params = {k: (getattr(args, k) if getattr(args, k) is not None else DEFAULTS[k])
                  for k in ('H', 'L', 'P', 'w', 'EI')}
        print("使用參數:", params,
              "  (加 --interactive 可以互動輸入，或用 --H --L --P --w --EI 直接指定)")

    problem = SwayFrameProblem(H=params['H'], L=params['L'], P=params['P'],
                                w=params['w'], EI_numeric=params['EI'])
    solver = SlopeDeflectionSolver(problem)
    solver.solve_and_report()

    if not args.no_handout:
        solver.print_teaching_handout()


if __name__ == '__main__':
    main()
