import uuid
import sqlite3

class Book:
    def __init__(self,
                 book_id: uuid,
                 title: str,
                 author: str,
                 genre: str,
                 is_available: bool) -> None:
        self.id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.is_available = is_available

class Library:
    def __init__(self):
        self.conn = sqlite3.connect(database='library.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS books
                         (id text, title text, author text, genre text, is_available bool)''')

    def _commit_changes(self):
        self.conn.commit()

    def add_book(self, title, author, genre) -> Book:
        book_id = str(uuid.uuid4())
        self.c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)",
                       (book_id, title, author, genre, True))
        self._commit_changes()
        return Book(book_id, title, author, genre, True)

    def remove_by_id(self, book_id) -> None:
        self.c.execute("DELETE FROM books WHERE id = ?",
                       __parameters=(book_id,))
        self._commit_changes()

    def get_book_by_title(self, title) -> Book | str:
        self.c.execute("SELECT * FROM books WHERE title = ?",
                       __parameters=(title,))
        row = self.c.fetchone()
        if row:
            return Book(*row)
        return f"No book with {title} found"

    def borrow_book(self, book) -> str:
        if book.is_available:
            self._set_availability(book.id, is_available=False)
            return f"Borrowing '{book.title}' by {book.author}."
        return f"Sorry, '{book.title}' is already borrowed."

    def return_book(self, book) -> None:
        if not book.is_available:
            self._set_availability(book.id, True)
            return f"Returning '{book.title}'."
        return f"Error: '{book.title}' was not borrowed."

    def _set_availability(self, book_id, is_available) -> None:
        self.c.execute("UPDATE books SET is_available = ? WHERE id = ?",
                       __parameters=(is_available, book_id))
        self._commit_changes()

    def search_books(self, search_type, keyword) -> list[Book]:
        query = "SELECT * FROM books WHERE {} LIKE ?".format(search_type)
        self.c.execute(query, ('%' + keyword.lower() + '%',))

        matching_books = [Book(*row) for row in self.c.fetchall()]
        return matching_books


# Example usage
# library = Library()
# book = library.add_book("Sample Title", "Sample Author", "Sample Genre")
# found_books = library.search_books("author", "Sample")
# for found_book in found_books:
#     print(f"'{found_book.title}' by {found_book.author} ({found_book.genre})")
