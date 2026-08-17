# slope_deflection_framework — 課程路線圖

參照 [pyfem-plastic-hinge](https://github.com/zhixiu0223/pyfem-plastic-hinge) 的組織方式：
Case 編號 notebook、每個 Case 自成一個可獨立在 Colab 跑的教學單元、
ROADMAP.md 記錄驗證進度、每個完成的 Case 都要跟 anastruct 交叉驗證過
才算「過關」。

## 框架介面 (SlopeDeflectionProblem)

`sd_framework.py` 定義的抽象介面，每個 Case 的 `model_*.py` 都要實作
（必要方法）或視需要覆寫（可選方法）：

**必要方法**：`get_unknowns`, `describe`, `draw_geometry`,
`build_moment_equations`, `build_equilibrium_equations`, `draw_bmd`

**可選方法**（有預設行為，不實作也不會出錯，求解器會優雅跳過）：
- `compute_reactions` — 步驟5 印支承反力，預設不計算
- `draw_sfd` — 步驟6 剪力圖，預設不畫，印提示跳過
- `teaching_breakdown` — **步驟8 教學詳解+評分要點**（Case-01 起新增）：
  回傳 list[dict]，每個 dict 是一個小題，包含
  `title/problem/concept/formula/substitution/answer/keywords/grading`，
  求解器會自動逐題印出「題目→概念解析→公式引用→帶入數據→參考答案→
  關鍵字→評分要點」，並加總配分。預設回傳空列表，不提供時印出
  「此模型尚未提供教學詳解，略過」而不報錯。

新增可選方法時務必記得：**model 的 class 一定要真的繼承
`SlopeDeflectionProblem`**（之前 Case-01/02 一度忘記繼承，只是靠鴨子
定型硬撐，新增 `teaching_breakdown` 時才炸出來——沒有繼承就拿不到
基底類別的預設實作）。

## 設計原則

1. **從最小的獨立位移自由度(Dk)開始**，每個 Case 只增加「一件新事情」
   （多一個未知數、多一種邊界條件、多一次側移、多一層樓...），
   絕不一次跳兩件事——這樣如果某個 Case 算錯，問題一定出在
   這次新加的那件事上，好抓。
2. **每個 Case 必做三件事**：
   - 用傾角變位法（我們的 Template Method + Strategy 框架）手算過程全部展開
   - 用 anastruct 建立完全獨立的 FEM 模型
   - **剪力交叉檢查**（不只比彎矩數值，也比剪力——這是這次抓到梁
     BC bug 的關页，剪力對不上通常代表畫圈/正負號有問題，比只比較
     彎矩數值更容易抓到「數值對、畫法錯」這種陷阱）
3. 每個 Case 完成後才進到下一個，不跳著做。
4. **教學詳解(`teaching_breakdown`)是可選的加分項**，不是每個 Case 的
   硬性要求——Case-01 已經示範過格式，之後哪個 Case 想額外補教學/
   評分內容，照 Case-01 的資料結構補上 `teaching_breakdown` 方法即可，
   沒補的 Case 不影響其他步驟正常運作。

## Validation Log

**表格說明**：`Ds`(靜不定度) 是贅力法的天然複雜度量，`Dk`(獨立位移自由度)
是傾角變位法的天然複雜度量——兩者是不同的東西，不要混用。目前這個 repo
只做傾角變位法，Case 的難度排序以 `Dk` 為主軸；`Ds` 先記錄下來備查，
等之後真的做贅力法比較時會用到。**沒有真正設計、驗證過的 Case，`Ds`欄
一律留白，不要用猜的填數字**——猜錯的數字比不填更誤導人。

| Case | 結構類型 | Ds (靜不定度) | Dk (獨立位移自由度，本課程主軸) | 新增的概念 | 狀態 |
|---|---|---|---|---|---|
| 01 | 一次靜不定梁 (propped cantilever, 固定+滾支承) | 1 | 1 (θ_B) | 邊界條件 M=0 取代節點平衡 | ✅ 完成，anastruct+剪力驗證通過 |
| 02 | 二次靜不定連續梁 (兩跨連續梁，三個支承) | 2 | 2 (θ_B, θ_C) | 中間支承的節點平衡；連續支承(共用θ)跟鉸接(各自獨立θ)的差別是這題最容易搞錯自由度的地方 | ✅ 完成，anastruct+剪力驗證通過 (四個端點全核對) |
| 03 | 無側移單跨剛架 (門型剛架，僅承受樑上均佈載重，柱不側移) | — (待設計時計算，不用猜) | 2 (θ_B, θ_C) | 樑柱剛架的節點平衡（柱剛度加入方程）、無側移(ψ=0) | ⬜ 待做 |
| 04 | 側移單跨剛架 (水平載重 P，即目前的「模型①」) | — | 3 (θ_B, θ_C, Δ) | 側移角 Δ、剪力平衡方程式 | ✅ 已完成 (先前對話中已充分驗證) |
| 05 | 二層對稱剛架 (即目前的「模型②」) | — | 4，對稱化簡為2 (θ_1F, θ_RF) | 多層節點平衡、對稱-反對稱化簡技巧——**這是 Ds 和 Dk 不是同一件事的鐵證**：結構本身的靜不定度不會因為發現對稱性而改變，但 Dk 會從4降到2 | ✅ 已完成 (先前對話中已充分驗證) |
| 06 | 二層剛架 + 側移 (不對稱載重或有水平力) | — | 4 (拿掉對稱化簡，回到完整4個獨立轉角/側移) | 拿掉對稱化簡，回到完整4個未知數 | ⬜ 待做 |
| 07 | 二跨不等跨剛架 | — | — | 不同跨度/剛度的樑柱組合 | ⬜ 待做 |

## Special Cases（特殊/進階案例，獨立編號，不排進 01~07 的階梯）

**這個區塊放什麼**：幾何跟現有 Case 完全不同、不是「Dk 遞增一個」能涵蓋的
題型——例如斜屋頂剛架、非正交桿件、考古題裡奇怪的混合支承組合。這些不是
教學階梯的下一步，是**測試框架本身泛用性**的題目，所以獨立編號
(`S-01`, `S-02`...)，不用擠進 01~07 的順序，加或不加都不影響主線進度。

**跟主線的關鍵差異**：01~07 都建立在同一個隱藏假設上——柱垂直、梁水平
剛性，所以側移角是單一純量 `ψ=Δ/H`（見 Case-04）。斜桿件的側移角要把
節點的 x,y 兩個位移分量投影到桿件自己的垂直方向，`sd_framework.py`
目前的一般式（`member_moment_curve` 那套 API）沒有處理這件事——這不是
寫一個新 `model_*.py` 就能解決的，是框架本身要先擴充。這也是之前討論
「通用宣告式輸入介面」被暫緩的那個方向會真正派上用場的地方。

| 編號 | 結構類型 | 需要框架先具備的能力 | 狀態 |
|---|---|---|---|
| S-01 | 斜屋頂剛架 (Gable/Pitched-roof Frame) | 斜桿件側移角(ψ)的一般化計算——節點位移拆 x,y 分量、投影到桿件局部垂直方向 | ⬜ 佔位，尚未開始，等framework補上斜桿件支援才能做 |

## 未來方向（先記錄，不現在做）

- **贅力法(Force Method)比較**：等 Case 03~07 的傾角變位法都做得差不多、
  介面穩定下來，才考慮在同一個 repo 開第二條支線做贅力法，拿同一個結構
  比較兩種方法的複雜度（Ds vs Dk 何者較小、何者好算）。現在不開新專案，
  也不預先加 `get_static_indeterminacy()` 這類方法——沒有贅力法要用，
  加了也是空殼。
- **參數變化範例**：不開新的 `samples/` 資料夾（這個名字已經被用來放
  model 實作 `.py` 檔了，避免混用）。同一個 Case 想跑不同參數組合，
  直接在該 Case 的 notebook 裡多加 cell（Case-04的側移剛架已經示範過
  這個模式：H=4,L=6,P=12 一組、H=5,L=8,P=20 另一組）。真的累積到需要
  正式收納 3~5 組變化時，再考慮開子資料夾，不用現在先立規矩。



## 專案結構

```
slope_deflection_framework/
├── README.md
├── ROADMAP.md               <- 這個檔案
├── sd_framework.py          <- Template Method 骨架 (共用，不因Case而變)
├── samples/
│   ├── model_propped_cantilever.py
│   ├── model_two_span_beam.py
│   └── ...                  <- 之後新Case的 model_*.py 也放這裡
└── notebooks/
    ├── Case-01-propped-cantilever.ipynb
    ├── Case-01-propped-cantilever-wget.ipynb
    ├── Case-02-two-span-beam.ipynb
    ├── Case-03-no-sway-frame.ipynb        (待做)
    ├── Case-04-sway-frame.ipynb           (待做，先前對話已完成待搬入)
    ├── Case-05-two-story-frame.ipynb      (待做，先前對話已完成待搬入)
    └── ...
```
