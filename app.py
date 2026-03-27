import json
import os

def clean_and_learn():
    files = ['osnova.json', 'vuzor.json']
    all_entries = []

    for file in files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    all_entries.extend(data)
                except:
                    continue

    # Usuwanie duplikatów (klucz: język polski)
    unique_dict = {}
    for entry in all_entries:
        p = entry.get('polish', '').lower().strip()
        s = entry.get('slovian', '').strip()
        if p and s:
            unique_dict[p] = s

    # Sortowanie alfabetyczne dla porządku
    sorted_data = [{"polish": k, "slovian": v} for k, v in sorted(unique_dict.items())]

    # Zapisanie "nauczonego" i czystego słownika
    with open('osnova.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    print(f"Sukces: Słownik zaktualizowany. Liczba słów: {len(sorted_data)}")

if __name__ == "__main__":
    clean_and_learn()
