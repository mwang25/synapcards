from card_attr import CardAttr
from card_node import CardNode


class AuthorNode(CardNode):
    def __init__(self, name, count):
        super(AuthorNode, self).__init__(CardAttr.AUTHOR, name, count)
