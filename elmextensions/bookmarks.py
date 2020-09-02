'''
Python module to read recently-used.xbel file into a dict like object
'''
import os
import xml.etree.ElementTree as et


# pylint: disable=too-few-public-methods
class Bookmarks(object):
    '''
    Bookmarks Class representing recently-used.xbel file_name file_path data.
    '''
    def __init__(self, path=None):
        if not path:
            path = os.path.expanduser('~/.local/share/recently-used.xbel')
        self.path = path
        self.dict = {}
        try:
            tree = et.parse(path)
            root = tree.getroot()
            self.walk_items(root)
        except IOError:
            pass

    def __repr__(self):
        return str(self.dict)

    def __getitem__(self, key):
        return self.dict[key]

    def walk_items(self, elem):
        '''Walk xml tree'''
        for child in elem:
            try:
                if elem.tag == 'bookmark':
                    ref = elem.attrib['href']
                    # Strip off the protocol
                    prefix = ref.find('://') + 7
                    name = os.path.split(ref[prefix:])[1]
                    # It seems protocols other than file can end up in this list
                    #   such as recent://
                    # I am skipping these
                    if 'file' in ref:
                        path = ref.split("file://")[1]
                        if os.path.isfile(path):
                            self.dict[name.replace('%20', ' ')] = path.replace('%20', ' ')
            except KeyError:
                pass

            self.walk_items(child)


if __name__ == "__main__":
    RECENT = Bookmarks()
    print(RECENT["test.txt"])
