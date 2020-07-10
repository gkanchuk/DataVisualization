import pandas as pd
import numpy as np
import json
from os import listdir
from os.path import isfile, join

def updateRating(old_tuple,rating):
    old_rating, old_count = old_tuple
    new_rating = (old_rating*old_count + rating)/(old_count+1)
    return (new_rating, old_count+1)

def getFoodCount(business_ids, dish_lists, ratings):
    food_to_biz = {}
    food_count = {}
    for business_id, dish_list, rating in zip(business_ids, dish_lists, ratings):
        dish_list = dish_list.replace('{','').replace('\"','').replace('}','').replace(']','').replace("'",'').replace(",",'')
        dish_list = dish_list.split(' ')
        for dish in dish_list:
            temp = food_to_biz.setdefault(dish,{})
            temp[business_id] = updateRating(temp.setdefault(business_id,(0,0)),rating)
            food_to_biz[dish] = temp
            food_count[dish] = updateRating(food_count.setdefault(dish,(0,0)),rating)
            
    return food_to_biz, food_count


fileList = [f for f in listdir('.') if isfile(join('.', f)) if 'csv' in f]
for filename1 in fileList:
    print('starting '+ filename1)
    #filename1="sample_output.csv"
    df = pd.read_csv(filename1)
    food_to_biz, food_count = getFoodCount(df['business_id'].values,df['Dishes'].values,df['sentiment'].values)


    temp = []
    for key in food_count.keys():
        temp.append([key, food_count[key][1], food_count[key][0]])
    temp.sort(key=lambda x: (x[1],x[2]), reverse = True)
    food_count_df = pd.DataFrame(temp)
    # food_count = pd.DataFrame(food_count)
    food_count_df.rename(columns={0:'Dish',1:'Count',2:'Avg_Rating'}, inplace=True)
    food_count_df.to_csv(filename1[:-4]+'_food_count.csv',index=False)


    ##Sort food_to_biz based on food count and business_id list based on count
    temp = {}
    for dish in food_count_df['Dish'].values:
        temp1 = []
        business_dict = food_to_biz[dish]
        for b_id in business_dict.keys():
            temp1.append([b_id,business_dict[b_id][1],business_dict[b_id][0]])
        temp1.sort(key=lambda x: (x[1],x[2]), reverse = True)
        temp[dish] = temp1
        
    with open(filename1[:-4]+'_food_to_biz.json', 'w') as f:
        json.dump(temp,f)
