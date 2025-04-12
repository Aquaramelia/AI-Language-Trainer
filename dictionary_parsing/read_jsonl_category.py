import json

from database_helpers import add_cat_entry

def count_jsonl_entries(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        count = sum(1 for _ in f)
    print(f"Total entries: {count}")
    return count

def read_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            # if i == 1:
            #     break
            yield json.loads(line)



def main(filename, category):
    i = count_jsonl_entries(filepath=filename)
    for entry in read_jsonl(filepath=filename):
        f = open("output.txt", "w", encoding="utf-8")
        pretty_entry = json.dumps(entry, indent=4, ensure_ascii=False)
        f.write(pretty_entry)
        
        # List of possible forms of the word
        form_list = [f["form"] for f in entry.get("forms", []) if f and "table" not in f["form"] and "decl" not in f["form"] and "strong" not in f["form"] and "weak" not in f["form"]]
        form_list = list(set(form_list))
        
        # # Entry word
        word = entry.get("word", "")
        
        # List of senses
        # senses_list = [f.get("links", [])[0][0] for f in entry.get("senses", [])]
        senses_list = [
            links[0][0]
            for f in entry.get("senses", [])
            if (links := f.get("links")) and len(links) > 0 and len(links[0]) > 0
        ]

        senses_list = list(set(senses_list))
        
        # List of examples
        examples_list = [f.get("examples", []) for f in entry.get("senses", [])]
        examples_list = [entry['text'] for sublist in examples_list for entry in sublist if entry is not None]
        examples_list = list(set(examples_list))
        
        # # List of roman versions
        # roman_list = [f.get("roman", []) for f in entry.get("senses", [])]
        # if roman_list:
        #     roman_list = [entry['text'] for sublist in roman_list for entry in sublist if entry is not None]
        #     roman_list = list(set(roman_list))
        
        # List of meanings (glosses)
        glosses_list = [f.get("glosses") for f in entry.get("senses", [])]
        glosses_list = [x for x in glosses_list if x is not None]
        glosses_list = [entry for sublist in glosses_list for entry in sublist]
        glosses_list = list(set(glosses_list))
        
        i -= 1
        
        add_cat_entry(
            word=word,
            forms=str(form_list),
            senses=str(senses_list),
            glosses=str(glosses_list),
            examples=str(examples_list),
            category=category,
            index=i
        )
        f.close()
        
    
 
if __name__ == "__main__":
    category = "Zoology"
    main(
        filename=f"data/{category}.jsonl",
        category=category
    )
