"""
Case-02 獨立驅動腳本——wget 抓下 sd_framework.py、model_two_span_beam.py、
這個檔案這三個檔案放同一個資料夾後，直接執行就能跑，不需要 Jupyter/Colab：

    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/sd_framework.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/samples/model_two_span_beam.py
    wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/scripts/run_case02.py
    python3 run_case02.py

在 Colab / Jupyter 裡直接 %run run_case02.py 或整段貼進 cell 也一樣能動
(sd_framework.py 會自動偵測環境，圖片在 notebook 顯示、在純終端機存檔)。

三種輸入方式，用命令列參數控制:
  python3 run_case02.py                查看/使用預設值
  python3 run_case02.py --interactive  互動輸入每個參數(直接Enter用預設值)
  python3 run_case02.py --L1 6 --L2 7 --w1 18 --w2 22 --EI 20000   直接指定
"""
import argparse

from sd_framework import SlopeDeflectionSolver, prompt_for_params
from model_two_span_beam import TwoSpanBeamProblem

DEFAULTS = {
    'L1': 5.0,      # AB跨跨度 (m)
    'L2': 6.0,      # BC跨跨度 (m)
    'w1': 15.0,     # AB跨均佈載重 (kN/m)
    'w2': 20.0,     # BC跨均佈載重 (kN/m)
    'EI': 15000.0,  # 撓曲勁度 (kN·m^2)，只影響變形圖大小，不影響彎矩/剪力/反力
}

PARAM_SPECS = [
    ('L1', 'AB跨跨度 m', DEFAULTS['L1'], float),
    ('L2', 'BC跨跨度 m', DEFAULTS['L2'], float),
    ('w1', 'AB跨均佈載重 kN/m', DEFAULTS['w1'], float),
    ('w2', 'BC跨均佈載重 kN/m', DEFAULTS['w2'], float),
    ('EI', '撓曲勁度 kN·m^2 (只影響變形圖大小)', DEFAULTS['EI'], float),
]


def parse_args():
    parser = argparse.ArgumentParser(description='Case-02 二次靜不定連續梁 —— 傾角變位法求解')
    parser.add_argument('--interactive', action='store_true',
                         help='互動輸入每個參數(直接按Enter使用預設值)')
    parser.add_argument('--L1', type=float, default=None, help=f'AB跨跨度 m (預設 {DEFAULTS["L1"]})')
    parser.add_argument('--L2', type=float, default=None, help=f'BC跨跨度 m (預設 {DEFAULTS["L2"]})')
    parser.add_argument('--w1', type=float, default=None, help=f'AB跨均佈載重 kN/m (預設 {DEFAULTS["w1"]})')
    parser.add_argument('--w2', type=float, default=None, help=f'BC跨均佈載重 kN/m (預設 {DEFAULTS["w2"]})')
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
                  for k in ('L1', 'L2', 'w1', 'w2', 'EI')}
        print("使用參數:", params,
              "  (加 --interactive 可以互動輸入，或用 --L1 --L2 --w1 --w2 --EI 直接指定)")

    problem = TwoSpanBeamProblem(L1=params['L1'], L2=params['L2'],
                                  w1=params['w1'], w2=params['w2'],
                                  EI_numeric=params['EI'])
    solver = SlopeDeflectionSolver(problem)
    solver.solve_and_report()

    if not args.no_handout:
        solver.print_teaching_handout()


if __name__ == '__main__':
    main()
