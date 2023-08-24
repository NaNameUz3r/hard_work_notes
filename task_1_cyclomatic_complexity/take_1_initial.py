class Book:
    def __init__(self, book_id, title, author, genre, is_available) -> None:
        self.id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.is_available = is_available

class Library:
    def __init__(self):
        self.books = []

    def add_book(self, title, author, genre) -> None:
        new_book = Book(title, author, genre, True)
        self.books.append(new_book)
        return f"Added '{title}' by {author} to the library."

    def remove_book(self, title):
        for book in self.books:
            if book.title == title:
                self.books.remove(book)
                print(f"Removed '{title}' from the library.")
                return
        return f"Book '{title}' not found in the library."

    def manage_borrow_return(self, title, action):
        for book in self.books:
            if book.title == title:
                if action == "borrow":
                    if book.is_available:
                        print(f"Borrowing '{title}' by {book.author}.")
                        book.is_available = False
                    else:
                        print(f"Sorry, '{title}' is already borrowed.")
                    return
                elif action == "return":
                    if not book.is_available:
                        print(f"Returning '{title}'.")
                        book.is_available = True
                    else:
                        print(f"Error: '{title}' was not borrowed.")
                    return
        return f"Book '{title}' not found in the library."

    def search_books(self, search_type, keyword):
        matching_books = []
        for book in self.books:
            if search_type == "author" and keyword.lower() in book.author.lower():
                matching_books.append(book)
            elif search_type == "genre" and keyword.lower() in book.genre.lower():
                matching_books.append(book)
        return matching_books
