class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            p = p.parent
            level += 1
        return level

    def print_tree(self):
        print(' ' * self.get_level() + '|--', end='')
        print(self.data)
        if self.children:
            for child in self.children:
                child.print_tree()


def run():
    root = TreeNode('Electronics')
    laptop = TreeNode('Laptop')
    root.add_child(laptop)
    laptop.add_child(TreeNode('Mac'))
    laptop.add_child(TreeNode('Windows'))
    laptop.add_child(TreeNode('Linux'))

    tv = TreeNode('TV')
    root.add_child(tv)
    tv.add_child(TreeNode('LG'))
    tv.add_child(TreeNode('Samsung'))
    tv.add_child(TreeNode('Apple'))

    root.print_tree()


if __name__ == '__main__':
    run()
