from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import nltk
import numpy as np
import pandas as pd
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from time import sleep
import json
import sys



##Uncomment if any of below package is missing
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')
# nltk.download('wordnet')


patterns="""
    NP: {<JJ>*<NN*>+}
    {<JJ>*<NN*><CC>*<NN*>+}
    {<NP><CC><NP>}
    {<RB><JJ>*<NN*>+}
    """

NPChunker = nltk.RegexpParser(patterns)

def prepare_text(input):
    sentences = nltk.sent_tokenize(input)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
#     print(sentences)
    sentences = [[word for word in sent if word!='i'] for sent in sentences]
#     print(sentences)
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    sentences = [NPChunker.parse(sent) for sent in sentences]
    return sentences


def parsed_text_to_NP(sentences):
    nps = []
    for sent in sentences:
        tree = NPChunker.parse(sent)
#         print(tree)
        for subtree in tree.subtrees():
            if subtree.label() == 'NP':
                t = subtree
                t = ' '.join(word for word, tag in t.leaves())
                nps.append(t)
    return nps


def sent_parse(input):
    sentences = prepare_text(input)
    nps = parsed_text_to_NP(sentences)
    return nps

def get_clean_sentence(text):
    """
    Converting text to lower case as in, converting "Hello" to  "hello" or "HELLO" to "hello".
    """
    wordnet_lemmatizer = WordNetLemmatizer()
    for c in string.punctuation:
        text = text.replace(c,' ')
    tokens = nltk.word_tokenize(text)
    words = [word for word in tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    words = [w.lower() for w in words if not w in stop_words]
    return ' '.join(words)

def updateRating(old_tuple,rating):
    old_rating, old_count = old_tuple
    new_rating = (old_rating*old_count + rating)/(old_count+1)
    return (new_rating, old_count+1)


def getDishes(reviews, word_list):
    result = []
    matching_cache = {}
    for review in tqdm(reviews):
        cleaned_review = get_clean_sentence(review)
        get_entities = sent_parse(review) + sent_parse(cleaned_review)
        get_unique_entities = set(get_entities)
        dishes_in_review = set([])
        for entity in get_unique_entities:
            dish = None
            if matching_cache.get(entity,0) == 0:
                match = process.extractOne(entity, word_list, scorer=fuzz.token_set_ratio)
                if match[1]>=70:
                    matching_cache[entity] = match[0]
                else:
                    matching_cache[entity] = None

            if matching_cache[entity] != None:
                dish = matching_cache[entity]
            
            if dish != None:
                dishes_in_review.add(dish)
            
        result.append(dishes_in_review)
    return result


def startProcess(filename):
    word_dict = {}
    word_list = pd.read_csv('food_list.csv', sep='\n',header=None,encoding='utf-8')
    #convert pandas dataframe to numpy object
    word_list = word_list.values
    word_list = np.asarray([str(word).replace('\\','').lower() for word in word_list])
    word_list = np.unique(word_list)
    word_list = np.asarray([word.replace('\\','').replace('\"','').replace('[','').replace(']','').replace("'",'') for word in word_list])

    df = pd.read_csv(filename)
    unwanted_cols = ['name','neighborhood','address', 'city', 'postal_code','latitude',
                    'longitude','stars_x','state', 'review_count','is_open','categories',
                    'review_id','user_id','date' ,'useful','funny','cool']
    try:
        df.drop(unwanted_cols,axis=1,inplace=True)
    except:
        pass
        
    matching_cache = {}
    df['Dishes'] = getDishes(df['text'].values, word_list)

    df.to_csv(filename[:-4]+'_output.csv',index=False)

    return



if __name__ == "__main__":
    # filename="sample.csv"
    filename = sys.argv[1]
    print(filename)
    startProcess(filename)