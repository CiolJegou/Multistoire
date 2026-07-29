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
    
def write_stories(stories: dict[str, str], tree, separator: str='\n'+'*'*10+'\n', leaf_only: bool=True)->dict[str,str]:
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
    # Set initial (starting) sub-story
    first_story = '0'*(NB_SUB_STORIES-1)+'1'
    if sorted_ids[0] == first_story:
        res[first_story] = stories[first_story]
    else:
        res[first_story] = '-- INITIAL STORY --'
    # Propagate stories
    for id in sorted_ids:
        children = tree[id]
        for child in children:
            res[child] = res[id] +separator + stories[child]
        # not leaf: has child OR its child have too many sub-stories
        if leaf_only and len(children) != 0 and len(next(iter(children)))==NB_SUB_STORIES: 
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


def visualise(folder: str=None, zipfile: str=None, preview_length=300):
    if folder is not None:
        stories = stories_from_folder(folder)
    elif zipfile is not None:
        stories = stories_from_zip(zipfile)
    else:
        raise ValueError('folder and zipfile cannot be None simultaneously.')
    
    # Build tree
    tree = build_tree(list(stories.keys()))
    values = write_stories(stories, tree, leaf_only=False)
    app = ArbreInteractif(
        tree=tree,
        single_value=stories,
        complete_value=values,
        preview_length=preview_length
    )
    app.show()

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

    visualise(zipfile=folder + '\\txt_files.zip')


### TO DO ###
# - visualisation tool to navigate through the stories
