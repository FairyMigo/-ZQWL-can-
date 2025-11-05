# -*- coding: gbk -*-

import csv
import re
from pathlib import Path

def hex_to_ascii(hex_str):
    """十六进制转ASCII（错误处理）"""
    try:
        hex_bytes = hex_str.strip().replace(' ', '')
        return bytes.fromhex(hex_bytes).decode('ascii', errors='replace')
    except Exception as e:
        print(f"解码错误: {e}")
        return ""

def process_ascii(original_str):
    """数值转换规则"""
    if len(original_str) < 2:
        return original_str
    
    char_list = list(original_str)
    try:
        char_list[1] = str(int(char_list[1]) + 1)
    except ValueError:
        pass
    
    modified_str = ''.join(char_list)
    match = re.search(r'([+-])(\d+)$', modified_str)
    
    if match:
        sign, digits = match.groups()
        try:
            value = int(f"{sign}{digits}")
            converted = f"{value/10000:.3f}mV"
            return re.sub(r'([+-]\d+)$', converted, modified_str)
        except ValueError:
            return modified_str
    
    return modified_str

# 文件路径配置，需要按实际路径修改！
input_path = Path(r"export_file.csv")

# 自动检测文件编码
encodings = ['utf-8', 'gbk', 'iso-8859-1']
file_encoding = 'utf-8'
for enc in encodings:
    try:
        with open(input_path, 'r', encoding=enc) as f:
            f.read(1024)
            file_encoding = enc
            break
    except UnicodeDecodeError:
        continue

# 主处理流程
rows = []
with open(input_path, 'r', encoding=file_encoding) as infile:
    reader = csv.reader(infile)
    
    # 读取并修改表头
    headers = next(reader) + ["传感器通道及位号", "电压数"]
    rows.append(headers)
    
    # 处理数据行
    for row in reader:
        if len(row) >= 10:
            raw_hex = row[9]
            decoded = hex_to_ascii(raw_hex)
            processed = process_ascii(decoded)
            
            # 拆分前两位和剩余内容
            prefix = processed[:2] if len(processed) >= 2 else processed
            remaining = processed[2:] if len(processed) >= 2 else ''
            row += [prefix, remaining]
        else:
            # 处理列不足的情况
            row += ['', '']
        rows.append(row)

# 写回原文件
with open(input_path, 'w', newline='', encoding=file_encoding) as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)

print(f"数据转换完成！已更新原文件：{input_path}")
