# -*- coding: utf-8 -*-
from _category import Category


class CatBody(Category):
    """
    Implementation of the category graph detection
    """

    def __init__(self):
        """
        Public Attributes:
            | *name* (str): the name of the category

        Returns:
            | instance of the gdetection object

        """
        self.name = 'Graph detection'
        # we need Category to load its algorithms after self.name assignment
        Category.__init__(self, self.name)


if __name__ == '__main__':
    pass
