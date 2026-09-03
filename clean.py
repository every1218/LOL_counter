import sys
import json

# Ensure Windows console uses UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def format_counter_item(item):
    """
    카운터 객체를 한 줄 { "name": "...", "reason": "..." } 형태의 문자열로 변환합니다.
    """
    if isinstance(item, dict):
        name = item.get("name", "")
        reason = item.get("reason", "")
    else:
        name = str(item)
        reason = ""
    name_json = json.dumps(name, ensure_ascii=False)
    reason_json = json.dumps(reason, ensure_ascii=False)
    return f'{{ "name": {name_json}, "reason": {reason_json} }}'


def format_string_array(items, indent_level=4, max_width=80):
    """
    문자열 배열(aliases, lines, synergy 등)을 정돈된 형태로 변환합니다.
    - 길이가 짧거나 항목이 적으면 한 줄로 표시
    - 시너지처럼 항목이 많거나 길 경우 지정한 글자 수(max_width) 기준으로 보기좋게 줄바꿈
    """
    if not items:
        return "[]"

    # 한 줄로 표현 가능한지 확인
    single_line_content = ", ".join(json.dumps(x, ensure_ascii=False) for x in items)
    single_line = f"[{single_line_content}]"

    prefix_space = " " * indent_level
    # 길이가 짧거나 (max_width 이하) 항목 개수가 3개 이하인 경우 한 줄로 유지
    if len(prefix_space + single_line) <= max_width or len(items) <= 3:
        return single_line

    # 기준 글자 수 초과 시 멀티라인 줄바꿈 처리
    sub_indent = " " * (indent_level + 2)
    lines = ["["]
    current_line = sub_indent

    for i, item in enumerate(items):
        item_str = json.dumps(item, ensure_ascii=False)
        is_last = i == len(items) - 1
        sep = "" if is_last else ","

        token = item_str + sep
        if current_line == sub_indent:
            current_line += token
        else:
            if len(current_line) + 1 + len(token) > max_width:
                lines.append(current_line)
                current_line = sub_indent + token
            else:
                current_line += " " + token

    if current_line.strip():
        lines.append(current_line)

    lines.append(" " * indent_level + "]")
    return "\n".join(lines)


def format_champ_entry(champ):
    """
    단일 챔피언 객체를 요구사항에 맞춰 깔끔하게 정돈된 JSON 문자열로 변환합니다.
    """
    fields = []

    # 1. 챔피언 이름
    fields.append('"champion": ' + json.dumps(champ["champion"], ensure_ascii=False))

    # 2. aliases (한 줄 정리)
    aliases = champ.get("aliases", [])
    fields.append('"aliases": ' + format_string_array(aliases, indent_level=4, max_width=80))

    # 3. lines (한 줄 정리)
    lines_arr = champ.get("lines", [])
    fields.append('"lines": ' + format_string_array(lines_arr, indent_level=4, max_width=80))

    # 4. 하드 카운터 (각 항목 { "name": ..., "reason": ... } 1줄 정돈)
    hard_counters = champ.get("hard_counters", [])
    if not hard_counters:
        fields.append('"hard_counters": []')
    else:
        hc_lines = ['"hard_counters": [']
        for i, item in enumerate(hard_counters):
            comma = "," if i < len(hard_counters) - 1 else ""
            hc_lines.append(f"      {format_counter_item(item)}{comma}")
        hc_lines.append("    ]")
        fields.append("\n".join(hc_lines))

    # 5. 일반 카운터 (각 항목 { "name": ..., "reason": ... } 1줄 정돈)
    gen_counters = champ.get("general_counters", [])
    if not gen_counters:
        fields.append('"general_counters": []')
    else:
        gc_lines = ['"general_counters": [']
        for i, item in enumerate(gen_counters):
            comma = "," if i < len(gen_counters) - 1 else ""
            gc_lines.append(f"      {format_counter_item(item)}{comma}")
        gc_lines.append("    ]")
        fields.append("\n".join(gc_lines))

    # 6. 조합 카운터 (존재할 경우)
    if "combo_counters" in champ:
        combo = champ["combo_counters"]
        fields.append('"combo_counters": ' + format_string_array(combo, indent_level=4, max_width=80))

    # 7. 시너지 (기준 글자 수에 맞춰 줄바꿈 정돈)
    synergy = champ.get("synergy", [])
    fields.append('"synergy": ' + format_string_array(synergy, indent_level=4, max_width=80))

    # 필드들을 챔피언 객체 텍스트로 조립
    obj_lines = ["  {"]
    for i, field in enumerate(fields):
        comma = "," if i < len(fields) - 1 else ""
        f_lines = field.split("\n")
        if len(f_lines) == 1:
            obj_lines.append(f"    {f_lines[0]}{comma}")
        else:
            for j, fl in enumerate(f_lines):
                if j == len(f_lines) - 1:
                    obj_lines.append(f"{fl}{comma}")
                else:
                    obj_lines.append(f"    {fl}" if j == 0 else fl)
    obj_lines.append("  }")
    return "\n".join(obj_lines)


def clean_champ_json(json_path="champ.json"):
    """
    champ.json 파일 전체를 포맷팅하여 다시 저장합니다.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result_lines = ["["]
    for i, champ in enumerate(data):
        comma = "," if i < len(data) - 1 else ""
        entry_str = format_champ_entry(champ)
        result_lines.append(entry_str + comma)
    result_lines.append("]")

    formatted_json = "\n".join(result_lines) + "\n"

    # 검증: JSON 파싱 및 데이터 개수 확인
    parsed = json.loads(formatted_json)
    if len(parsed) != len(data):
        raise ValueError("포맷팅 오류: 챔피언 데이터 개수가 일치하지 않습니다!")

    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(formatted_json)

    print(f"[★] {json_path} 포맷팅 및 정리 완료! (총 {len(result_lines)}줄)")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "champ.json"
    clean_champ_json(target)
