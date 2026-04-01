import json
import os

def load_dicts():
    data = []
    for f in ['osnova.json', 'vuzor.json']:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                data.extend(json.load(file))
    return data

def save_dict(data, filename='osnova.json'):
    unique = {}
    for entry in data:
        p = entry.get('polish', '').lower().strip()
        if p:
            unique[p] = entry
    sorted_data = sorted(unique.values(), key=lambda x: x.get('polish','').lower())
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print(f"Learned: {len(sorted_data)} entries")

def learn_from_examples(examples_file='examples.json'):
    if not os.path.exists(examples_file):
        print("No examples.json")
        return
    with open(examples_file, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    existing = load_dicts()
    new_entries = []
    for ex in examples:
        entry = {
            "type and case": ex.get("type", "phrase - rěčenьje"),
            "context": ex.get("context", ""),
            "polish": ex["polish"],
            "slovian": ex["slovian"]
        }
        if "case" in ex:
            entry["type and case"] += f" | {ex['case']}"
        new_entries.append(entry)
    all_data = existing + new_entries
    save_dict(all_data)

if __name__ == "__main__":
    learn_from_examples()
