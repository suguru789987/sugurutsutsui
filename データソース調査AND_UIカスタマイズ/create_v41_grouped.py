# -*- coding: utf-8 -*-
"""
V41 再構成スクリプト
- 画面タイプでグループ化（表示画面/設定入力画面）
- 予算一覧は表示画面に含める
- 各グループ内はV36案3の画面タイトル・指標名の順番
- Noは区分別に1から付番
"""

import csv
from datetime import datetime
import re

# ============================================
# 会社画面：本部・オーナー視点の経営重要度
# ============================================
COMPANY_IMPORTANCE = {
    'S': {
        'description': '最重要（経営判断直結）',
        'criteria': '収益性・投資回収に直結、取締役会/オーナー報告必須',
        'indicators': [
            '営業利益', '営業利益率', 'ROI', 'FL率', 'FD仕入率', '人件費率',
            '経常利益', '粗利', '粗利率'
        ],
        'patterns': [
            r'営業利益', r'利益率', r'ROI', r'FL率', r'粗利'
        ]
    },
    'A': {
        'description': '重要（業績管理必須）',
        'criteria': '月次業績報告の主要KPI、全店舗比較の基準',
        'indicators': [
            '売上(税抜)', '売上税抜', '売上', '客数', '客単価', '当月客数',
            'FD仕入', '人件費', '原価率', '仕入率'
        ],
        'patterns': [
            r'^売上', r'客数', r'客単価', r'FD仕入$', r'^人件費$', r'原価率'
        ]
    },
    'B': {
        'description': '標準（管理対象）',
        'criteria': '予実管理・進捗管理の対象、店舗評価指標',
        'indicators': [
            '売上達成率', '売上進捗率', '利益進捗率', '達成率', '進捗率',
            '坪月商', '家賃比率', '売上目標', '予算金額'
        ],
        'patterns': [
            r'達成率', r'進捗率', r'坪月商', r'家賃比率', r'目標', r'予算'
        ]
    },
    'C': {
        'description': '参考（分析用）',
        'criteria': '詳細分析・原因究明に使用、定期確認不要',
        'indicators': [
            '売上構成比率', '販売点数', '販売点数構成比率', '価格', '単価',
            '金額税抜', '比率', '数量', '平均売上', '平均客数',
            'ランチ売上', 'ディナー売上', '時間帯', '曜日'
        ],
        'patterns': [
            r'構成比', r'販売点数', r'金額', r'比率$', r'数量', r'平均',
            r'ランチ', r'ディナー', r'時間帯', r'曜日'
        ]
    },
    'D': {
        'description': '補助（マスタ/設定）',
        'criteria': 'マスタデータ、設定値、ラベル情報',
        'indicators': [
            '店舗名', '商品', '商品名', 'アイテム', '仕入れ先', '費目',
            '支払方法', '仕入商品ラベル'
        ],
        'patterns': [
            r'店舗名', r'^商品$', r'商品名', r'アイテム', r'仕入れ先', r'仕入先',
            r'^費目$', r'支払方法', r'ラベル'
        ]
    }
}

# ============================================
# 店舗画面：店長視点の経営重要度
# ============================================
SHOP_IMPORTANCE = {
    'S': {
        'description': '最重要（日次確認必須）',
        'criteria': '毎日確認すべき数値、売上・利益に直結',
        'indicators': [
            '売上(税抜)', '売上税抜', '売上', '営業利益', 'FL率', '人件費率',
            'FD仕入率', '日次', '本日'
        ],
        'patterns': [
            r'^売上\(税抜\)$', r'^売上税抜$', r'^売上$', r'営業利益', r'FL率',
            r'人件費率', r'FD仕入率', r'日次'
        ]
    },
    'A': {
        'description': '重要（週次確認推奨）',
        'criteria': '週次で傾向把握、シフト・発注判断に影響',
        'indicators': [
            '客数', '客単価', 'FD原価率', '原価率', '売上達成率', 'FD仕入',
            '人件費', '仕入税抜'
        ],
        'patterns': [
            r'客数', r'客単価', r'原価率', r'達成率', r'^FD仕入$', r'^人件費$'
        ]
    },
    'B': {
        'description': '標準（月次確認）',
        'criteria': '月次振り返り、改善施策立案に使用',
        'indicators': [
            '坪月商', '売上進捗率', '利益進捗率', '進捗率', 'ROI', '家賃比率',
            '営業利益率', '売上目標', '商品別売上'
        ],
        'patterns': [
            r'坪月商', r'進捗率', r'ROI', r'家賃比率', r'営業利益率', r'目標'
        ]
    },
    'C': {
        'description': '参考（必要時確認）',
        'criteria': '問題発生時の原因分析、詳細確認用',
        'indicators': [
            '時間帯別', '曜日別', '仕入先', '売上構成比率', '販売点数',
            '金額税抜', '比率', '平均売上', '平均客数', 'ランチ', 'ディナー'
        ],
        'patterns': [
            r'時間帯', r'曜日', r'仕入先', r'構成比', r'販売点数',
            r'金額', r'比率$', r'平均', r'ランチ', r'ディナー'
        ]
    },
    'D': {
        'description': '補助（設定/入力）',
        'criteria': '設定入力、マスタ情報、直接管理対象外',
        'indicators': [
            '予算設定', '費用入力', '棚卸', '店舗マスタ', '商品', '商品名',
            'アイテム', '費目', '支払方法', '仕入商品ラベル'
        ],
        'patterns': [
            r'予算', r'費用', r'棚卸', r'マスタ', r'^商品$', r'商品名',
            r'アイテム', r'^費目$', r'支払方法', r'ラベル'
        ]
    }
}

# 表示画面として扱う画面タイトル（予算一覧を含む）
DISPLAY_SCREEN_TITLES = ['予算一覧', '予算一覧(予算構成)', '予算一覧(予算設定値)']


def determine_importance(indicator_name, screen_title, data_source_type, screen_type):
    """経営重要度を判定"""

    if screen_type == '会社':
        importance_def = COMPANY_IMPORTANCE
    else:
        importance_def = SHOP_IMPORTANCE

    # 設定入力画面は基本的にD（ただし予算一覧は除く）
    if ('設定' in screen_title or '入力' in screen_title or '棚卸' in screen_title) and screen_title not in DISPLAY_SCREEN_TITLES:
        return 'D', importance_def['D']['description']

    # データソース区分による判定
    if data_source_type in ['店舗マスタ（設定）']:
        return 'D', importance_def['D']['description']

    # 指標名によるパターンマッチング（S→A→B→C→Dの順で判定）
    for rank in ['S', 'A', 'B', 'C', 'D']:
        # 完全一致チェック
        if indicator_name in importance_def[rank]['indicators']:
            return rank, importance_def[rank]['description']

        # パターンマッチング
        for pattern in importance_def[rank]['patterns']:
            if re.search(pattern, indicator_name):
                return rank, importance_def[rank]['description']

    # 画面タイトルによる補足判定
    if screen_type == '店舗':
        if '日次' in screen_title:
            return 'S', importance_def['S']['description']
        elif any(x in screen_title for x in ['主要KPI', '当月実績', '店舗別サマリー']):
            return 'A', importance_def['A']['description']
    else:  # 会社
        if any(x in screen_title for x in ['主要KPI', '当月実績']):
            return 'A', importance_def['A']['description']
        elif '店舗別' in screen_title or 'サマリー' in screen_title:
            return 'B', importance_def['B']['description']

    # デフォルト
    return 'C', importance_def['C']['description']


def get_screen_type_for_row(screen_title, original_screen_type):
    """行の画面タイプを決定（予算一覧は表示画面として扱う）"""
    if screen_title in DISPLAY_SCREEN_TITLES:
        return '表示画面'
    return original_screen_type


def read_v36_order(v36_file):
    """V36案3から画面タイトル・指標名の順番を読み取る"""
    order_list = []

    with open(v36_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if row and row[0] == 'No':
                header = row
            elif header and row and row[0].isdigit():
                row_dict = dict(zip(header, row))
                screen_title = row_dict.get('画面タイトル', '')
                indicator_name = row_dict.get('指標名', '')
                order_list.append((screen_title, indicator_name))

    return order_list


def process_v40_to_v41_grouped(input_file, output_file, v36_file, screen_type):
    """V40を読み込み、V36の順番でグループ化してV41を出力"""

    # V36の順番を読み込む
    v36_order = read_v36_order(v36_file)

    # V40を読み込む
    rows = []
    header = None

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == 'No':
                header = row
            elif header and row and row[0].isdigit():
                rows.append(dict(zip(header, row)))

    # 経営重要度を再判定
    importance_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}

    for row in rows:
        indicator_name = row.get('指標名', '')
        screen_title = row.get('画面タイトル', '')
        data_source_type = row.get('データソース区分', '')

        new_importance, description = determine_importance(
            indicator_name, screen_title, data_source_type, screen_type
        )
        row['経営重要度'] = new_importance
        importance_counts[new_importance] += 1

        # 画面タイプを修正（予算一覧は表示画面）
        original_screen_type = row.get('画面タイプ', '')
        row['画面タイプ'] = get_screen_type_for_row(screen_title, original_screen_type)

    # V36の順番に基づいてソート用の辞書を作成
    v36_order_dict = {}
    for idx, (screen_title, indicator_name) in enumerate(v36_order):
        key = (screen_title, indicator_name)
        v36_order_dict[key] = idx

    def get_sort_key(row):
        key = (row.get('画面タイトル', ''), row.get('指標名', ''))
        return v36_order_dict.get(key, 99999)

    # 表示画面と設定入力画面に分ける
    display_rows = [r for r in rows if r.get('画面タイプ') == '表示画面']
    input_rows = [r for r in rows if r.get('画面タイプ') == '設定入力画面']

    # V36の順番でソート
    display_rows_sorted = sorted(display_rows, key=get_sort_key)
    input_rows_sorted = sorted(input_rows, key=get_sort_key)

    # 重要度定義を取得
    if screen_type == '会社':
        importance_def = COMPANY_IMPORTANCE
        viewpoint = '本部・オーナー視点'
    else:
        importance_def = SHOP_IMPORTANCE
        viewpoint = '店長視点'

    # V41を出力
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow([f'ラクミー経営管理 {screen_type}画面 データソース定義表 V41（経営重要度再定義版）'])
        writer.writerow([f'作成日: {datetime.now().strftime("%Y年%m月%d日")}'])
        writer.writerow([f'総指標数: {len(rows)}指標'])
        writer.writerow([f'経営重要度: {viewpoint}'])
        writer.writerow([])

        # 経営重要度の定義を出力
        writer.writerow(['■ 経営重要度 定義'])
        writer.writerow([])
        writer.writerow(['ランク', '定義', '判断基準', '該当指標数'])
        for rank in ['S', 'A', 'B', 'C', 'D']:
            writer.writerow([
                rank,
                importance_def[rank]['description'],
                importance_def[rank]['criteria'],
                f'{importance_counts[rank]}指標'
            ])
        writer.writerow([])

        # 表示画面セクション
        if display_rows_sorted:
            writer.writerow([f'■ 表示画面 ({len(display_rows_sorted)}指標)'])
            writer.writerow([])
            writer.writerow(header)
            # 番号を1から付番
            for idx, row in enumerate(display_rows_sorted, 1):
                row['No'] = str(idx)
                writer.writerow([row.get(h, '') for h in header])

        # 設定入力画面セクション
        if input_rows_sorted:
            writer.writerow([])
            writer.writerow([f'■ 設定入力画面 ({len(input_rows_sorted)}指標)'])
            writer.writerow([])
            writer.writerow(header)
            # 番号を1から付番
            for idx, row in enumerate(input_rows_sorted, 1):
                row['No'] = str(idx)
                writer.writerow([row.get(h, '') for h in header])

    return len(rows), importance_counts, len(display_rows_sorted), len(input_rows_sorted)


def main():
    print("=" * 60)
    print("V41 データソース定義表 作成（画面タイプ別グループ化版）")
    print("=" * 60)

    # 会社画面
    print("\n【会社画面】本部・オーナー視点で再定義...")
    company_total, company_counts, company_display, company_input = process_v40_to_v41_grouped(
        '/Users/sugurutsutsui/Downloads/会社画面_データソース定義表_V40.csv',
        '/Users/sugurutsutsui/Downloads/会社画面_データソース定義表_V41.csv',
        '/Users/sugurutsutsui/Downloads/会社画面_データソース定義表_V36_案3.csv',
        '会社'
    )
    print(f"  総指標数: {company_total}")
    print(f"  表示画面: {company_display}指標")
    print(f"  設定入力画面: {company_input}指標")
    print(f"  S(最重要): {company_counts['S']}")
    print(f"  A(重要): {company_counts['A']}")
    print(f"  B(標準): {company_counts['B']}")
    print(f"  C(参考): {company_counts['C']}")
    print(f"  D(補助): {company_counts['D']}")

    # 店舗画面
    print("\n【店舗画面】店長視点で再定義...")
    shop_total, shop_counts, shop_display, shop_input = process_v40_to_v41_grouped(
        '/Users/sugurutsutsui/Downloads/店舗画面_データソース定義表_V40.csv',
        '/Users/sugurutsutsui/Downloads/店舗画面_データソース定義表_V41.csv',
        '/Users/sugurutsutsui/Downloads/店舗画面_データソース定義表_V36_案3.csv',
        '店舗'
    )
    print(f"  総指標数: {shop_total}")
    print(f"  表示画面: {shop_display}指標")
    print(f"  設定入力画面: {shop_input}指標")
    print(f"  S(最重要): {shop_counts['S']}")
    print(f"  A(重要): {shop_counts['A']}")
    print(f"  B(標準): {shop_counts['B']}")
    print(f"  C(参考): {shop_counts['C']}")
    print(f"  D(補助): {shop_counts['D']}")

    print("\n" + "=" * 60)
    print("完了!")
    print("出力ファイル:")
    print("  - 会社画面_データソース定義表_V41.csv")
    print("  - 店舗画面_データソース定義表_V41.csv")
    print("=" * 60)


if __name__ == '__main__':
    main()
