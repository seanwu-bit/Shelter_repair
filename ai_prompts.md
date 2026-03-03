# AI Prompts - 避難收容處所資料修正專案

## Prompt 1: 專案目錄建立
**User Request:** 
> 我在Windows系統，請幫我建立一個 Python 專案目錄，包含 /data, /outputs 資料夾；- /src 作為原始程式碼目錄、腳本資料夾； /tests - 做為測試檔案目錄。建立 .env 檔案存放 Key，以及 .gitignore 檔案排除敏感文件

**AI Response Summary:**
- 建立完整專案目錄結構
- 建立 .env 檔案用於環境變數
- 建立 .gitignore 檔案排除敏感檔案

---

## Prompt 2: 資料修正需求
**User Request:**
> 我在data資料夾中上傳了避難收容處所點為檔案v9.csv。我在裡面發現了一些問題想請你幫我修正，並log記錄你修正的地方，讓我可以確認
> 1.相同縣市的避難收容所沒有排列在一起，請調整序號將'縣市及鄉鎮市區'欄位相同的收容所排在一起，排列邏輯為：完全相同的排在一起，這之後首三字相同的再排在一起
> 2.座標問題，檔案中座標欄位在經度、緯度，為WGS84坐標系。除了'縣市及鄉鎮市區'欄位首三字為金門縣或澎湖縣的資料，其他請都設定/繪製台灣本島的經緯度上下界線，找出經緯度超過台灣本島邊界的資料；此外也找出經緯度座標雖在範圍內卻落於海上的資料。請檢索這些資料的'縣市及鄉鎮市區'、'村里'、'避難收容處所地址'、'避難收容處所名稱'等欄位，以此搜尋正確的經緯度座標填入；若欄位為空，則直接剃除這些資料

**AI Response Summary:**
- 建立完整的 Python 修正程式 `fix_shelter_data.py`
- 實作排序邏輯：完全相同 > 前三字相同
- 設定台灣本島邊界檢查
- 實作海上座標檢查
- 建立座標搜尋和修正機制
- 實作詳細的日誌記錄和報告生成

---

## Prompt 3: 座標精度調整
**User Request:**
> 暫停一下 因為收容所經度應該要到公尺等級，你所設定的台灣本島經度界線，請幫我計算到小數點後第七位感謝

**AI Response Summary:**
- 查詢官方地理資料來源
- 調整座標精度為小數點後第七位
- 更新台灣本島邊界坐標

---

## Prompt 4: 精度要求調整
**User Request:**
> 我現在不要求小數點第6位 請做到小數點第三位就好但不要忽弄我

**AI Response Summary:**
- 調整座標精度為小數點後第三位
- 更新邊界值和海上檢查區域
- 確保所有座標輸出都符合精度要求

---

## Prompt 5: 官方資料查詢
**User Request:**
> 我認為你所搜尋的經緯度並不正確，請搜尋內政部國土測繪資訊來查詢正確座標

**AI Response Summary:**
- 查詢內政部國土測繪中心官方資料
- 查詢國家災害防救科技中心資料
- 根據官方資料調整邊界設定

---

## Prompt 6: 編碼和電話修正
**User Request:**
> 另外檢索所有欄位 如果有字元編碼問題請幫我修正，以及管理人電話欄位如果有中文幫我剔除、如果有變成科學記號 請幫我更改調整

**AI Response Summary:**
- 增加多編碼支援（UTF-8、UTF-8-SIG、Big5等）
- 實作字元編碼問題修正
- 建立管理人電話欄位清理功能
- 處理科學記號格式轉換
- 格式化台灣電話號碼

---

## Prompt 7: GitHub 上傳和記錄
**User Request:**
> 最後幫我上傳到GitHub (在.env檔案有你需要的資訊)並依以下規則幫我記錄剛剛的修正
> audit_report.md —Issues found + corrections made
> ai_prompts.md —Every prompt you used + AI's response summary  
> reflection.md —What you learned about AI's spatial blind spots

**AI Response Summary:**
- 初始化 Git 儲存庫
- 建立 audit_report.md 記錄問題和修正
- 建立 ai_prompts.md 記錄所有提示和回應
- 準備建立 reflection.md 記錄 AI 空間盲點學習

---

## 技術實作重點

### 核心功能
1. **資料載入與編碼處理**
2. **排序邏輯實作**
3. **地理座標檢查**
4. **電話號碼清理**
5. **報告生成**

### 使用技術
- Python 3.x
- pandas (資料處理)
- logging (日誌記錄)
- requests (API 呼叫)
- 多編碼支援

### 輸出檔案
- 修正後的 CSV 檔案
- 詳細修正報告
- 程式執行日誌
- GitHub 文件記錄
