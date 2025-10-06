class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.value = key

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
        else:
            self._insert_recursively(self.root, key)

    def _insert_recursively(self, current_node, key):
        if key < current_node.value:
            if current_node.left is None:
                current_node.left = Node(key)
            else:
                self._insert_recursively(current_node.left, key)
        else:
            if current_node.right is None:
                current_node.right = Node(key)
            else:
                self._insert_recursively(current_node.right, key)

    def inorder_traversal(self):
        return self._inorder_recursively(self.root)

    def _inorder_recursively(self, node):
        result = []
        if node:
            result.extend(self._inorder_recursively(node.left))   # Traverse left subtree
            result.append(node.value)                              # Visit the root
            result.extend(self._inorder_recursively(node.right))  # Traverse right subtree
        return result

    def find_max(self):
        return self._find_max_recursively(self.root)

    def _find_max_recursively(self, node):
        if node is None:
            return None  # Tree is empty
        while node.right is not None:  # Traverse to the rightmost node
            node = node.right
        return node.value  # Return the maximum value found

    def find_min(self):
        return self._find_min_recursively(self.root)

    def _find_min_recursively(self, node):
        if node is None:
            return None  # Tree is empty
        while node.left is not None:  # Traverse to the rightmost node
            node = node.left
        return node.value  # Return the maximum value found

    def delete(self, key):
        self.root = self._delete_recursively(self.root, key)

    def _delete_recursively(self, node, key):
        if node is None:
            print(f"{key} not found in bst")
            return node  # Key not found

        # Traverse the tree
        if key < node.value:
            node.left = self._delete_recursively(node.left, key)
        elif key > node.value:
            node.right = self._delete_recursively(node.right, key)
        else:
            # Node with only one child or no child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            min_larger_node = self._find_min(node.right)
            node.value = min_larger_node.value  # Copy the inorder successor's value
            node.right = self._delete_recursively(node.right, min_larger_node.value)  # Delete the inorder successor

        return node

    def _find_min(self, node):
        current = node
        while current.left is not None:  # Go to the leftmost leaf
            current = current.left
        return current

# Example usage
bst = BinarySearchTree()
values_to_insert = [2, 1, 3]
for value in values_to_insert:
    bst.insert(value)

print("Printing values of binary search tree in inorder traversal:")
inorder_values = bst.inorder_traversal()
print(inorder_values)  # Output: [6, 10, 14, 15, 20, 25, 60]

max_value = bst.find_max()
print("Maximum value in the binary search tree:", max_value)  # Output: 60

min_value = bst.find_min()
print("Minimum value in the binary search tree:", min_value)  # Output: 60

bst.delete(4)
print("Inorder traversal after deleting 1:")
print(bst.inorder_traversal())