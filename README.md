# slope_deflection_framework
[![Execute notebook & verify results](https://github.com/zhixiu0223/slope_deflection_framework/actions/workflows/run-notebooks.yml/badge.svg)](https://github.com/zhixiu0223/slope_deflection_framework/actions/workflows/run-notebooks.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


傾角變位法教學專案，架構參照 [pyfem-plastic-hinge](https://github.com/zhixiu0223/pyfem-plastic-hinge)：
Case 編號 notebook，每個 Case 都自成一個可獨立在 Colab 執行的教學單元，
用傾角變位法手算 + anastruct 獨立 FEM 建模 + 剪力交叉檢查 三方比對。

見 `ROADMAP.md` 了解目前進度與課程規劃。

## 檔案說明

- `sd_framework.py` — 共用引擎 (Template Method)：`SlopeDeflectionProblem`
  規格介面 + `SlopeDeflectionSolver` 六步驟求解流程，不因結構種類而變。
- `model_*.py` — 每個 Case 專屬的 Strategy 實作，把特定結構的幾何、
  彎矩方程式、平衡方程式、畫圖邏輯填進 `sd_framework.py` 規定的介面。
- `notebooks/Case-XX-*.ipynb` — 每個 Case 的教學 notebook，可直接在
  Colab 開啟執行；內容是把對應的 `.py` 原始碼整段內嵌進 cell（不用
  import），所以是自包含、不依賴根目錄檔案的獨立單元 —— **這代表
  notebook 內嵌的程式碼跟根目錄的 `.py` 檔是兩份拷貝，修改時要兩邊
  一起改，否則會分岔**。
- `.github/workflows/run-notebooks.yml` — CI，每次 push 自動重跑
  `notebooks/` 底下所有 notebook，任何一個 cell 出錯就讓 CI 失敗。

## 目前進度

- ✅ Case-01：一次靜不定梁 (propped cantilever)
- ⬜ Case-02：二次靜不定連續梁
- ⬜ Case-03：無側移單跨剛架
- ✅ Case-04：側移單跨剛架（先前對話已完成，待搬入本專案重新包裝）
- ✅ Case-05：二層對稱剛架（先前對話已完成，待搬入本專案重新包裝）
* [Case-01：一次靜不定梁 (propped cantilever) ](notebooks/Case-01-propped-cantilever.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-01-propped-cantilever.ipynb)
* [Case-01：wget版本](notebooks/Case-01-propped-cantilever-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-01-propped-cantilever-wget.ipynb)
* [Case-02 二次靜不定連續梁 ](notebooks/Case-02-two-span-beam.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-02-two-span-beam.ipynb)
* [Case-02:二次靜不定連續梁-wget版本-notebook](notebooks/Case-02-two-span-beam-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-02-two-span-beam-wget.ipynb)
* [Case-03 無側移單跨剛架](notebooks/Case-03-no-sway-frame.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-03-no-sway-frame.ipynb)

