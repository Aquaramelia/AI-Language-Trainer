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
        form_list = [
            f["form"] 
            for f in entry.get("forms", []) 
            if f and "table-tags" not in f.get("tags") 
            and "inflection-template" not in f.get("tags")
            and "class" not in f.get("tags")]
        form_list = list(set(form_list))
        
        # # Entry word
        word = entry.get("word", "")
        
        # List of senses
        # senses_list = [f.get("links", [])[0][0] for f in entry.get("senses", [])]
        senses_list = [
            link[0]
            for f in entry.get("senses", [])
            if "links" in f and isinstance(f["links"], list)
            for link in f["links"]
            if isinstance(link, list) and len(link) > 0
        ]

        senses_list = list(set(senses_list))
        
        # List of examples
        examples_list = [f.get("examples", []) for f in entry.get("senses", [])]
        examples_list = [entry['text'] for sublist in examples_list for entry in sublist if entry is not None]
        examples_list = list(set(examples_list))
        
        examples_list = examples_list + list({
            ex["text"]
            for sense in entry.get("senses", [])
            for ex in sense.get("examples", [])
            if ex and "text" in ex
        })
        examples_list = examples_list + [f["word"] for f in entry.get("examples", []) if f]
        examples_list = list(set(examples_list))
        
        # List of derived words
        derived_list = [
            f["word"]
            for sense in entry.get("senses", []) 
            for f in sense.get("derived", [])]
        derived_list = derived_list + [f["word"] for f in entry.get("derived", []) if f]
        derived_list = list(set(derived_list))
        
        # List of related words
        related_list = [
            f["word"]
            for sense in entry.get("senses", []) 
            for f in sense.get("related", [])]
        related_list = related_list + [f["word"] for f in entry.get("related", []) if f]
        related_list = list(set(related_list))
        
        # List of hyponyms
        hyponyms_list = [
            f["word"]
            for sense in entry.get("senses", [])
            if sense and "hyponyms" in sense
            for f in sense["hyponyms"]
            if "word" in f
        ]
        hyponyms_list = hyponyms_list + [f["word"] for f in entry.get("hyponyms", []) if f]
        hyponyms_list = list(set(hyponyms_list))
        
        # List of hypernyms
        hypernyms_list = [
            f["word"]
            for sense in entry.get("senses", [])
            if sense and "hypernyms" in sense
            for f in sense["hypernyms"]
            if "word" in f
        ]
        hypernyms_list = hypernyms_list + [f["word"] for f in entry.get("hypernyms", []) if f]
        hypernyms_list = list(set(hypernyms_list))
        
        # List of synonyms
        synonyms_list = [f.get("synonyms") for f in entry.get("senses", [])]
        synonyms_list = [x for x in synonyms_list if x is not None]
        synonyms_list = [entry['word'] for sublist in synonyms_list for entry in sublist]
        
        synonyms_list = synonyms_list + [f["word"] for f in entry.get("synonyms", []) if f]
        synonyms_list = list(set(synonyms_list))
        
        # List of antonyms
        antonyms_list = [f.get("antonyms") for f in entry.get("senses", [])]
        antonyms_list = [x for x in antonyms_list if x is not None]
        antonyms_list = [entry['word'] for sublist in antonyms_list for entry in sublist]
        
        antonyms_list = antonyms_list + [f["word"] for f in entry.get("antonyms", []) if f]
        antonyms_list = list(set(antonyms_list))
        
        # List of meanings (glosses)
        glosses_list = [f.get("glosses") for f in entry.get("senses", [])]
        glosses_list = [x for x in glosses_list if x is not None]
        glosses_list = [entry for sublist in glosses_list for entry in sublist]
        glosses_list = list(set(glosses_list))
        
        # Get appropriate article, if it is a noun
        head_templates = entry.get("head_templates", [])
        part_of_speech = ""
        if head_templates:
            part_of_speech = head_templates[0].get("name", "")
        article = ""
        if part_of_speech and part_of_speech == "de-noun":
            args = head_templates[0].get("args")
            if args:
                gender = args.get("1", "")
                if gender:
                    gender = gender[0]
                    if gender == "m":
                        article = "der"
                    elif gender == "f" or gender == "p":
                        article = "die"
                    elif gender == "n":
                        article = "das"
        
        i -= 1
        
        add_cat_entry(
            word=word,
            article=article,
            forms=str(form_list),
            senses=str(senses_list),
            glosses=str(glosses_list),
            examples=str(examples_list),
            related=str(related_list),
            derived=str(derived_list),
            hyponyms=str(hyponyms_list),
            hypernyms=str(hypernyms_list),
            antonyms=str(antonyms_list),
            synonyms=str(synonyms_list),
            category=category,
            index=i
        )
        f.close()
        
    
 
if __name__ == "__main__":
    category = "Ecology"
    main(
        filename=f"data/{category}.jsonl",
        category=category
    )
