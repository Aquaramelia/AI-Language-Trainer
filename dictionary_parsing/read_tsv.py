import csv
import os

def read_tsv(filepath):
    with open(filepath, newline='', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for i, row in enumerate(reader):
            if i == 20:
                break
            yield row  # each row is a list: [id, lang, sentence]

def main():
    print("Current working directory:", os.getcwd())
    for row in read_tsv("deu_sentences.tsv"):
        print(row)

if __name__ == "__main__":
    main()
