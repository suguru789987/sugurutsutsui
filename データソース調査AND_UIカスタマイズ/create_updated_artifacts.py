# -*- coding: utf-8 -*-
"""
V41ベースで以下を更新:
1. 会社画面データリネージュ図
2. 店舗画面データリネージュ図
3. UIカスタマイズ仕様書（既存合成、ディメンション、新指標）
"""

import csv
from datetime import datetime
from collections import defaultdict

def read_v41(file_path):
    """V41ファイルを読み込む"""
    rows = []
    header = None

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == 'No':
                header = row
            elif header and row and row[0].isdigit():
                rows.append(dict(zip(header, row)))

    return rows, header


def create_data_lineage_html(rows, screen_type, output_file):
    """データリネージュ図HTMLを生成"""

    # 外部連携グループ別に集計
    external_groups = defaultdict(list)
    for row in rows:
        group = row.get('外部連携グループ名', '')
        if group and group != '-':
            for g in group.split(', '):
                if g.strip():
                    external_groups[g.strip()].append(row)

    # 画面タイトル別に集計
    screens = defaultdict(list)
    for row in rows:
        screen_title = row.get('画面タイトル', '')
        screens[screen_title].append(row)

    # 経営重要度別に集計
    importance_counts = defaultdict(int)
    for row in rows:
        imp = row.get('経営重要度', 'C')
        importance_counts[imp] += 1

    # 画面タイプ別に集計
    display_screens = set()
    input_screens = set()
    for row in rows:
        screen_type_row = row.get('画面タイプ', '')
        screen_title = row.get('画面タイトル', '')
        if screen_type_row == '表示画面':
            display_screens.add(screen_title)
        else:
            input_screens.add(screen_title)

    if screen_type == '会社':
        viewpoint = '本部・オーナー視点'
        importance_desc = {
            'S': '最重要（経営判断直結）',
            'A': '重要（業績管理必須）',
            'B': '標準（管理対象）',
            'C': '参考（分析用）',
            'D': '補助（マスタ/設定）'
        }
    else:
        viewpoint = '店長視点'
        importance_desc = {
            'S': '最重要（日次確認必須）',
            'A': '重要（週次確認推奨）',
            'B': '標準（月次確認）',
            'C': '参考（必要時確認）',
            'D': '補助（設定/入力）'
        }

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{screen_type}画面 データリネージュ図 V41</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4a90d9;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #4a90d9;
            padding-left: 10px;
        }}
        h3 {{
            color: #666;
            margin-top: 20px;
        }}
        .summary {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card.s {{ background: linear-gradient(135deg, #E53935 0%, #C62828 100%); }}
        .summary-card.a {{ background: linear-gradient(135deg, #FB8C00 0%, #EF6C00 100%); }}
        .summary-card.b {{ background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); }}
        .summary-card.c {{ background: linear-gradient(135deg, #757575 0%, #616161 100%); }}
        .summary-card.d {{ background: linear-gradient(135deg, #BDBDBD 0%, #9E9E9E 100%); }}
        .summary-card h4 {{
            margin: 0 0 10px 0;
            font-size: 14px;
        }}
        .summary-card .number {{
            font-size: 32px;
            font-weight: bold;
        }}
        .mermaid {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
            margin-bottom: 20px;
        }}
        .legend {{
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 15px;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 13px;
        }}
        .external {{ background-color: #e3f2fd; border: 2px solid #2196f3; }}
        .internal {{ background-color: #e8f5e9; border: 2px solid #4caf50; }}
        .screen {{ background-color: #fff3e0; border: 2px solid #ff9800; }}
        .input {{ background-color: #fce4ec; border: 2px solid #e91e63; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 15px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            font-size: 13px;
        }}
        th {{
            background-color: #4a90d9;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .importance-s {{ color: #E53935; font-weight: bold; }}
        .importance-a {{ color: #FB8C00; font-weight: bold; }}
        .importance-b {{ color: #1E88E5; }}
        .importance-c {{ color: #757575; }}
        .importance-d {{ color: #BDBDBD; }}
        .section {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .screen-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .screen-tag {{
            background-color: #fff3e0;
            border: 1px solid #ff9800;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .screen-tag.input {{
            background-color: #fce4ec;
            border-color: #e91e63;
        }}
    </style>
</head>
<body>
    <h1>{screen_type}画面 データリネージュ図 V41</h1>
    <p>作成日: {datetime.now().strftime("%Y年%m月%d日")} | 経営重要度: {viewpoint} | 総指標数: {len(rows)}指標</p>

    <div class="summary">
        <h3>経営重要度サマリー</h3>
        <div class="summary-grid">
            <div class="summary-card s">
                <h4>S: {importance_desc['S']}</h4>
                <div class="number">{importance_counts['S']}</div>
            </div>
            <div class="summary-card a">
                <h4>A: {importance_desc['A']}</h4>
                <div class="number">{importance_counts['A']}</div>
            </div>
            <div class="summary-card b">
                <h4>B: {importance_desc['B']}</h4>
                <div class="number">{importance_counts['B']}</div>
            </div>
            <div class="summary-card c">
                <h4>C: {importance_desc['C']}</h4>
                <div class="number">{importance_counts['C']}</div>
            </div>
            <div class="summary-card d">
                <h4>D: {importance_desc['D']}</h4>
                <div class="number">{importance_counts['D']}</div>
            </div>
        </div>
    </div>

    <div class="legend">
        <strong>凡例:</strong>
        <span class="legend-item external">外部データソース (POS/インフォマート/KOT)</span>
        <span class="legend-item internal">内部データソース (マスタ/設定)</span>
        <span class="legend-item screen">表示画面</span>
        <span class="legend-item input">設定入力画面</span>
    </div>

    <h2>1. 全体概要図</h2>
    <div class="mermaid">
flowchart LR
    subgraph EXT[外部データソース]
        direction TB
        ZTOTAL[(ZTOTAL<br/>POS売上日次)]
        TITEM[(TITEM<br/>POS商品別)]
        TTEND[(TTEND<br/>POS支払別)]
        INFOMART[(インフォマート<br/>仕入データ)]
        LABOR[(KOT/ジョブカン<br/>人件費)]
    end

    subgraph INT[内部データソース]
        direction TB
        BUDGETS[(monthly_budgets<br/>予算マスタ)]
        COSTS[(monthly_costs<br/>費用マスタ)]
        SHOPS[(shops<br/>店舗マスタ)]
        INVENTORY[(shop_inventories<br/>棚卸マスタ)]
    end

    subgraph DISPLAY[表示画面]
        direction TB
        KPI[主要KPI指標<br/>営業利益率/FL率/坪月商]
        MONTHLY[当月実績<br/>売上/仕入率/人件費率]
        SHOP_SUMMARY[店舗別サマリー<br/>営業利益/達成率]
        ANALYSIS[各種分析画面<br/>ABC/時間帯/曜日別]
    end

    subgraph INPUT[設定入力画面]
        direction TB
        BUDGET_INPUT[予算設定]
        COST_INPUT[月次費用入力]
        MASTER_INPUT[費目マスタ]
    end

    ZTOTAL --> MONTHLY
    ZTOTAL --> SHOP_SUMMARY
    TITEM --> ANALYSIS
    TTEND --> ANALYSIS
    INFOMART --> MONTHLY
    LABOR --> MONTHLY

    BUDGETS --> KPI
    COSTS --> KPI
    SHOPS --> KPI

    MONTHLY --> KPI
    SHOP_SUMMARY --> KPI

    BUDGET_INPUT --> BUDGETS
    COST_INPUT --> COSTS
    </div>

    <h2>2. 画面一覧</h2>
    <div class="section">
        <h3>表示画面 ({len(display_screens)}画面)</h3>
        <div class="screen-list">
'''

    for screen in sorted(display_screens):
        html += f'            <span class="screen-tag">{screen}</span>\n'

    html += '''        </div>
        <h3>設定入力画面 (''' + str(len(input_screens)) + '''画面)</h3>
        <div class="screen-list">
'''

    for screen in sorted(input_screens):
        html += f'            <span class="screen-tag input">{screen}</span>\n'

    html += '''        </div>
    </div>

    <h2>3. 外部連携グループ別データフロー</h2>
'''

    # 外部連携グループ別のセクション
    group_names = {
        'POS売上（日別集計）': ('ZTOTAL', 'head_office_connected_service_sales_logs'),
        'POS売上（商品別）': ('TITEM', 'head_office_item_sales_logs'),
        'POS売上（支払別）': ('TTEND', 'head_office_payment_method_sales_logs'),
        'インフォマート（仕入）': ('インフォマート', 'infomart_transactions'),
        '勤怠（KOT/ジョブカン）': ('KOT/ジョブカン', 'head_office_connected_service_labor_costs_logs'),
        'ユーザー入力（予算設定）': ('予算設定', 'monthly_budgets'),
        'ユーザー入力（費用設定）': ('費用設定', 'monthly_costs'),
    }

    for group_name, (short_name, table_name) in group_names.items():
        if group_name in external_groups:
            indicators = external_groups[group_name]
            html += f'''
    <div class="section">
        <h3>{group_name}</h3>
        <p>外部テーブル: {short_name} → ラクミーテーブル: {table_name}</p>
        <table>
            <tr>
                <th>No</th>
                <th>画面タイトル</th>
                <th>指標名</th>
                <th>経営重要度</th>
                <th>独自度</th>
                <th>演算ロジック</th>
            </tr>
'''
            for idx, row in enumerate(indicators[:20], 1):  # 最大20件表示
                imp = row.get('経営重要度', 'C')
                imp_class = f'importance-{imp.lower()}'
                html += f'''            <tr>
                <td>{idx}</td>
                <td>{row.get('画面タイトル', '')}</td>
                <td>{row.get('指標名', '')}</td>
                <td class="{imp_class}">{imp}</td>
                <td>{row.get('独自指標レベル', '')}</td>
                <td>{row.get('演算ロジック', '')}</td>
            </tr>
'''
            if len(indicators) > 20:
                html += f'            <tr><td colspan="6">... 他 {len(indicators) - 20} 件</td></tr>\n'
            html += '''        </table>
    </div>
'''

    html += '''
    <h2>4. 経営重要度別 指標一覧</h2>
'''

    for rank in ['S', 'A', 'B', 'C', 'D']:
        rank_rows = [r for r in rows if r.get('経営重要度', '') == rank]
        if rank_rows:
            imp_class = f'importance-{rank.lower()}'
            html += f'''
    <div class="section">
        <h3 class="{imp_class}">{rank}: {importance_desc[rank]} ({len(rank_rows)}指標)</h3>
        <table>
            <tr>
                <th>No</th>
                <th>画面タイトル</th>
                <th>指標名</th>
                <th>データソース区分</th>
                <th>独自度</th>
                <th>インプット元</th>
            </tr>
'''
            for idx, row in enumerate(rank_rows[:30], 1):  # 最大30件表示
                html += f'''            <tr>
                <td>{idx}</td>
                <td>{row.get('画面タイトル', '')}</td>
                <td>{row.get('指標名', '')}</td>
                <td>{row.get('データソース区分', '')}</td>
                <td>{row.get('独自指標レベル', '')}</td>
                <td>{row.get('インプット元（画面名.指標名）', '')[:50]}</td>
            </tr>
'''
            if len(rank_rows) > 30:
                html += f'            <tr><td colspan="6">... 他 {len(rank_rows) - 30} 件</td></tr>\n'
            html += '''        </table>
    </div>
'''

    html += '''
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
    </script>
</body>
</html>
'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return len(rows), importance_counts


def create_ui_customization_csv(company_rows, shop_rows, output_file):
    """UIカスタマイズ仕様書を生成"""

    all_rows = company_rows + shop_rows

    # カスタマイズ分類
    def classify_customization(row):
        imp = row.get('経営重要度', 'C')
        data_source = row.get('データソース区分', '')
        screen_type = row.get('画面タイプ', '')

        if screen_type == '設定入力画面':
            return '設定のみ'
        elif imp == 'S':
            return '固定表示'
        elif imp == 'A':
            return '固定表示'
        elif imp == 'B':
            return 'カスタマイズ可'
        elif imp == 'C':
            return '表示切替可'
        else:
            return '設定のみ'

    # 指標タイプ分類（既存合成、ディメンション、新指標）
    def classify_indicator_type(row):
        indicator_type = row.get('指標タイプ', '')
        indicator_detail = row.get('指標タイプ詳細', '')
        calc_range = row.get('演算範囲', '')

        if '外部連携単独' in indicator_type or '単独' in indicator_detail:
            return 'ベース指標'
        elif 'マスタ' in indicator_type or 'マスタ' in indicator_detail:
            return 'ディメンション'
        elif calc_range == '画面間':
            return '既存合成（画面間）'
        elif calc_range == '画面内':
            return '既存合成（画面内）'
        elif '演算' in indicator_type or '計算' in row.get('データソース区分', ''):
            return '演算指標'
        else:
            return 'その他'

    # ディメンション数を判定
    def count_dimensions(row):
        input_source = row.get('インプット元（画面名.指標名）', '')
        if not input_source or input_source == '-':
            return 0
        sources = [s.strip() for s in input_source.split(',') if s.strip()]
        return len(sources)

    # 集計
    customization_counts = {'会社': defaultdict(int), '店舗': defaultdict(int)}
    indicator_type_counts = {'会社': defaultdict(int), '店舗': defaultdict(int)}
    dimension_counts = {'会社': defaultdict(int), '店舗': defaultdict(int)}

    for row in company_rows:
        cust = classify_customization(row)
        itype = classify_indicator_type(row)
        dims = count_dimensions(row)
        customization_counts['会社'][cust] += 1
        indicator_type_counts['会社'][itype] += 1
        if dims >= 3:
            dimension_counts['会社']['3個以上'] += 1
        elif dims >= 1:
            dimension_counts['会社'][f'{dims}個'] += 1
        else:
            dimension_counts['会社']['なし'] += 1

    for row in shop_rows:
        cust = classify_customization(row)
        itype = classify_indicator_type(row)
        dims = count_dimensions(row)
        customization_counts['店舗'][cust] += 1
        indicator_type_counts['店舗'][itype] += 1
        if dims >= 3:
            dimension_counts['店舗']['3個以上'] += 1
        elif dims >= 1:
            dimension_counts['店舗'][f'{dims}個'] += 1
        else:
            dimension_counts['店舗']['なし'] += 1

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['UIカスタマイズ仕様書 V41'])
        writer.writerow([f'作成日: {datetime.now().strftime("%Y年%m月%d日")}'])
        writer.writerow([])

        # カスタマイズ可否別
        writer.writerow(['■ カスタマイズ可否別 分布'])
        writer.writerow([])
        writer.writerow(['カスタマイズ可否', '会社画面', '店舗画面', '合計', '説明'])
        cust_types = ['固定表示', '表示切替可', 'カスタマイズ可', '設定のみ']
        for cust in cust_types:
            company = customization_counts['会社'][cust]
            shop = customization_counts['店舗'][cust]
            desc = {
                '固定表示': '経営判断に必須のため常時表示（S/A重要度）',
                '表示切替可': 'ON/OFF切替可能（C重要度）',
                'カスタマイズ可': '表示順序変更・お気に入り登録可能（B重要度）',
                '設定のみ': '設定画面でのみ表示（D重要度・設定入力画面）'
            }
            writer.writerow([cust, f'{company}件', f'{shop}件', f'{company + shop}件', desc.get(cust, '')])
        writer.writerow([])

        # 指標タイプ別
        writer.writerow(['■ 指標タイプ別 分布'])
        writer.writerow([])
        writer.writerow(['指標タイプ', '会社画面', '店舗画面', '合計', '説明'])
        itypes = ['ベース指標', 'ディメンション', '既存合成（画面内）', '既存合成（画面間）', '演算指標', 'その他']
        for itype in itypes:
            company = indicator_type_counts['会社'][itype]
            shop = indicator_type_counts['店舗'][itype]
            desc = {
                'ベース指標': '外部連携から直接取得（売上税抜、客数等）',
                'ディメンション': 'マスタ/軸データ（店舗名、商品名、曜日等）',
                '既存合成（画面内）': '同一画面内の指標を演算（構成比率等）',
                '既存合成（画面間）': '異なる画面の指標を演算（営業利益率等）',
                '演算指標': '複数データソースの演算（FL率等）',
                'その他': '上記に分類されない指標'
            }
            writer.writerow([itype, f'{company}件', f'{shop}件', f'{company + shop}件', desc.get(itype, '')])
        writer.writerow([])

        # ディメンション数別
        writer.writerow(['■ インプット元数別 分布（ディメンション数）'])
        writer.writerow([])
        writer.writerow(['インプット元数', '会社画面', '店舗画面', '合計', '複雑度'])
        dim_types = ['なし', '1個', '2個', '3個以上']
        for dim in dim_types:
            company = dimension_counts['会社'][dim]
            shop = dimension_counts['店舗'][dim]
            complexity = {
                'なし': '単純（外部連携直接）',
                '1個': '低（単一参照）',
                '2個': '中（2要素演算）',
                '3個以上': '高（複合演算）'
            }
            writer.writerow([dim, f'{company}件', f'{shop}件', f'{company + shop}件', complexity.get(dim, '')])
        writer.writerow([])

        # 新指標候補（独自度L4b）
        writer.writerow(['■ 新指標候補（独自度L4b: ラクミー独自の最高独自度）'])
        writer.writerow([])
        writer.writerow(['画面区分', '画面タイトル', '指標名', '経営重要度', '演算ロジック'])

        l4b_rows = [r for r in all_rows if r.get('独自指標レベル', '') == 'L4b']
        for row in l4b_rows[:30]:
            screen = '会社' if row in company_rows else '店舗'
            writer.writerow([
                screen,
                row.get('画面タイトル', ''),
                row.get('指標名', ''),
                row.get('経営重要度', ''),
                row.get('演算ロジック', '')
            ])
        if len(l4b_rows) > 30:
            writer.writerow([f'... 他 {len(l4b_rows) - 30} 件'])
        writer.writerow([])

        # UI実装ガイド
        writer.writerow(['■ カスタマイズ可否別 UI実装ガイド'])
        writer.writerow([])
        writer.writerow(['カスタマイズ可否', '対象指標例', '表示設定', 'デフォルト', 'UI表現', '実装詳細'])
        writer.writerow(['固定表示', '営業利益率・FL率・売上税抜・客数', 'ユーザーが非表示にできない', '常時ON', '設定画面でグレーアウト', '経営判断に必須のため常時表示'])
        writer.writerow(['表示切替可', '商品別売上・支払種別・時間帯別', 'ON/OFF切替可能', '表示ON', 'トグルスイッチ', '詳細データの表示/非表示を切替'])
        writer.writerow(['カスタマイズ可', '坪月商・達成率・ROI・進捗率', 'ON/OFF + 表示順序変更', '表示ON（推奨）', 'ドラッグ&ドロップで並び替え', 'お気に入り登録・ダッシュボード追加可能'])
        writer.writerow(['設定のみ', '店舗マスタ・費目・予算設定', '分析画面には非表示', '設定画面のみ', '設定画面でのみ表示', '分析ダッシュボードには表示しない'])
        writer.writerow([])

        # 経営重要度別 色分け（会社・店舗で定義が異なる）
        writer.writerow(['■ 経営重要度別 色分け（視点別定義）'])
        writer.writerow([])
        writer.writerow(['経営重要度', '会社画面（本部・オーナー視点）', '店舗画面（店長視点）', '推奨カラー'])
        writer.writerow(['S', '最重要（経営判断直結）', '最重要（日次確認必須）', '#E53935 (赤)'])
        writer.writerow(['A', '重要（業績管理必須）', '重要（週次確認推奨）', '#FB8C00 (オレンジ)'])
        writer.writerow(['B', '標準（管理対象）', '標準（月次確認）', '#1E88E5 (青)'])
        writer.writerow(['C', '参考（分析用）', '参考（必要時確認）', '#757575 (グレー)'])
        writer.writerow(['D', '補助（マスタ/設定）', '補助（設定/入力）', '#BDBDBD (薄グレー)'])

    return len(all_rows)


def main():
    print("=" * 60)
    print("V41ベース 成果物更新")
    print("=" * 60)

    # V41読み込み
    print("\n【1】V41データ読み込み...")
    company_rows, _ = read_v41('/Users/sugurutsutsui/Downloads/会社画面_データソース定義表_V41.csv')
    shop_rows, _ = read_v41('/Users/sugurutsutsui/Downloads/店舗画面_データソース定義表_V41.csv')
    print(f"  会社画面: {len(company_rows)}指標")
    print(f"  店舗画面: {len(shop_rows)}指標")

    # 会社画面データリネージュ
    print("\n【2】会社画面データリネージュ図作成...")
    company_total, company_imp = create_data_lineage_html(
        company_rows, '会社',
        '/Users/sugurutsutsui/Downloads/会社画面_データリネージュ図_V41.html'
    )
    print(f"  総指標数: {company_total}")
    print(f"  経営重要度: S={company_imp['S']}, A={company_imp['A']}, B={company_imp['B']}, C={company_imp['C']}, D={company_imp['D']}")

    # 店舗画面データリネージュ
    print("\n【3】店舗画面データリネージュ図作成...")
    shop_total, shop_imp = create_data_lineage_html(
        shop_rows, '店舗',
        '/Users/sugurutsutsui/Downloads/店舗画面_データリネージュ図_V41.html'
    )
    print(f"  総指標数: {shop_total}")
    print(f"  経営重要度: S={shop_imp['S']}, A={shop_imp['A']}, B={shop_imp['B']}, C={shop_imp['C']}, D={shop_imp['D']}")

    # UIカスタマイズ仕様書
    print("\n【4】UIカスタマイズ仕様書作成...")
    total = create_ui_customization_csv(
        company_rows, shop_rows,
        '/Users/sugurutsutsui/Downloads/UIカスタマイズ仕様書_V41.csv'
    )
    print(f"  総指標数: {total}")

    print("\n" + "=" * 60)
    print("完了!")
    print("出力ファイル:")
    print("  - 会社画面_データリネージュ図_V41.html")
    print("  - 店舗画面_データリネージュ図_V41.html")
    print("  - UIカスタマイズ仕様書_V41.csv")
    print("=" * 60)


if __name__ == '__main__':
    main()
