from . import CACHE_DIR
import pickle
import os


class PickleList:

    def getDir(self):
        global CACHE_DIR
        return CACHE_DIR

    @classmethod
    def load(cls, name):
        """
        Use to load or create a new PickleList.

        name: Used to identify the pickled list.
        Don't forget to save!!!
        """
        global CACHE_DIR

        myList = cls()

        myList.name = name
        myList.dumpFile = os.path.join(CACHE_DIR, myList.name + ".p")

        if os.path.exists(myList.dumpFile):
            myList._inner_list = pickle.load(open(myList.dumpFile, "rb"))
        else:
            myList._inner_list = list()

        return myList

    def save(self):
        pickle.dump(self._inner_list, open(self.dumpFile, "wb"))

        print("saved", self.name)

    def getName(self):
        return self.name

    # Standard list methodes

    def __getitem__(self, index):
        return self._inner_list[index]

    def __delitem__(self, index):
        self._inner_list.__delitem__(index)

    def __setitem__(self, index, value):
        self._inner_list.__setitem__(index, value)

    def __len__(self):
        return self._inner_list.__len__()

    def append(self, object_):
        self._inner_list.append(object_)

    def extend(self, iterable):
        self._inner_list.extend(iterable)

    def insert(self, index, value):
        self._inner_list.insert(index, value)

    def reverse(self):
        self._inner_list.reverse()

    def pop(self, *index):
        return self._inner_list.pop(*index)
