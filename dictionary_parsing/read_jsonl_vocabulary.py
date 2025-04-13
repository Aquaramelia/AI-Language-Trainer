import json

from database_helpers import add_dict_entry

def read_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 10000:
                break
            elif i >= 0:
                yield json.loads(line)

def main():
    for entry in read_jsonl("kaikki-dict.jsonl"):
        f = open("output.txt", "w", encoding="utf-8")
        pretty_entry = json.dumps(entry, indent=4, ensure_ascii=False)
        f.write(pretty_entry)
        
        # List of possible forms of the word
        form_list = [f["form"] for f in entry.get("forms", []) if f and "table" not in f["form"] and "decl" not in f["form"]]
        form_list = list(set(form_list))
        
        # Entry word
        word = entry.get("word", "")
        
        # List of derived words
        derived_list = [f["word"] for f in entry.get("derived", [])]
        derived_list = list(set(derived_list))
        
        # List of related words
        related_list = [f["word"] for f in entry.get("related", [])]
        related_list = list(set(related_list))
        
        # List of senses
        senses_list = [
            links[0][0]
            for f in entry.get("senses", [])
            if (links := f.get("links")) and len(links) > 0 and len(links[0]) > 0
        ]
        senses_list = list(set(senses_list))
        
        # List of synonyms
        synonyms_list = [f.get("synonyms") for f in entry.get("senses", [])]
        synonyms_list = [x for x in synonyms_list if x is not None]
        synonyms_list = [entry['word'] for sublist in synonyms_list for entry in sublist]
        synonyms_list = list(set(synonyms_list))
        
        # List of antonyms
        antonyms_list = [f.get("antonyms") for f in entry.get("senses", [])]
        antonyms_list = [x for x in antonyms_list if x is not None]
        antonyms_list = [entry['word'] for sublist in antonyms_list for entry in sublist]
        antonyms_list = list(set(antonyms_list))
        
        # List of examples
        examples_list = [f.get("examples", []) for f in entry.get("senses", [])]
        examples_raw = entry.get("examples", [])
        examples_list = [
            ex.get("text", ex.get("ref"))
            for ex in examples_raw
            if isinstance(ex, dict) and ("text" in ex)
        ]
        # examples_list = [entry['text'] for sublist in examples_list for entry in sublist if entry is not None]
        examples_list = list(set(examples_list))
        
        # List of meanings (glosses)
        glosses_list = [f.get("glosses") for f in entry.get("senses", [])]
        glosses_list = [x for x in glosses_list if x is not None]
        glosses_list = [entry for sublist in glosses_list for entry in sublist]
        glosses_list = list(set(glosses_list))
        
        print("Word added: ", word)
        add_dict_entry(
            word=word,
            forms=str(form_list),
            derived=str(derived_list),
            related=str(related_list),
            synonyms=str(synonyms_list),
            antonyms=str(antonyms_list),
            senses=str(senses_list),
            glosses=str(glosses_list),
            examples=str(examples_list)
        )
        f.close()
    
if __name__ == "__main__":
    main()
