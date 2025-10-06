class Book:
    def __init__(self, isbn, name, author):
        self.isbn = isbn
        self.name = name
        self.author = author


class Node:
    def __init__(self, book):
        self.book = book  # Store the Book object
        self.left = None
        self.right = None


class BookBST:
    def __init__(self):
        self.root = None

    def insert(self, isbn, name, author):
        new_book = Book(isbn, name, author)
        if self.root is None:
            self.root = Node(new_book)
        else:
            self._insert_recursively(self.root, new_book)

    def _insert_recursively(self, current_node, book):
        if book.isbn < current_node.book.isbn:
            if current_node.left is None:
                current_node.left = Node(book)
            else:
                self._insert_recursively(current_node.left, book)
        else:
            if current_node.right is None:
                current_node.right = Node(book)
            else:
                self._insert_recursively(current_node.right, book)

    def search(self, isbn):
        return self._search_recursively(self.root, isbn)

    def _search_recursively(self, current_node, isbn):
        if current_node is None or current_node.book.isbn == isbn:
            return current_node
        if isbn < current_node.book.isbn:
            return self._search_recursively(current_node.left, isbn)
        return self._search_recursively(current_node.right, isbn)

    def delete(self, isbn):
        self.root = self._delete_recursively(self.root, isbn)

    def _delete_recursively(self, node, isbn):
        if node is None:
            return node

        if isbn < node.book.isbn:
            node.left = self._delete_recursively(node.left, isbn)
        elif isbn > node.book.isbn:
            node.right = self._delete_recursively(node.right, isbn)
        else:  # Node with the value found
            # Node with only one child or no child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            min_larger_node = self._find_min(node.right)
            node.book = min_larger_node.book  # Copy the inorder successor's book
            node.right = self._delete_recursively(node.right, min_larger_node.book.isbn)  # Delete the inorder successor

        return node

    def _find_min(self, node):
        current = node
        while current.left is not None:  # Go to the leftmost leaf
            current = current.left
        return current

    def _find_max(self, node):
        current = node
        while current.right is not None:  # Go to the rightmost leaf
            current = current.right
        return current

    def find_min(self):
        if self.root is None:
            return None  # Tree is empty
        min_node = self._find_min(self.root)
        return min_node.book if min_node else None

    def find_max(self):
        if self.root is None:
            return None  # Tree is empty
        max_node = self._find_max(self.root)
        return max_node.book if max_node else None

    def inorder_traversal(self):
        books_in_order = []
        self._inorder_recursively(self.root, books_in_order)
        return books_in_order

    def _inorder_recursively(self, node, books_in_order):
        if node is not None:
            self._inorder_recursively(node.left, books_in_order)  # Traverse left subtree
            books_in_order.append(node.book)  # Visit the root (current book)
            self._inorder_recursively(node.right, books_in_order)  # Traverse right subtree


# Example usage
book_bst = BookBST()
book_bst.insert(9780134685991, "Effective Java", "Joshua Bloch")
book_bst.insert(9780134757592, "Clean Code", "Robert C. Martin")
book_bst.insert(9780134694740, "Design Patterns", "Erich Gamma")
book_bst.insert(9780135166307, "Introduction to Algorithms", "Thomas H. Cormen")

# Inorder traversal of the BST
books_sorted = book_bst.inorder_traversal()
print("Books in sorted order by ISBN:")
for book in books_sorted:
    print(f"ISBN: {book.isbn}, Title: {book.name}, Author: {book.author}")

# Search for a book by ISBN
found_book = book_bst.search(9780134685991)
if found_book:
    print(f"Book found: {found_book.book.name} by {found_book.book.author} (ISBN: {found_book.book.isbn})")
else:
    print("Book not found.")

# Find minimum and maximum books by ISBN
min_book = book_bst.find_min()
max_book = book_bst.find_max()

if min_book:
    print(f"Minimum Book: ISBN: {min_book.isbn}, Title: {min_book.name}, Author: {min_book.author}")
else:
    print("No minimum book found.")

if max_book:
    print(f"Maximum Book: ISBN: {max_book.isbn}, Title: {max_book.name}, Author: {max_book.author}")
else:
    print("No maximum book found.")

# Delete a book by ISBN
book_bst.delete(9780134757592)
print("Book with ISBN 9780134757592 deleted.")

# Inorder traversal of the BST
books_sorted = book_bst.inorder_traversal()
print("Books in sorted order by ISBN:")
for book in books_sorted:
    print(f"ISBN: {book.isbn}, Title: {book.name}, Author: {book.author}")