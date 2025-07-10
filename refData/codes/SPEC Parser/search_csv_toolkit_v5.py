
import csv
import json
import argparse

def load_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        return list(csv.reader(f))

def load_rules(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def collect_results(reader, rules, model_count):
    result_rows = [[] for _ in range(model_count)]

    for rule_index, rule in enumerate(rules):
        keywords = rule.get("keywords", [])
        logic = rule.get("logic", "OR").upper()
        rowspan = rule.get("rowspan", 1)
        column_name = rule.get("column_name", f"欄位{rule_index+1}")

        matched_blocks = []

        for i, row in enumerate(reader):
            if logic == "AND":
                match = True
                for kw in keywords:
                    if not any(kw.lower() in str(cell).lower() for cell in row):
                        match = False
                        break
            else:
                match = False
                for kw in keywords:
                    if any(kw.lower() in str(cell).lower() for cell in row):
                        match = True
                        break

            if match:
                block = reader[i:i + rowspan]
                matched_blocks.append((i, block))

        if len(matched_blocks) == 0:
            print(f"⚠️ 規則 {rule_index+1} - {column_name}: 找不到關鍵字 {keywords}，全欄填空白")
            for idx in range(model_count):
                result_rows[idx].append("")
        else:
            if len(matched_blocks) > 1:
                print(f"⚠️ 警告：規則 {rule_index+1} - {column_name} 找到超過一個匹配（共 {len(matched_blocks)} 個），僅使用第一筆！")
            first_index, block = matched_blocks[0]
            print(f"🔍 規則 {rule_index+1} - {column_name}: 找到關鍵字 {keywords} 於第 {first_index+1} 行")

            for idx in range(model_count):
                col_index = 2 + idx
                if all(col_index < len(row) for row in block):
                    lines = []
                    for r in block:
                        value = r[col_index].strip()
                        prefix_label = r[1].strip() if len(r) > 1 else ""
                        if prefix_label:
                            lines.append(f"{prefix_label}: {value}")
                        else:
                            lines.append(value)
                    result = "\n".join(lines).strip()
                    result_rows[idx].append(result)
                    print(f"  → 機種{idx+1}: {result}")
                else:
                    result_rows[idx].append("")
                    print(f"  → 機種{idx+1}: ⚠️警告：該機種此處無資料")

    return result_rows

def write_csv(output_path, result_rows, headers, model_type):
    headers = ["modeltype"] + headers
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in result_rows:
            writer.writerow([model_type] + row)
    print(f"✅ 已輸出至：{output_path}")

def main():
    parser = argparse.ArgumentParser(description="根據 JSON 規則搜尋 CSV 並轉為每機種一列格式（v4 + prefix 每列讀取）")
    parser.add_argument("csv_path", help="輸入CSV")
    parser.add_argument("json_path", help="規則JSON")
    parser.add_argument("--model_count", type=int, required=True, help="幾個機種")
    parser.add_argument("--model_type", type=str, required=True, help="共用的 model type 字串")
    parser.add_argument("--output_csv", required=True, help="輸出CSV檔名")

    args = parser.parse_args()

    reader = load_csv(args.csv_path)
    rules = load_rules(args.json_path)
    results = collect_results(reader, rules, args.model_count)

    headers = [
        rule.get("column_name").strip() if rule.get("column_name") and rule.get("column_name").strip() != "" else f"欄位{i+1}"
        for i, rule in enumerate(rules)
    ]
    write_csv(args.output_csv, results, headers, args.model_type)

if __name__ == "__main__":
    main()
