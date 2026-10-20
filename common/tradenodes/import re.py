import re

DOSYA_YOLU = r"C:\Users\muham\OneDrive\Documents\Paradox Interactive\Europa Universalis IV\mod\Darapmarap\common\tradenodes\00_tradenodes.txt"

# Bütün eyaletlerin toplanacağı ana düğüm
HEDEF_NODE = "carribean_trade"

# Dosyandaki tüm Amerika düğümleri
AMERIKA_NODELARI = [
    "patagonia", "amazonas_node", "rio_grande", "james_bay", "california",
    "mississippi_river", "ohio", "mexico", "cuiaba", "lima", "laplata",
    "brazil", "panama", "carribean_trade", "chesapeake_bay", "st_lawrence"
]

with open(DOSYA_YOLU, "r", encoding="utf-8") as f:
    content = f.read()

node_members_spans = {}
all_provinces = set()

# 1. Amerika düğümlerindeki eyalet sayılarını topla ve konumlarını belirle
for node in AMERIKA_NODELARI:
    node_start_match = re.search(r'\b' + node + r'\s*=\s*\{', content)
    if not node_start_match:
        continue
    
    start_idx = node_start_match.start()
    depth = 0
    end_idx = start_idx
    for i in range(node_start_match.end() - 1, len(content)):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                end_idx = i + 1
                break
    
    node_block = content[start_idx:end_idx]
    
    mem_match = re.search(r'\bmembers\s*=\s*\{', node_block)
    if mem_match:
        m_start = start_idx + mem_match.start()
        m_depth = 0
        m_end = m_start
        for i in range(start_idx + mem_match.end() - 1, len(content)):
            if content[i] == '{':
                m_depth += 1
            elif content[i] == '}':
                m_depth -= 1
                if m_depth == 0:
                    m_end = i + 1
                    break
        
        members_text = content[m_start:m_end]
        nums = re.findall(r'\b\d+\b', members_text)
        all_provinces.update(nums)
        node_members_spans[node] = (m_start, m_end)

# 2. Dosya yapısını bozmadan sadece members kısımlarını güncelle
sorted_spans = sorted(node_members_spans.items(), key=lambda x: x[1][0], reverse=True)
sorted_nums_str = " ".join(sorted(all_provinces, key=int))

for node, (s_start, s_end) in sorted_spans:
    if node == HEDEF_NODE:
        new_members = f"members = {{ \n\t\t{sorted_nums_str}\n\t}}"
    else:
        new_members = "members = { }"
    
    content = content[:s_start] + new_members + content[s_end:]

with open(DOSYA_YOLU, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Islem tamam! Toplam {len(all_provinces)} eyalet '{HEDEF_NODE}' altinda birlestirildi.")