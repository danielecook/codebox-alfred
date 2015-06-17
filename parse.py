#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import base64
from pprint import pprint as pp

"""

Very special thanks to Dorian Alcacer-Labrador (http://www.alcacer.de)
for providing a script that acted as the backbone for writing this one below.

"""


def b64(q):
    return base64.b64decode(q)

def idref(item, single = False):
    idrefs = item.get('idrefs')
    if single == False:
        if idrefs is not None:
            return str(idrefs).strip().split(" ")
        else:
            return []
    else:
        if idrefs is not None:
            return str(item.get('idrefs')).strip().split(" ")[0]
        else:
            return ""

class snippets():

    def __init__(self, file):
        self._file = file
        self._tagobjects = dict()
        self._assetobjects = dict()
        self._snippetobjects = dict()
        self._listobjects = dict()
        self._folderobjects = dict()

    def parse(self):
        tree = ET.parse(self._file)
        root = tree.getroot()
        for child in root._children:
            childtype = child.attrib.get('type')
            if childtype == "ASSET":
                 self._parseAsset(child)
            elif childtype == "SNIPPET":
                self._parseSnippet(child)
            elif childtype == "TAG":
                self._parseTag(child)
            elif childtype == "LIST":
                self._parseList(child)
            elif childtype == "FOLDER":
                self._parseFolder(child)
            else:
                pass

    def _parseAsset(self, asset):
        """
        parses and decodes an asset-tag
        0.1 id, content
        <object type="ASSET" id="z116">
            <attribute name="sort" type="int32">-1</attribute>
            <attribute name="path" type="string">Asset.java</attribute>
            <attribute name="content" type="binary">LyoqCiAgICAgKiBXcml0ZXMgYW4gYnl0ZSBhcnJheSBpbnRvIGEgZmlsZS4KICAgICAqIEBwYXJh
            bSBkYXRhIERhdGEgdGhhdCBzaG91bGQgYmUgd3JpdHRlbiBpbnRvIGEgZmlsZS4KICAgICAqIEBwYXJhbSBmaWxlbmFtZSBUaGUgZmlsZSwgdGhhdCBzaG91bGQgYmUgdXNlZC4KICAgICAqIEB0aHJvd3MgSU9FeGNlcHRpb24KICAgICAqLwogICAgcHVibGljIHN0YXRpYyB2b2lkIHdyaXRlQnl0ZTJGaWxlKGJ5dGVbXSBkYXRhLCBTdHJpbmcgZmlsZW5hbWUpIHRocm93cyBJT0V4Y2VwdGlvbiB7CiAgICAgICAgT3V0cHV0U3RyZWFtIG91dCA9IG5ldyBGaWxlT3V0cHV0U3RyZWFtKGZpbGVuYW1lKTsKICAgICAgICBvdXQud3JpdGUoZGF0YSk7CiAgICAgICAgb3V0LmNsb3NlKCk7CiAgICB9
            </attribute>
            <relationship name="snippet" type="1/1" destination="SNIPPET" idrefs="z113"></relationship>
        </object>
        """
        asset_id = asset.attrib.get('id')
        self._assetobjects[asset_id] = {}
        for child in asset._children:
            if child.tag == "attribute":
                # attribute tags
                attributeType = child.attrib.get("name")
                if attributeType == 'content':
                    encoded = child.text
                    if encoded is not None:
                        self._assetobjects[asset_id]["content"] = b64(encoded)
            elif child.tag == 'relationship':
                attributeType = child.attrib.get("name")
                if attributeType == "snippet":
                    self._assetobjects[asset_id]["snippet_id"] = child.attrib.get("idrefs")


    def _parseSnippet(self, snippet):
        """
        parses a snippet-tag
        0.1 id, assetes, tags
        <object type="SNIPPET" id="z108">
            <attribute name="name" type="string">.gitignore</attribute>
            <attribute name="modified" type="date">336046917.00164198875427246094</attribute>
            <attribute name="locked" type="bool">0</attribute>
            <relationship name="list" type="1/1" destination="LIST" idrefs="z114"></relationship>
            <relationship name="assets" type="0/0" destination="ASSET" idrefs="z107"></relationship>
            <relationship name="tags" type="0/0" destination="TAG"></relationship>
        </object>
        """
        snippid = snippet.attrib.get('id')
        self._snippetobjects[snippid] = {}
        for child in snippet._children:
            if child.tag == "attribute":
                # attribute tags
                attributeType = child.attrib.get("name")
                if attributeType == 'name':
                    self._snippetobjects[snippid]["title"] = child.text
            elif child.tag == 'relationship':
                # relationship-tag
                attributeType = child.attrib.get("name")
                if attributeType == 'list':
                    # list relationship
                    self._snippetobjects[snippid]["lists"] = idref(child)
                elif attributeType == 'assets':
                    # assets relationship
                    self._snippetobjects[snippid]["assets"] = idref(child, True)
                elif attributeType == 'tags':
                    # tags relationships
                    self._snippetobjects[snippid]["tags"] = idref(child)

    def _parseTag(self, tag):
        """
        parses a tag-tag :)
        0.1 id and content
        <object type="TAG" id="z106">
            <attribute name="name" type="string">gitignore</attribute>
            <relationship name="snippets" type="0/0" destination="SNIPPET"></relationship>
        </object>
        """
        tagid = tag.attrib.get('id')
        self._tagobjects[tagid] = {}
        for child in tag._children:
            if child.tag == "attribute":
                # attribute tags
                self._tagobjects[tagid]["name"] = child.text
            elif child.tag == 'relationship':
                # relationship tags
                self._tagobjects[tagid]["snippets"] = idref(child)

    def _parseList(self, list):
        """
        <object type="LIST" id="z118">
            <attribute name="sort" type="int16">0</attribute>
            <attribute name="name" type="string">s</attribute>
            <attribute name="expanded" type="bool">0</attribute>
            <relationship name="parent" type="1/1" destination="FOLDER" idrefs="z107"></relationship>
            <relationship name="children" type="0/0" destination="FOLDER"></relationship>
            <relationship name="snippets" type="0/0" destination="SNIPPET" idrefs="z120"></relationship>
        </object>
        """
        listid = list.attrib.get('id')
        self._listobjects[listid] = {}
        self._listobjects[listid]["id"] = listid
        self._listobjects[listid]["type"] = "list"
        for child in list._children:
            if child.tag == "attribute":
                attributeType = child.attrib.get("name")
                if attributeType == 'name':
                    self._listobjects[listid]["name"] = child.text
            elif child.tag == 'relationship':
                # relationship tags
                attributeType = child.attrib.get("name")
                if attributeType == "parent":
                    self._listobjects[listid]["parent"] = idref(child)
                elif attributeType == "children":
                    self._listobjects[listid]["children"] = idref(child)


    def _parseFolder(self, folder):
        """
        object type="FOLDER" id="z229">
            <attribute name="sort" type="int16">7</attribute>
            <attribute name="name" type="string">java</attribute>
            <attribute name="expanded" type="bool">1</attribute>
            <relationship name="parent" type="1/1" destination="FOLDER"></relationship>
            <relationship name="children" type="0/0" destination="FOLDER" idrefs="z223 z222 z333 z228"></relationship>
        </object>
        """
        folderid = folder.attrib.get('id')
        self._folderobjects[folderid] = {}
        self._folderobjects[folderid]["id"] = folderid
        self._folderobjects[folderid]["type"] = "folder"
        for child in folder._children:
            if child.tag == "attribute":
                # attribute tags
                attributeType = child.attrib.get("name")
                if attributeType == 'name':
                    self._folderobjects[folderid]["name"] = child.text
            elif child.tag == 'relationship':
                attributeType = child.attrib.get("name")
                if attributeType == "parent":
                    self._folderobjects[folderid]["parent"] = idref(child)
                elif attributeType == "children":
                    self._folderobjects[folderid]["children"] = idref(child)

    def list_snippets(self):
        for k,snippet in self._snippetobjects.items():
            # Fetch asset
            try:
                snippet["content"] = self._assetobjects[snippet["assets"]]["content"]
                del snippet["assets"]
            except:
                snippet["content"] = ""
            # Fetch tag
            snippet["tags"] = [self._tagobjects[x]["name"] for x in snippet["tags"]]
            # Fetch lists
            snippet["lists"] = [self._listobjects[x]["name"] for x in snippet["lists"]]
            # Fetch folders
            #snippet["folders"] = [self._folderobjects[x]["name"] for x in snippet["lists"]]

        return [v for k,v in self._snippetobjects.items()]

    def list_tags(self):
        """ returns tag and associated snippets """
        for k,tag in self._tagobjects.items():
            tag["count"] = len(tag["snippets"])
        return [v for k,v in self._tagobjects.items()]

    def unique_folder_name(self, folder_name):
        # Determine if folder name is unique
        return len([x for x in self._folderobjects.values() if x["name"] == folder_name]) == 1

    def unique_list_name(self, list_name):
        # Determine if list name is unique
        return len([x for x in self._listobjects.values() if x["name"] == list_name]) == 1

    def get_folder_items(self, folder, use_id = False):
        if use_id == False:
            try:
                folder_id = [x for x in self._folderobjects.values() if x["name"] == folder][0]["id"]
            except:
                return []
        folder_items = [x for x in self._folderobjects.values() if folder_id in x["parent"]]
        # Add counts
        list_items = [x for x in self._listobjects.values() if folder_id in x["parent"]]
        return folder_items + list_items

    def get_list_items(self, list_id, use_id = False):
        if use_id == False:
            try:
                list_id = [x["id"] for x in self._listobjects.values() if list_id == x["name"]][0]
            except:
                return []
        list_items = [x for x in self._snippetobjects.values() if list_id in x["lists"]]
        for snippet in list_items:
            try:
                snippet["content"] = self._assetobjects[snippet["assets"]]["content"]
                del snippet["assets"]
            except:
                snippet["content"] = ""
            # Fetch tag
            snippet["tags"] = [self._tagobjects[x]["name"] for x in snippet["tags"]]
            # Fetch lists
            snippet["lists"] = [self._listobjects[x]["name"] for x in snippet["lists"]]
        return list_items


