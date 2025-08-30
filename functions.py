# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 07:46:38 2025

@author: Jegou
"""
#Stories get incremented in crescent order.
#if 12 exists, the next one will be 13 (not 19)
import os
import random
#from upstash_redis import Redis

path_to_stories = 'stories'
n_sentences = 3


def load_file(name = '1'):
    path = convert_name_to_path(name)
    with open(path, mode = 'r', encoding="utf-8") as f:
        text = f.read()
    return text

def split_text(name = '1', text = None):
    if name is not None:
        a = load_file(name = str(name))
    elif text is not None:
        a = text
    else:
        print('No text found')
        a = 'Alea jacta est.'
    case = 2
    #case = 2 : only dots
    #case = 3 : only dots and exclamation marks
    #case = 4 : only dots and question marks
    #case = 6 : dots, exclamation marks and question marks
    if '!' in a:
        case +=1
    if '?' in a:
        case = case*2
    #print(case)
    a_split = []
    a_split_dot = a.split('.')
    #(a_split_dot)
    if case == 2:
        a_split = a_split_dot
    if case == 3:
        for a in a_split_dot:
            a_tmp = a.split('!')
            for i,f in enumerate(a_tmp):
                if len(a_tmp)>1 and i<len(a_tmp)-1:
                    a_split.append(f+'!')
                else:
                    a_split.append(f)
                    
    #I split the sentences and add a question mark at the end of the splitted ones
    elif case == 4:
        for a in a_split_dot:
            a_tmp = a.split('?')
            for i,f in enumerate(a_tmp):
                if len(a_tmp)>1 and i<len(a_tmp)-1:
                    a_split.append(f+'?')
                else:
                    a_split.append(f)
                    
    #I split the sentences and add a question/exclamation mark at the end of the splitted ones
    elif case == 6:
        a_split_tmp = []
        for a in a_split_dot:
            a_tmp = a.split('!')
            for i,f in enumerate(a_tmp):
                if len(a_tmp)>1 and i<len(a_tmp)-1:
                    a_split_tmp.append(f+'!')
                else:
                    a_split_tmp.append(f)
                    
        for a in a_split_tmp:
            a_tmp = a.split('?')
            for i,f in enumerate(a_tmp):
                if len(a_tmp)>1 and i<len(a_tmp)-1:
                    a_split.append(f+'?')
                else:
                    a_split.append(f)
    else:
        print(f'Unknown case number, weird file at path: {name}')
    return a_split
    
def get_n_sentences(name = '1', text = None):
    a_split = split_text(name = name, text = text)
    return len(a_split)


def get_last_sentences(name = '1', text = None, n_sentences = n_sentences):
    a_split = split_text(name = name, text = text)
    #I get the two last sentences of the list
    #Parsed in reverse and remove any return to line
    to_return = []
    cpt= 0
    for f in reversed(a_split):
        #At least 5 character in the sentence 
        if (len(f) > 4) and (cpt < n_sentences):
            to_return.append(f)
            cpt += 1
    return list(reversed(to_return))

def get_all_filenames(path = path_to_stories):
    all_files = [f.split('.')[0] for f in os.listdir(path)]
    #print(all_files)
    if len(all_files) >= 9**9:
        print('All stories have been written')
    return all_files

def check_layer_np1(name = '0000000001'):
    #Check if file xxxx9 of layer n+1 exists in files list
    name = int(name)*10 + 9
    name_to_check = str(name).zfill(10)
    all_files = get_all_filenames()
    if name_to_check in all_files:
        is_full = True
    else:
        is_full = False
    return is_full
    
def select_file(name = 0):
    #Stories number can go from 0 to 9 for one layer.
    #there is only one 1.txt stories
    #then it goes 10, 11, ... 19. 100, 101, ... 109; 190, 191, ..., 199.
    #maximum number is 1999999999 (1 and nine 9 after)

    #check that the n+1 layer is not already full (#i.e. if the name ends by a 9, return an error)

    name_str = str(name).zfill(10)
    #print(name_str)
    all_files = get_all_filenames()
    
    #Select a random file
    if int(name) == 0:
        is_full = True
        while is_full == True:
            rand_name = random.choice(all_files)
            #Check that the layer n + 1 is not already full of stories
            #print(rand_name)
            is_full = check_layer_np1(rand_name)
        #selected_file = os.path.join(path_to_stories,rand_name.zfill(10) +'.txt')
        selected_file = rand_name

    #Select a precise story
    elif name_str in all_files:
        is_full = check_layer_np1(name)
        if is_full:
            print('This story is already full, selecting a random one')
            while is_full == True:
                rand_name = random.choice(all_files)
                #Check that the layer n + 1 is not already full of stories
                is_full = check_layer_np1(rand_name)
            #selected_file = os.path.join(path_to_stories,rand_name.zfill(10) +'.txt')
            selected_file = rand_name
        else:
            #selected_file = os.path.join(path_to_stories,name_str + '.txt')
            selected_file = name_str + '.txt'
    else:
        print('Unknown file name, returning a random one')
        is_full = True
        while is_full == True:
            rand_name = random.choice(all_files)
            #Check that the layer n + 1 is not already full of stories
            is_full = check_layer_np1(rand_name)
        #selected_file = os.path.join(path_to_stories,rand_name.zfill(10) +'.txt')
        selected_file = rand_name
    return selected_file

def convert_name_to_path(name = '1'):
    return os.path.join(path_to_stories,str(name).zfill(10) +'.txt')

def write_file(name = 1, text = 'Une océan infinie'):
    #Here we assume that the name selection phase prevent any selection of a wrong file 
    #(i.e. layer n+1 already full)
    
    #We have to find the new name, layer n+1, last story
    all_files = get_all_filenames()
    
    #We loop over all potential names and stop when one does not exist yet
    new_names = [str(int(name)*10+i).zfill(10) for i in range(10)]
    #print(new_names)
    for n in new_names:
        if n not in all_files:
            new_name = convert_name_to_path(n)
            break
    #print(new_name)
    #Write the text in the newfile
    #Just in case the file already exists, we append at the end
    with open(new_name, mode = 'a', encoding="utf-8") as f:
        f.write(text)
    
#name = '1'
#sf = select_file(0)
#print(sf)
#print(get_last_sentences())
#text = 'Salut la team. Ceci est un test ? Je sais pas trop. Peut etre que ça marche pas en fait !'
#write_file(sf, text)
