import json

# 조합 카운터 데이터 (원본 표기 그대로 저장)
combo_counter_data = {
    "탐 켄치": []
}

# JSONL 읽기
file_path = "champ.jsonl"
lines = []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        champ_name = data.get("champion", "")
        if champ_name in combo_counter_data:
            data["combo_counters"] = combo_counter_data[champ_name]
            print(f"✅ {champ_name} - combo_counters 추가됨")
        lines.append(data)

# JSONL 다시 쓰기
with open(file_path, "w", encoding="utf-8") as f:
    for data in lines:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

print("\n완료! champ.jsonl 업데이트됨")
