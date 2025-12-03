# ラクミー経営管理データソース調査

## 概要
ラクミー飲食店経営管理システムのデータマッピング・画面間連携調査結果

## ファイル一覧

### インプットデータ
| ファイル名 | 説明 |
|-----------|------|
| external_data_summary.txt | 外部連携データ項目サマリー（ZTOTAL, インフォマート, KOT, ジョブカン） |
| original_store_indicators_clean.txt | オリジナル店舗指標一覧 |
| v18_store_indicators.txt | v18版店舗指標一覧（233指標） |

### 最終マッピング表（v21）
| ファイル名 | 説明 |
|-----------|------|
| 会社画面マッピングリスト_v21.tsv | 会社画面マッピング定義（151指標、62列） |
| 店舗画面マッピングリスト_v21.tsv | 店舗画面マッピング定義（278指標、62列） |

### 画面間演算データ
| ファイル名 | 説明 |
|-----------|------|
| 画面間連携サマリー.tsv | 画面間連携サマリー |
| 画面別演算ロジック詳細.csv | 画面別演算ロジック詳細（Markdown版） |
| 画面内指標間演算詳細.csv | 画面内指標間演算詳細（101指標） |
| 画面内指標間演算_アウトプット先含む完全版.csv | 全指標の演算ロジック・アウトプット先（429指標） |
| 会社画面_指標間演算_インプットアウトプット.csv | 会社画面の指標間演算（インプット元・アウトプット先含む） |
| 店舗画面_指標間演算_インプットアウトプット.csv | 店舗画面の指標間演算（インプット元・アウトプット先含む） |

## 主要な演算定義

### 営業利益
```
演算式: 売上 - 仕入 - 人件費 - 経費

詳細式:
  ZTOTAL.sales_excluded 
  - trade_total.total_tax_excluded 
  - labor_costs_logs.labor_costs 
  - monthly_costs.value

使用する指標:
  ├─ 売上税抜 ─── ZTOTAL.sales_excluded
  ├─ FD仕入額 ─── trade_total.total_tax_excluded
  ├─ 人件費 ───── labor_costs_logs.labor_costs
  └─ 経費 ─────── monthly_costs.value
```

### FL率
```
演算式: (仕入 + 人件費) ÷ 売上 × 100

詳細式:
  (trade_total.total_tax_excluded + labor_costs_logs.labor_costs) 
  ÷ ZTOTAL.sales_excluded × 100
```

## データソース早見表

| テーブル名 | 物理名 | 用途 |
|-----------|--------|------|
| ZTOTAL | 日別集計 | 売上税抜、客数（日別合計） |
| TTOTAL | 伝票単位 | ランチ/ディナー分割時の売上・客数 |
| TITEM | 商品別 | 商品別売上、ABC分析 |
| trade_total | インフォマート合計 | FD仕入額 |
| tax_excluded_total | インフォマート税抜合計 | 変動費、原価 |
| labor_costs_logs | 勤怠連携 | 人件費 |
| monthly_costs | ラクミー月次費用 | 経費（家賃、水道光熱費等） |
| monthly_budgets | ラクミー予算 | 売上目標、利益目標 |
| shops | 店舗マスタ | 坪数、総卓数 |

## 作成日
2024年12月3日
