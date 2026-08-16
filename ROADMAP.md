# slope_deflection_framework — 課程路線圖

參照 [pyfem-plastic-hinge](https://github.com/zhixiu0223/pyfem-plastic-hinge) 的組織方式：
Case 編號 notebook、每個 Case 自成一個可獨立在 Colab 跑的教學單元、
ROADMAP.md 記錄驗證進度、每個完成的 Case 都要跟 anastruct 交叉驗證過
才算「過關」。

## 設計原則

1. **從最小的靜不定結構開始**，每個 Case 只增加「一件新事情」
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

## Validation Log

| Case | 結構類型 | 靜不定度 | 新增的概念 | 狀態 |
|---|---|---|---|---|
| 01 | 一次靜不定梁 (propped cantilever, 固定+滾支承) | 1 | 最基本的1個未知數 θ_B，邊界條件 M=0 取代節點平衡 | ✅ 完成，anastruct+剪力驗證通過 |
| 02 | 二次靜不定連續梁 (兩跨連續梁，三個支承) | 2 | 兩個未知數 θ_B, θ_C，中間支承的節點平衡 | ⬜ 待做 |
| 03 | 無側移單跨剛架 (門型剛架，僅承受樑上均佈載重，柱不側移) | 2 | 樑柱剛架的節點平衡（柱剛度加入方程）、無側移(ψ=0) | ⬜ 待做 |
| 04 | 側移單跨剛架 (水平載重 P，即目前的「模型①」) | 3 | 側移角 Δ、剪力平衡方程式 | ✅ 已完成 (先前對話中已充分驗證) |
| 05 | 二層對稱剛架 (即目前的「模型②」) | 4→對稱化簡為2 | 多層節點平衡、對稱-反對稱化簡技巧 | ✅ 已完成 (先前對話中已充分驗證) |
| 06 | 二層剛架 + 側移 (不對稱載重或有水平力) | — | 拿掉對稱化簡，回到完整4個未知數 | ⬜ 待做 |
| 07 | 二跨不等跨剛架 | — | 不同跨度/剛度的樑柱組合 | ⬜ 待做 |

## 專案結構

```
slope_deflection_framework/
├── docs/
│   └── ROADMAP.md          <- 這個檔案
├── src/
│   └── sd_framework.py     <- Template Method 骨架 (共用，不因Case而變)
└── cases/
    ├── Case-01-propped-cantilever.ipynb
    ├── Case-02-two-span-beam.ipynb        (待做)
    ├── Case-03-no-sway-frame.ipynb        (待做)
    ├── Case-04-sway-frame.ipynb           (已有，等待搬進來重新包裝)
    ├── Case-05-two-story-frame.ipynb      (已有，等待搬進來重新包裝)
    └── ...
```
