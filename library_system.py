import hashlib
from datetime import datetime, timedelta
import uuid

class Book:
    def __init__(self, isbn, title, author, year, subject, copies=1, location=""):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.subject = subject
        self.total_copies = copies
        self.available_copies = copies
        self.location = location
    
    def is_available(self): return self.available_copies > 0
    def borrow_book(self): 
        if self.is_available():
            self.available_copies -= 1
            return True
        return False
    def return_book(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    def __str__(self): 
        status = "Available" if self.is_available() else "Borrowed"
        return f"ISBN: {self.isbn} - '{self.title}' by {self.author} - {status} - {self.available_copies}/{self.total_copies} copies"

class LibraryCard:
    def __init__(self, card_number):
        self.card_number = card_number
        self.issued_date = datetime.now()
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"Library Card #{self.card_number} - Issued: {self.issued_date.strftime('%Y-%m-%d')} - {status}"

class User:
    def __init__(self, user_id, name, email, password, date_of_birth="", gender="", address="", phone="", role="member"):
        
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.phone = phone
        self.date_joined = datetime.now()
        self.library_card = LibraryCard(user_id)

        if len(password) > 6:
            raise ValueError("Password must be maximum 6 characters")
    
    def verify_password(self, password): 
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def reset_password(self, new_password):
        if len(new_password) > 6:
            return False, "Password must be maximum 6 characters"
        self.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        return True, "Password reset successfully"
    
    def update_profile(self, **updates):
        """Cap nhat thong tin ca nhan"""
        allowed_fields = ['name', 'date_of_birth', 'gender', 'address', 'phone']
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        return True, "Cap nhat thong tin thanh cong"
    
    def __str__(self): 
        return f"{self.name} ({self.email}) - {self.role}"
   
class Member(User):
    def __init__(self, user_id, name, email, password, date_of_birth="", gender="", address="", phone=""):
        super().__init__(user_id, name, email, password, 
                        date_of_birth=date_of_birth,
                        gender=gender, 
                        address=address,
                        phone=phone,
                        role="member")
        self.max_books = 5
        self.current_loans = []
    
    def can_borrow_more(self): 
        return len(self.current_loans) < self.max_books

class Librarian(User):
    def __init__(self, user_id, name, email, password, date_of_birth="", gender="", address="", phone=""):
        super().__init__(user_id, name, email, password,
                        date_of_birth=date_of_birth,
                        gender=gender,
                        address=address, 
                        phone=phone,
                        role="librarian")

class Loan:
    def __init__(self, book, member, loan_days=14):
        self.loan_id = str(uuid.uuid4())[:8]
        self.book = book
        self.member = member
        self.borrow_date = datetime.now()
        self.due_date = self.borrow_date + timedelta(days=loan_days)
        self.return_date = None
        self.is_returned = False
        self.renewal_count = 0
    
    def is_overdue(self): return not self.is_returned and datetime.now() > self.due_date
    def calculate_fine(self, daily_fine=5000): 
        return (datetime.now() - self.due_date).days * daily_fine if self.is_overdue() else 0
    def return_book(self):
        self.is_returned = True
        self.return_date = datetime.now()
        self.book.return_book()
        if self in self.member.current_loans:
            self.member.current_loans.remove(self)
    
    def renew_loan(self, additional_days=14):
        """Gia han sach"""
        if not self.is_returned and self.renewal_count < 2:
            self.due_date += timedelta(days=additional_days)
            self.renewal_count += 1
            return True, f"Da gia han thanh cong. Ngay tra moi: {self.due_date.strftime('%Y-%m-%d')}"
        return False, "Khong the gia han"
    
    def __str__(self): 
        status = "Returned" if self.is_returned else "Active"
        overdue = " (OVERDUE)" if self.is_overdue() else ""
        return f"Loan #{self.loan_id}: {self.book.title} - Due: {self.due_date.strftime('%Y-%m-%d')} ({status}{overdue})"

class Reservation:
    def __init__(self, book, member):
        self.reservation_id = str(uuid.uuid4())[:8]
        self.book = book
        self.member = member
        self.reservation_date = datetime.now()
        self.expiry_date = self.reservation_date + timedelta(days=7)
        self.is_active = True
    
    def is_expired(self): return datetime.now() > self.expiry_date
    def __str__(self): 
        status = "Active" if self.is_active else "Inactive"
        expired = " (Expired)" if self.is_expired() else ""
        return f"Reservation #{self.reservation_id}: {self.book.title} - {status}{expired}"

class LibraryService:
    def __init__(self):
        self.books = []
        self.users = []
        self.loans = []
        self.reservations = []
        self.current_user = None
        self.verification_codes = {}
        self.load_librarians()

    def register_user(self, user):
        if hasattr(user, 'password') and len(user.password) > 6:
            return False, "Password must be maximum 6 characters"

        if any(u.email == user.email for u in self.users):
            return False, "Email already registered"
        self.users.append(user)
        return True, f"User {user.name} registered successfully"
    
    def load_librarians(self):
        try:
            with open('librarians.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        email, password, name = line.strip().split(',')
                        user_id = f"L{len([u for u in self.users if u.role == 'librarian']) + 1:03d}"
                        librarian = Librarian(user_id, name, email, password)
                        self.users.append(librarian)
            print("Da tai danh sach thu thu")
        except FileNotFoundError:
            print("Khong tim thay file librarians.txt")
        except Exception as e:
            print(f"Loi khi doc file: {e}")
        
    def login(self, email, password):
        user = next((u for u in self.users if u.email == email), None)
        if user and user.verify_password(password):
            self.current_user = user
            return True, f"Welcome back, {user.name}!"
        return False, "Invalid email or password"
    
    def logout(self):
        self.current_user = None
        return True, "Logged out successfully"
    
    def add_book(self, book):
        self.books.append(book)
        return True, f"Book '{book.title}' added successfully"
    
    def find_books(self, **kwargs):
        results = self.books
        if 'isbn' in kwargs and kwargs['isbn']: 
            results = [b for b in results if kwargs['isbn'].lower() in b.isbn.lower()]
        if 'title' in kwargs and kwargs['title']: 
            results = [b for b in results if kwargs['title'].lower() in b.title.lower()]
        if 'author' in kwargs and kwargs['author']: 
            results = [b for b in results if kwargs['author'].lower() in b.author.lower()]
        if 'subject' in kwargs and kwargs['subject']: 
            results = [b for b in results if kwargs['subject'].lower() in b.subject.lower()]
        return results
    
    def borrow_book(self, book_isbn, member_email=None):
        """Muon sach - cho phep ca thanh vien va thu thu"""
        if member_email is None:
            if not self.current_user or self.current_user.role != "member":
                return False, "Only members can borrow books for themselves"
            member_email = self.current_user.email
        elif not self.current_user:
            return False, "Please login to process borrowing"
        
        book = next((b for b in self.books if b.isbn == book_isbn), None)
        member = next((u for u in self.users if u.email == member_email and u.role == "member"), None)
        
        if not book: return False, "Book not found"
        if not book.is_available(): return False, "Book not available"
        if not member: return False, "Member not found"
        if not member.can_borrow_more(): return False, f"Cannot borrow more books (limit: {member.max_books})"
        
        if book.borrow_book():
            loan = Loan(book, member)
            self.loans.append(loan)
            member.current_loans.append(loan)
            return True, f"Book '{book.title}' borrowed successfully. Due: {loan.due_date.strftime('%Y-%m-%d')}"
        return False, "Borrow failed"
    
    def return_book(self, loan_id):
        loan = next((l for l in self.loans if l.loan_id == loan_id), None)
        if loan and not loan.is_returned:
            loan.return_book()
            fine = loan.calculate_fine()
            message = f"Book '{loan.book.title}' returned successfully"
            if fine > 0: message += f". Overdue fine: ${fine}"
            return True, message
        return False, "Return failed"
    
    def make_reservation(self, book_isbn, member_email):
        book = next((b for b in self.books if b.isbn == book_isbn), None)
        member = next((u for u in self.users if u.email == member_email and u.role == "member"), None)
        
        if not book: return False, "Book not found"
        if book.is_available(): return False, "Book is available for borrowing"
        
        reservation = Reservation(book, member)
        self.reservations.append(reservation)
        return True, f"Reservation for '{book.title}' created successfully"

    def renew_loan(self, loan_id, member_email):
        loan = next((l for l in self.loans if l.loan_id == loan_id), None)
        member = next((u for u in self.users if u.email == member_email), None)
        
        if not loan or not member:
            return False, "Khong tim thay thong tin muon sach"
        if loan.is_returned:
            return False, "Sach da duoc tra, khong the gia han"
        
        book_reservations = [r for r in self.reservations 
                           if r.book.isbn == loan.book.isbn 
                           and r.is_active 
                           and r.member.email != member_email]
        if book_reservations:
            return False, "Khong the gia han - sach da duoc dat truoc boi thanh vien khac"
        
        return loan.renew_loan()
    
    def member_return_book(self, book_isbn):
        """Thanh vien tu tra sach"""
        if not self.current_user or self.current_user.role != "member":
            return False, "Only members can return their own books"
        
        # Tim loan record chua tra cua thanh vien nay
        loan = next((l for l in self.loans 
                    if l.book.isbn == book_isbn 
                    and l.member.email == self.current_user.email 
                    and not l.is_returned), None)
        
        if not loan:
            return False, "No active loan found for this book"
        
        # Tra sach
        loan.return_book()
        fine = loan.calculate_fine()
        
        message = f"Book '{loan.book.title}' returned successfully"
        if fine > 0:
            message += f". Overdue fine: ${fine}"
        
        return True, message

    def forgot_password(self, email):
        user = next((u for u in self.users if u.email == email), None)
        if not user:
            return False, "This email is not registered in the system."
        
        verification_code = str(uuid.uuid4())[:6].upper()
        self.verification_codes[email] = verification_code
        print(f"Verification code sent to {email}: {verification_code}")
        return True, "Verification code sent to your email"
    
    def reset_password(self, email, verification_code, new_password):
        if email not in self.verification_codes:
            return False, "No password reset request found for this email"
        if self.verification_codes[email] != verification_code:
            return False, "Invalid verification code"
        if len(new_password) > 6:
            return False, "Password must maximum 6 characters"
        
        user = next((u for u in self.users if u.email == email), None)
        if user:
            user.reset_password(new_password)
            del self.verification_codes[email]
            return True, "Password reset successfully"
        return False, "User not found"

    def get_stats(self):
        return {
            'total_books': len(self.books),
            'total_users': len(self.users),
            'active_loans': len([l for l in self.loans if not l.is_returned]),
            'overdue_loans': len([l for l in self.loans if l.is_overdue()]),
            'active_reservations': len([r for r in self.reservations if r.is_active])
        }
    
    def add_new_book(self, title, author, subject, publication_year, isbn, total_copies=1, location=""):
        """Thu thu them sach moi"""
        if not self.current_user or self.current_user.role != "librarian":
            return False, "Only librarians can add books"
        
        # Kiem tra ISBN trung
        if any(b.isbn == isbn for b in self.books):
            return False, "Book with this ISBN already exists"
        
        new_book = Book(isbn, title, author, publication_year, subject, total_copies, location)
        self.books.append(new_book)
        return True, f"Book '{title}' added successfully"

    def edit_book(self, isbn, **updates):
        """Thu thu chinh sua thong tin sach"""
        if not self.current_user or self.current_user.role != "librarian":
            return False, "Only librarians can edit books"
        
        book = next((b for b in self.books if b.isbn == isbn), None)
        if not book:
            return False, "Book not found"
        
        # Kiem tra xem sach co dang duoc muon khong
        active_loans = [loan for loan in self.loans if loan.book.isbn == isbn and not loan.is_returned]
        if active_loans:
            return False, "Cannot edit book that is currently on loan"
        
        # Cap nhat thong tin
        allowed_fields = ['title', 'author', 'subject', 'publication_year', 'total_copies', 'location']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(book, field):
                setattr(book, field, value)
        
        return True, f"Book '{book.title}' updated successfully"

    def remove_book(self, isbn):
        """Thu thu xoa sach"""
        if not self.current_user or self.current_user.role != "librarian":
            return False, "Only librarians can remove books"
        
        book = next((b for b in self.books if b.isbn == isbn), None)
        if not book:
            return False, "Book not found"
        
        # Kiem tra xem sach co dang duoc muon khong
        active_loans = [loan for loan in self.loans if loan.book.isbn == isbn and not loan.is_returned]
        if active_loans:
            return False, "Cannot remove book that is currently on loan"
        
        # Kiem tra xem sach co duoc dat truoc khong
        active_reservations = [r for r in self.reservations if r.book.isbn == isbn and r.is_active]
        if active_reservations:
            return False, "Cannot remove book that has active reservations"
        
        self.books.remove(book)
        return True, f"Book '{book.title}' removed successfully"

    def get_all_loans(self):
        if not self.current_user or self.current_user.role != "librarian":
            return []
        return self.loans

    def send_due_date_reminders(self):
        if not self.current_user or self.current_user.role != "librarian":
            return False, "Only librarians can send reminders"
    
        upcoming_loans = []
        for loan in self.loans:
            if not loan.is_returned and not loan.is_overdue():
                days_until_due = (loan.due_date - datetime.now()).days
                if 0 <= days_until_due <= 2:  # Nhac nho truoc 2 ngay
                    upcoming_loans.append(loan)
    
        if not upcoming_loans:
            return True, "No reminders to send"
    
        print(f"\n GUI NHAC NHO CHO {len(upcoming_loans)} THANH VIEN:")
        for loan in upcoming_loans:
            days_until_due = (loan.due_date - datetime.now()).days
            print(f"  {loan.member.name}: '{loan.book.title}' - Con {days_until_due} ngay")
    
        return True, f"Sent {len(upcoming_loans)} reminders successfully"