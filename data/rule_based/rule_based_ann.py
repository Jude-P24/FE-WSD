import pandas as pd
import ast
from tqdm.auto import tqdm
tqdm.pandas()
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

data = pd.read_csv('../pubmed_abstracts/abstracts_final.csv')
dict = pd.read_csv('../ncbi/WSD_NCBI_dict.csv')
dict['variations'] = dict['variations'].apply(ast.literal_eval)


def contains_substring(sentence, substrings):
    sentence_lower = sentence.lower()
    return any(substring.lower() in sentence_lower for substring in substrings)

def find_keywords(text, keywords):
    found_keywords = set()
    
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, flags=re.IGNORECASE):
            found_keywords.add(keyword)
    
    return list(found_keywords)


import re

def replace_keywords(text, keywords, keyword_to_replace):
    found_keywords = find_keywords(text, keywords)
    
    modified_text = text
    
    for keyword in found_keywords:
        modified_text = re.sub(r'\b' + re.escape(keyword) + r'\b', keyword_to_replace, modified_text, flags=re.IGNORECASE)
    
    return modified_text



data_array = []

for id, row in data.iterrows():
    pmid = row['pmid']
    abbr = row['abbreviation']
    FS = row['full_spell']
    text = row['text']
    
    unique_FS = dict['FS'].unique().tolist()
    
    if FS in unique_FS:
        variations = dict[dict['FS']==FS]['variations'].iloc[0]
        sentences = sent_tokenize(text)
        for s in sentences:
            if abbr!='AAPC':
                abbr_arr = [f' {abbr} ']
            else:
                abbr_arr = [' AAPC ',' aAPC ']
                
            text_present = find_keywords(text, variations) 
            sentence_present = find_keywords(s, variations)               
            abbr_present = contains_substring(s, abbr_arr)
            
            if len(sentence_present) > 0:
                masked_sent = replace_keywords(s, variations, abbr)
                if f'({abbr})' in masked_sent: 
                    masked_sent = masked_sent.replace(f'({abbr})', '')
                data_array.append({'pmid': pmid, 'sentence': s, 'masked_sentence': masked_sent, 'abbreviation': abbr, 'full_spell': FS}) 
            elif len(text_present) > 0 and abbr_present:
                data_array.append({'pmid': pmid, 'sentence': s, 'masked_sentence': s, 'abbreviation': abbr, 'full_spell': FS}) 

df = pd.DataFrame(data_array)


print(f'Length of the dataset: {len(df)}')

df.to_csv('./sentences_final.csv', index=False)