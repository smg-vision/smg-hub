with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import json, re

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', text, re.DOTALL)
if idmap_match:
    idmap = json.loads(idmap_match.group(1))
    print(f"Total keys in IDMAP: {len(idmap)}")
    
    # Check how many keys appear elsewhere in the file
    found_keys = {}
    for k in idmap:
        # count occurrences excluding the IDMAP declaration itself
        count = text.count(k) - 1
        if count > 0:
            found_keys[k] = count
            
    print(f"Keys found elsewhere in original_frame: {len(found_keys)} / {len(idmap)}")
    print("Found keys details:", found_keys)
