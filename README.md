# slope_deflection_framework
[![Execute notebook & verify results](https://github.com/zhixiu0223/slope_deflection_framework/actions/workflows/run-notebooks.yml/badge.svg)](https://github.com/zhixiu0223/slope_deflection_framework/actions/workflows/run-notebooks.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

傾角變位法教學專案，架構參照 [pyfem-plastic-hinge](https://github.com/zhixiu0223/pyfem-plastic-hinge)：
Case 編號 notebook，每個 Case 都自成一個可獨立在 Colab 執行的教學單元，
用傾角變位法手算 + anastruct(必要時加 OpenSeesPy) 獨立 FEM 建模 + 剪力
交叉檢查 三方比對。

見 `ROADMAP.md` 了解目前進度、課程規劃、以及一路踩過的坑跟教訓。

## FEM 慣例

**近端負、遠端正**（傳統教科書慣例），傾角變位法本身順時針為正。
四個 Case 已統一，畫圖（拉力側彎矩圖、剪力圖、變形圖）一律用「近端取
負號、遠端直接用」這條規則，細節見 `ROADMAP.md`。

## 檔案說明

- `sd_framework.py` — 共用引擎 (Template Method)：`SlopeDeflectionProblem`
  規格介面 + `SlopeDeflectionSolver`。兩種輸出方式：
  - `solve_and_report()` — 完整步驟1~7，展開所有中間過程(公式引用、
    平衡方程式、解方程式)
  - `print_teaching_handout()` — 只有五張圖(結構受力圖／剪力圖／彎矩
    圖／拉力側標註圖／變形圖)，沒有中間符號方程式，適合直接複製當
    教學講義用
  - 會自動偵測執行環境(`IN_NOTEBOOK`)：Jupyter/Colab 正常渲染；純
    終端機(`python3 xxx.py`)文字改用`print()`、圖片自動存檔
- `samples/model_*.py` — 每個 Case 專屬的 Strategy 實作，把特定結構的
  幾何、彎矩方程式、平衡方程式、畫圖邏輯填進 `sd_framework.py` 規定的
  介面。
- `scripts/run_case0X.py` — 獨立驅動腳本，wget 抓 `sd_framework.py` +
  對應的 `model_*.py` + 這個檔案後，`python3 run_case0X.py` 就能跑，
  不需要 Jupyter/Colab。支援 `--interactive` 互動輸入或
  `--參數名 數值` 直接指定，細節見各腳本開頭的說明。
- `notebooks/Case-XX-*.ipynb` — 內嵌版，程式碼整段貼在 cell 裡，完全
  自包含、不連網路。**跟 `.py` 檔是兩份拷貝，修改時要兩邊一起改，
  否則會分岔。**
- `notebooks/Case-XX-*-wget.ipynb` — wget 版，用 `!wget` 即時抓
  `sd_framework.py`/`model_*.py`，不會分岔，push 完 `.py` 後這份
  notebook 重新執行就自動跟上最新版——**適合分享給別人用**。
- `.github/workflows/run-notebooks.yml` — CI，每次 push 自動重跑
  `notebooks/` 底下所有 notebook，任何一個 cell 出錯就讓 CI 失敗。

## 三種使用方式

1. **Colab（最簡單）**：點下面對應 Case 的「Open In Colab」徽章，
   逐格執行。
2. **本地 / 手機終端機（Termux、Pydroid 等）**：
   ```bash
   wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/sd_framework.py
   wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/samples/model_no_sway_frame.py
   wget -q https://raw.githubusercontent.com/zhixiu0223/slope_deflection_framework/main/scripts/run_case03.py
   python3 run_case03.py --interactive
   ```
3. **改參數重跑**：不管哪個 Case，`model_*.py` 的建構子都能直接改
   幾何/載重/`EI_numeric` 參數，例如
   `NoSwayFrameProblem(H=5.0, L=8.0, w=30.0, EI_numeric=20000.0)`。

⚠️ **已知限制**：用「Open in Colab」徽章連結開啟時，sympy 的數學式
(步驟2的桿端彎矩式、步驟4的位移解) 一開始會是空的，**每次**都要重新
執行那個 cell 才會顯示——這是 Colab 透過 GitHub 連結載入 notebook 時
的限制，不是程式問題。如果只是想看已經算好的結果(不用互動)，直接在
GitHub 網頁上開 `.ipynb` 檔案反而看得到存檔的完整輸出。細節見
`ROADMAP.md`。

## 目前進度

- ✅ Case-01：一次靜不定梁 (propped cantilever)
- ✅ Case-02：二次靜不定連續梁
- ✅ Case-03：無側移單跨剛架
- ✅ Case-04：側移單跨剛架
- ⬜ Case-05：二層對稱剛架（先前對話已完成，待搬入本專案套用目前框架）
- ⬜ Case-06：二層剛架+側移
- ⬜ Case-07：二跨不等跨剛架

## Notebook 連結

* [Case-01：一次靜不定梁 (propped cantilever)](notebooks/Case-01-propped-cantilever.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-01-propped-cantilever.ipynb)
* [Case-01：wget版本](notebooks/Case-01-propped-cantilever-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-01-propped-cantilever-wget.ipynb)
* [Case-02：二次靜不定連續梁](notebooks/Case-02-two-span-beam.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-02-two-span-beam.ipynb)
* [Case-02：wget版本](notebooks/Case-02-two-span-beam-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-02-two-span-beam-wget.ipynb)
* [Case-03：無側移單跨剛架](notebooks/Case-03-no-sway-frame.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-03-no-sway-frame.ipynb)
* [Case-03：wget版本](notebooks/Case-03-no-sway-frame-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-03-no-sway-frame-wget.ipynb)
* [Case-04：側移單跨剛架](notebooks/Case-04-sway-frame.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-04-sway-frame.ipynb)
* [Case-04：wget版本](notebooks/Case-04-sway-frame-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-04-sway-frame-wget.ipynb)
* [Case-04.5：側移單垮鋼架-加梁重](notebooks/Case-04.5-sway-frame-with-udl.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-04.5-sway-frame-with-udl.ipynb)
* [Case-04.5：wget版本 側移單垮鋼架-加梁重](notebooks/Case-04.5-sway-frame-with-udl-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-04.5-sway-frame-with-udl-wget.ipynb)
* [Case-05：二層對稱剛架](notebooks/Case-05-two-story-frame.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-05-two-story-frame.ipynb)
* [Case-05：wget版本-二層對稱剛架](notebooks/Case-05-two-story-frame-wget.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zhixiu0223/slope_deflection_framework/blob/main/notebooks/Case-05-two-story-frame-wget.ipynb)
