import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt')
nltk.download('stopwords')

def extract_pubmed_abstracts(file_path):
    # Create lists to store PubMed IDs and abstracts
    pubmed_ids = []
    abstracts = []
    ann = []

    # Open the file and read through it line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            pubmed_id = 0
            # Check if the line contains an abstract
            if '|a|' in line:
                parts = line.split('|a|')
                if len(parts) > 1:
                    # Extract PubMed ID from the part before '|a|'
                    pubmed_id = parts[0].split('|')[0]
                    # The abstract is the part after '|a|'
                    abstract = parts[1].strip()

                    pubmed_ids.append(pubmed_id)
                    abstracts.append(abstract)
          
            if '|ann|' in line: 
              parts = line.split('|ann|')
              id = parts[0].strip()
              annotations = parts[1].strip()
              ann.append({'id': id, 'abbr': annotations.split('|')[0], 'FS': annotations.split('|')[1]})

    df = pd.DataFrame({
        'PubMedID': pubmed_ids,
        'Abstract': abstracts
    })

    return df, pd.DataFrame(ann)


file_path = '../data/ncbi/NCBItestset_corpus_WSD.txt'
df_abstracts, df_annotation = extract_pubmed_abstracts(file_path)


def words_tokenize(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words and word not in ['.', ',', '(', ')', '[', ']',':','-']]
    return filtered_tokens

def add_unique(dictionary, list_of_dictionaries):
    if dictionary not in list_of_dictionaries:
        list_of_dictionaries.append(dictionary)
        
non_ambiguous_abbr = ['ADNDI','B-NHL','BPAD','C5D','C6D','EDMD','FNDI','FRDA','HNPCC','NF1','PKU','T-PLL','VLCAD','XLDCM']       
        
final_sentences = []
for id, abstract in df_abstracts.iterrows():
  pmid = abstract['PubMedID']
  text = abstract['Abstract']
  sentences = sent_tokenize(text)
  annotations = df_annotation[df_annotation['id']==pmid]
  for id, ann in annotations.iterrows():
    abbr = ann['abbr']
    FS = ann['FS']
    for sentence in sentences:
      if abbr.strip() not in non_ambiguous_abbr:
        if f' {abbr} ' or f'({abbr})' in sentence:
          if FS.lower() in sentence.lower():
            masked_sentence = re.sub(FS, '', sentence, flags=re.IGNORECASE)
            masked_sentence = masked_sentence.replace(f'({abbr})', abbr)
            data = {'pmid': pmid, 'sentence': sentence, 'masked_sentence':masked_sentence, 'abbr': abbr, 'FS': FS.lower()}
            add_unique(data,final_sentences)
          elif f' {abbr} ' in sentence:
            masked_sentence = sentence
            data = {'pmid': pmid, 'sentence': sentence, 'masked_sentence':masked_sentence, 'abbr': abbr, 'FS': FS.lower()}
            add_unique(data,final_sentences)

sentences_df = pd.DataFrame(final_sentences)
sentences_df.to_csv('../data/ncbi/WSD_NCBI_sentences.csv', index=False)

# print(df_abstracts.head(3))
# print("#"*50)
# print(df_annotation.head(3))
# print("#"*50)
# print(sentences_df.head(3))