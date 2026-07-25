# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 07:46:38 2025

@author: Jegou
"""
#Stories get incremented in crescent order.
#if 12 exists, the next one will be 13 (not 19)
import os
import random
from collections import defaultdict
import zipfile
from upstash_redis import Redis

db_url = os.getenv("TEST")
redis = Redis(url="https://super-minnow-34706.upstash.io", token=db_url)

#path_to_stories = 'stories'
N_SENTENCES = 3 # minimal nb of sentences
NB_SUB_STORIES = 10 # number of sub_stories in a story

def load_file(name = '1'):
    path = convert_name_to_path(name)
    text = redis.get(path)
    #with open(path, mode = 'r', encoding="utf-8") as f:
    #    text = f.read()
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
    
def get_N_SENTENCES(name = '1', text = None):
    a_split = split_text(name = name, text = text)
    return len(a_split)


def get_last_sentences(name = '1', text = None, N_SENTENCES = N_SENTENCES):
    a_split = split_text(name = name, text = text)
    #I get the two last sentences of the list
    #Parsed in reverse and remove any return to line
    to_return = []
    cpt= 0
    for f in reversed(a_split):
        #At least 5 character in the sentence 
        if (len(f) > 4) and (cpt < N_SENTENCES):
            to_return.append(f)
            cpt += 1
    return list(reversed(to_return))
"""
def get_all_filenames(path = path_to_stories):
    all_files = [f.split('.')[0] for f in os.listdir(path)]
    #print(all_files)
    if len(all_files) >= 9**9:
        print('All stories have been written')
    return all_files
"""
def get_all_filenames():
    keys = redis.keys("*")
    return keys

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
            selected_file = name_str
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
    #return os.path.join(path_to_stories,str(name).zfill(10) +'.txt')
    return str(name).zfill(10)

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
    redis.set(new_name, text)
    #with open(new_name, mode = 'a', encoding="utf-8") as f:
    #    f.write(text)
    
#name = '1'
#sf = select_file(0)
#print(sf)
#print(get_last_sentences())
#text = 'Salut la team. Ceci est un test ? Je sais pas trop. Peut etre que ça marche pas en fait !'
#write_file(sf, text)

### Story Building

def build_tree(names: list[str], accept_longer_stories: bool=True):
    """
    Create a tree from a list of names.

    Parameters
    ----------
    names: list of str
        List of the names of the stories.
        Should be at least ``NB_SUB_STORIES`` length.
        First story is '00...1', sub_story is '00...10', etc.
    accept_longer_stories: bool, default=True
        Wether to accept stories with more than ``NB_SUB_STORIES``
        or not.
    
    Returns
    -------
    tree: dict of set
        A dictionnary, where the keys are the names of the father nodes
        (previous sub-story) and values are sets containing the names
        of the children (following suib-stories).
    """
    sorted_names = sorted(names, reverse=True) # names ordered from 19...9, 0...01
    tree = defaultdict(set)
    # Remove the starting story (no father)
    if sorted_names[-1] == '0'*(NB_SUB_STORIES-1)+'1':
        sorted_names.pop()
    # is_leaf = {n: True for n in sorted_names}
    level = 1 # begin at 1st sub-story
    while level <= NB_SUB_STORIES and len(sorted_names) > 0:
        current = sorted_names.pop() # "oldest", node
        
        if level+1 < NB_SUB_STORIES: # not last stories
            if current[-1-(level+1)] == '1': # pass to next level
                level += 1
                sorted_names.append(current) # put it back in the list
                continue
        else: # reached last stories: 1...X
            if len(current) > NB_SUB_STORIES: # exit loop if story of 11 sub-stories
                level += 1
                sorted_names.append(current)
                break
        
        father = '0'+current[:-1]
        tree[father].add(current)
    

    if accept_longer_stories and len(sorted_names) > 0:
        while len(sorted_names) > 0:
            current = sorted_names.pop()
            if len(current) > level+1: # next level
                level += 1
                sorted_names.append(current)
                continue

            father = current[:-1]
            tree[father].add(current)

    return tree
    
def write_stories(stories: dict[str, str], tree, separator: str='\n'+'*'*10+'\n')->dict[str,str]:
    """
    Write all stories, as {leaf_id: story}.

    Parameters
    ----------
    stories: dict
        Dictionnary of stories (from stories_from_XXX).
    tree: dict
        Tree defining the father-child relationship between stories,
        obtained by ``build_tree``.
    separator: str, default='\n'+'*'*10+'\n'
        Separator between individual small stories. 
        Used to visually separate them in a global story.

    Return
    ------
    res: dict
        Dictionnary of leaf stories, i.e concatenation of all the sub-stories
        up to the last sub-story written, for each branch.
        Organized as {leaf_id: story string}
    """
    sorted_ids = sorted(list(stories.keys()), reverse=False) # first text to last text
    res = defaultdict(str)
    for id in sorted_ids:
        children = tree[id]
        for child in children:
            res[child] = res[id] +separator + stories[child]
        # not leaf: has child OR its child are longer stories than it should
        if len(children) != 0 and len(next(iter(children)))==NB_SUB_STORIES: 
            del res[id] # remove the father

    return res


def stories_from_folder(folder: str)->dict[str,str]:
    """
    Generate stories dict from a folder of stories.

    Parameters
    ----------
    folder: str
        Path to the folder of stories.
    
    Returns
    -------
    stories: dict
        Dictionnary with the stories, organised as
        {story_id: story string}
    """
    stories = {}
    for filename in os.listdir(folder):
        _, story_id = os.path.split(filename) # extract story id, e.g '000...1'
        with open(filename, 'r') as file:
            stories[story_id] = file.readlines()
    return stories

def stories_from_zip(filepath: str)->dict[str,str]:
    """
    Generate stories dict from a folder of stories.

    Parameters
    ----------
    filepath: str
        Path to the zipfile of stories.
    
    Returns
    -------
    stories: dict
        Dictionnary with the stories, organised as
        {story_id: story string}
    """
    stories = {}
    if not filepath.endswith('.zip'):
        filepath += '.zip'
    with zipfile.ZipFile(filepath, "r") as zipf:
        for id in zipf.namelist():
            if id.endswith('.txt'): # not path to story file
                _, story_id = os.path.split(id)
                story_id = os.path.splitext(story_id)[0] # extract story id, e.g '000...1'
                content = zipf.read(id)
                stories[story_id] = content.decode()
        
    return stories

def build_stories(folder: str=None, zipfile: str=None, separator: str='\n'+'*'*10+'\n'):
    """
    Returns two dictionnaries:
    - one with ended stories
    - one with the remaining leaf stories

    Parameters
    ----------
    folder: str, optionnal
        Path to the folder containing stories.
    zipfile: str, optionnal
        Path of the zip file containing stories.
    separator: str, default='\n'+'*'*10+'\n'
        Separator between individual small stories. 
        Used to visually separate them in a global story.
    
    Returns
    -------
    ended_stories: dict
        Dictionnary of ended stories, organized as {story_id: story string}.
    in_progress_stories: dict
        Dictionnary of stories in progress, organized as {story_id: story string}.
    """
    # Extract stories from folder
    # files = {name: content}
    if folder is not None:
        stories = stories_from_folder(folder)
    elif zipfile is not None:
        stories = stories_from_zip(zipfile)
    else:
        raise ValueError('folder and zipfile cannot be None simultaneously.')
    
    # Build tree
    tree = build_tree(list(stories.keys()))

    # Build leaf stories
    leaf_stories = write_stories(stories, tree, separator)
    leaf_id = list(leaf_stories.keys())
    ended_stories = {}
    in_progress_stories = {}
    for id in leaf_id: 
        leaf_story = leaf_stories[id]
        if id[0] != '0': # ended_story
            ended_stories[id] = leaf_story
        else: # in progress
            in_progress_stories[id] = leaf_story

    return ended_stories, in_progress_stories


if __name__=='__main__':
    import json 
    folder = os.getcwd()
    ended_stories, in_progress_stories = build_stories(zipfile=folder + '\\txt_files.zip')

    # Save files as json
    with open(folder + '\\processed_stories\\ended_stories.json', 'w') as file:
        json.dump(ended_stories, file, indent=4, ensure_ascii=False)
    with open(folder + '\\processed_stories\\in_progress_stories.json', 'w') as file:
        json.dump(in_progress_stories, file, indent=4, ensure_ascii=False)

    # Save ended stories as txt
    for id, story in ended_stories.items():
        with open(folder + f'\\processed_stories\\{id}.txt', 'w', encoding='utf-8') as file:
            file.write(story)


### TO DO ###
# - add the root story to the written stories !!
# - visualisation tool to navigate through the stories