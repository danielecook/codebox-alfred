#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow
from parse import *
import re
from collections import Counter
import difflib

__version__ = '0.1'

def main(wf):
    arg = ' '.join(wf.args)
    codebox_location = wf.stored_data('codebox_location')
    log.debug(codebox_location)
    if codebox_location is None:
        wf.add_item("You must set the codebox xml location with 'cb_src'", icon="info.png",uid=u"set source")
        wf.send_feedback()
    snp = snippets(codebox_location)
    snp.parse()
    snps = snp.list_snippets()
    item_name = arg.split(" ")[0].strip()
    search = ' '.join(arg.split()[1:])
    log.debug(item_name)
    log.debug(search)

    if arg == "":
        results = [1] # Set dummy result
        wf.add_item("Tags", autocomplete = "#", icon="tag.png", uid=u"cb:Tags")

        # Add top folders
        top_folders = [x for x in snp._folderobjects.values() if x["parent"] == []]
        top_lists = [x for x in snp._listobjects.values() if x["parent"] == []]
        for i in top_folders:
            if snp.unique_folder_name(i["name"]):
                autocomplete = "F:" + i["name"] + " "
            else:
                autocomplete = "F-ID:" + i["id"] + " "
            wf.add_item(i["name"], autocomplete = autocomplete, icon="folder.png")
        for i in top_lists:
            if snp.unique_list_name(i["name"]):
                autocomplete = "L:" + i["name"] + " "
            else:
                autocomplete =  "L-ID:" + i["id"] + ""
            wf.add_item(i["name"], autocomplete = autocomplete, icon="list.png")

    #
    # TAGS
    #

    elif item_name in ["#" + x["name"] for x in snp._tagobjects.values()]:
        """ Select Tag items and search """
        results = [x for x in snps if item_name[1:] in x["tags"]]
        if search != "":
            results = wf.filter(search, results, key= lambda x: x["title"])
        for i in results:
            wf.add_item(i["title"], i["content"].strip(), arg = i["content"] + " ", valid=True, icon="snippet.png")

    elif arg.startswith("#"):
        results = snp.list_tags()
        if arg != "#" and search.strip() != "":
            results = wf.filter(search, results, key= lambda x: x["name"])
        for i in results:
            tag_name = i["name"]
            count = i["count"]
            # Filter further
            wf.add_item("{tag_name} ({count})".format(**locals()), autocomplete = "#" + tag_name + " ", icon="tag.png")


    #
    # Folders
    #

    elif arg.startswith("F:") == True or arg.startswith("F-ID:"):
        if arg.startswith("F:"):
            item_name = item_name.replace("F:","")
            results = snp.get_folder_items(item_name)
        elif arg.startswith("F-ID:"):
            item_name = item_name.replace("F-ID::","")
            results = snp.get_folder_items(item_name,True)
        if search != "":
            results = wf.filter(search, results, key= lambda x: x["name"])
        for i in results:
            name_or_id = i["name"]
            use_id = ""
            if i["type"] == "folder":
                unique = snp.unique_folder_name(i["name"])
            elif i["type"] == "list":
                unique = snp.unique_list_name(i["name"])
            if unique == False:
                use_id = "-ID"
                name_or_id = i["id"]
            wf.add_item(i["name"], autocomplete = i["type"][0].upper() + use_id + ":" + name_or_id + " ", icon=i["type"] + ".png")

    #
    # List
    #
    elif arg.startswith("L:") == True or arg.startswith("L-ID:"):
        # Why parse again?
        snp.parse()
        if arg.startswith("L:"):
            item_name = item_name.replace("L:","")
            results = snp.get_list_items(item_name)
        elif arg.startswith("L-ID:"):
            item_name = item_name.replace("L-ID:","")
            results = snp.get_list_items(item_name, True)
        if search != "":
            results = wf.filter(search, results, key= lambda x: x["title"])
        for i in results:
            wf.add_item(i["title"] , i["content"].strip(), arg = i["content"], valid=True, icon="snippet.png")




    else:
        # Search

        results = wf.filter(arg, snps, key= lambda x: x["title"] + ' '.join(x["tags"]) + " " + x["content"])
        for snp in results:
            wf.add_item(snp["title"] , snp["content"].strip(), arg = snp["content"], valid=True, icon="snippet.png")
    
    if len(results) == 0:
        wf.add_item("No Results Found", valid=True, icon="error.png")



    # Send output to Alfred
    #log.debug(wf.send_feedback())
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'danielecook/codebox-alfred',
        'version': __version__,
        'frequency': 7
        })
    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.start_update()
    log = wf.logger
    sys.exit(wf.run(main))

