from library_system import *
from datetime import datetime, timedelta

# Khởi tạo hệ thống
library = LibraryService()

# === CÁC LỚP QUẢN LÝ MENU ===
class MenuManager:
    @staticmethod
    def show_guest_menu():
        print("\n" + "="*50)
        print("HE THONG QUAN LY THU VIEN - KHACH")
        print("="*50)
        print("1. Tim sach")
        print("2. Xem danh sach sach")
        print("3. Dang ky thanh vien")
        print("4. Dang nhap")
        print("5. Quen mat khau")
        print("0. Thoat")
        print("="*50)

    @staticmethod
    def show_member_menu(user_name):
        print("\n" + "="*50)
        print(f"THU VIEN - Chao {user_name}")
        print("="*50)
        print("1. Tim sach")
        print("2. Xem danh sach sach") 
        print("3. Muon sach")
        print("4. Tra sach") 
        print("5. Dat truoc sach")
        print("6. Gia han sach")
        print("7. Xem phieu muon cua toi")
        print("8. Quan ly thong tin ca nhan")
        print("9. Dang xuat")
        print("="*50)

    @staticmethod
    def show_librarian_menu(user_name):
        print("\n" + "="*50)
        print(f"THU VIEN - Thu Thu {user_name}")
        print("="*50)
        print("1. Tim sach")
        print("2. Xem danh sach sach")
        print("3. Muon sach")
        print("4. Tra sach")
        print("5. Xem danh sach nguoi dung")
        print("6. Xem tat ca phieu muon")
        print("7. Xem thong ke")
        print("8. Quan ly sach")
        print("9. Gui nhac nho")
        print("10. Dang xuat")
        print("="*50)

# === CÁC LỚP XỬ LÝ CHỨC NĂNG ===
class AuthHandler:
    @staticmethod
    def register_member(library):
        print("\nDANG KY THANH VIEN")
        name = input("Ho ten: ").strip()
        email = input("Email: ").strip()
        
        if any(u.email == email for u in library.users):
            print("Email da duoc dang ky!")
            return
        
        password = AuthHandler._get_valid_password()
        
        date_of_birth = input("Ngay sinh (YYYY-MM-DD): ").strip()
        gender = input("Gioi tinh: ").strip()
        address = input("Dia chi: ").strip()
        phone = input("So dien thoai: ").strip()
        
        user_id = f"M{len([u for u in library.users if u.role == 'member']) + 1:03d}"
        new_member = Member(user_id, name, email, password, 
                           date_of_birth=date_of_birth,
                           gender=gender,
                           address=address,
                           phone=phone)
        
        success, message = library.register_user(new_member)
        print(message)
        if success:
            print(f"The thu vien cua ban: {new_member.library_card}")

    @staticmethod
    def _get_valid_password():
        while True:
            password = input("Mat khau (toi da 6 ky tu): ").strip()
            if len(password) > 6:
                print("Mat khau toi da 6 ky tu! Xin nhap lai")
            else:
                return password

    @staticmethod
    def login(library):
        print("\nDANG NHAP")
        email = input("Email: ").strip()
        password = input("Mat khau: ").strip()
        
        success, message = library.login(email, password)
        print(message)
        if success:
            print(f"Chao mung {library.current_user.name}!")

    @staticmethod
    def forgot_password_flow(library):
        email = input("Nhap email da dang ky: ").strip()
        success, message = library.forgot_password(email)
        print(message)

        if success:
            verification_code = input("Nhap ma xac nhan tu email: ").strip()
            new_password = AuthHandler._get_valid_password()
            success, message = library.reset_password(email, verification_code, new_password)
            print(message)

class BookHandler:
    @staticmethod
    def search_books(library):
        print("\nTIM SACH")
        print("(Enter de bo qua)")
        isbn = input("Nhap ISBN: ").strip()
        title = input("Nhap tieu de: ").strip()
        author = input("Nhap tac gia: ").strip()
        subject = input("Nhap chu de: ").strip()
        
        books = library.find_books(isbn=isbn, title=title, author=author, subject=subject)
        print(f"\nTim thay {len(books)} sach:")
        for i, book in enumerate(books, 1):
            print(f"{i}. {book}")

    @staticmethod
    def show_books(library):
        print("\nDANH SACH SACH")
        for i, book in enumerate(library.books, 1):
            print(f"{i}. {book}")

class MemberHandler:
    @staticmethod
    def borrow_book(library):
        print("\nMUON SACH")
        available_books = [b for b in library.books if b.is_available()]
        if not available_books:
            print("Hien khong co sach nao co san!")
            return
        
        for i, book in enumerate(available_books, 1):
            print(f"{i}. {book}")
        
        try:
            book_choice = int(input("\nChon so thu tu sach: ")) - 1
            if 0 <= book_choice < len(available_books):
                book = available_books[book_choice]
                success, message = library.borrow_book(book.isbn)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def return_book(library):
        print("\nTRA SACH")
        my_active_loans = [loan for loan in library.loans 
                          if loan.member.email == library.current_user.email 
                          and not loan.is_returned]
        
        if not my_active_loans:
            print("Ban khong co sach nao dang muon!")
            return
        
        print("Danh sach sach dang muon:")
        for i, loan in enumerate(my_active_loans, 1):
            fine = loan.calculate_fine()
            fine_info = f" - Phi tre: ${fine}" if fine > 0 else ""
            print(f"{i}. {loan}{fine_info}")
        
        try:
            choice = int(input("\nChon so thu tu sach de tra: ")) - 1
            if 0 <= choice < len(my_active_loans):
                loan = my_active_loans[choice]
                success, message = library.member_return_book(loan.book.isbn)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def make_reservation(library):
        print("\nDAT TRUOC SACH")
        borrowed_books = [b for b in library.books if not b.is_available()]
        if not borrowed_books:
            print("Tat ca sach deu co san, khong can dat truoc!")
            return
        
        for i, book in enumerate(borrowed_books, 1):
            print(f"{i}. {book}")
        
        try:
            book_choice = int(input("\nChon so thu tu sach: ")) - 1
            if 0 <= book_choice < len(borrowed_books):
                book = borrowed_books[book_choice]
                success, message = library.make_reservation(book.isbn, library.current_user.email)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def renew_loan(library):
        print("\nGIA HAN SACH")
        my_active_loans = [loan for loan in library.loans 
                          if loan.member.email == library.current_user.email 
                          and not loan.is_returned]
        
        if not my_active_loans:
            print("Ban khong co sach nao dang muon!")
            return
        
        print("Danh sach sach dang muon:")
        for i, loan in enumerate(my_active_loans, 1):
            can_renew = loan.renewal_count < 2
            renew_status = "Co the gia han" if can_renew else "Da het luot gia han"
            print(f"{i}. {loan} - {renew_status}")
        
        try:
            choice = int(input("\nChon so thu tu sach de gia han: ")) - 1
            if 0 <= choice < len(my_active_loans):
                loan = my_active_loans[choice]
                success, message = library.renew_loan(loan.loan_id, library.current_user.email)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def show_my_loans(library):
        print(f"\nLICH SU MUON SACH CUA {library.current_user.name}")
        my_loans = [loan for loan in library.loans if loan.member.email == library.current_user.email]
        
        active_loans = [loan for loan in my_loans if not loan.is_returned]
        returned_loans = [loan for loan in my_loans if loan.is_returned]
        
        if active_loans:
            print("\nDANG MUON:")
            for i, loan in enumerate(active_loans, 1):
                fine = loan.calculate_fine()
                fine_info = f" - Phi tre: ${fine}" if fine > 0 else ""
                renew_info = f" - Da gia han {loan.renewal_count}/2 lan"
                print(f"  {i}. {loan}{fine_info}{renew_info}")
        else:
            print("\nDang muon: Khong co")
        
        if returned_loans:
            print("\nDA TRA:")
            for i, loan in enumerate(returned_loans, 1):
                print(f"  {i}. {loan}")
        
        print(f"\nTHONG KE:")
        print(f"  • Sach dang muon: {len(active_loans)}/{library.current_user.max_books}")
        print(f"  • Sach da tra: {len(returned_loans)}")
        overdue_count = len([loan for loan in active_loans if loan.is_overdue()])
        if overdue_count > 0:
            print(f"  Sach tre han: {overdue_count}")

    @staticmethod
    def manage_profile(library):
        print(f"\nTHONG TIN CA NHAN - {library.current_user.name}")
        user = library.current_user
        
        while True:
            print("\nTHONG TIN HIEN TAI:")
            print(f"1. Ho ten: {user.name}")
            print(f"2. Email: {user.email} (khong the thay doi)")
            print(f"3. Ngay sinh: {user.date_of_birth}")
            print(f"4. Gioi tinh: {user.gender}")
            print(f"5. Dia chi: {user.address}")
            print(f"6. So dien thoai: {user.phone}")
            print(f"7. The thu vien: {user.library_card}")
            print(f"8. Quay lai")
            
            choice = input("\nChon thong tin can chinh sua (1-8): ").strip()
            
            if choice == '1':
                new_name = input(f"Nhap ho ten moi [{user.name}]: ").strip()
                if new_name:
                    success, message = user.update_profile(name=new_name)
                    print(message)
            
            elif choice == '2':
                print("Email khong the thay doi!")
            
            elif choice == '3':
                new_dob = input(f"Nhap ngay sinh moi (YYYY-MM-DD) [{user.date_of_birth}]: ").strip()
                if new_dob:
                    success, message = user.update_profile(date_of_birth=new_dob)
                    print(message)
            
            elif choice == '4':
                new_gender = input(f"Nhap gioi tinh moi [{user.gender}]: ").strip()
                if new_gender:
                    success, message = user.update_profile(gender=new_gender)
                    print(message)
            
            elif choice == '5':
                new_address = input(f"Nhap dia chi moi [{user.address}]: ").strip()
                if new_address:
                    success, message = user.update_profile(address=new_address)
                    print(message)
            
            elif choice == '6':
                new_phone = input(f"Nhap so dien thoai moi [{user.phone}]: ").strip()
                if new_phone:
                    success, message = user.update_profile(phone=new_phone)
                    print(message)
            
            elif choice == '7':
                print(f"The thu vien: {user.library_card}")
            
            elif choice == '8':
                break
            
            else:
                print("Lua chon khong hop le!")

class LibrarianHandler:
    @staticmethod
    def borrow_book_for_member(library):
        print("\nMUON SACH (Chi thu thu)")
        if not library.current_user or library.current_user.role != "librarian":
            print("Chi thu thu moi co the muon sach!")
            return
        
        available_books = [b for b in library.books if b.is_available()]
        members = [u for u in library.users if u.role == "member"]
        
        print("Danh sach sach co san:")
        for i, book in enumerate(available_books, 1):
            print(f"{i}. {book}")
        
        print("\nDanh sach thanh vien:")
        for i, member in enumerate(members, 1):
            print(f"{i}. {member.name} ({member.email})")
        
        try:
            book_choice = int(input("\nChon so thu tu sach: ")) - 1
            member_choice = int(input("Chon so thu tu thanh vien: ")) - 1
            
            if 0 <= book_choice < len(available_books) and 0 <= member_choice < len(members):
                book = available_books[book_choice]
                member = members[member_choice]
                success, message = library.borrow_book(book.isbn, member.email)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def return_book_for_member(library):
        print("\nTRA SACH (Chi thu thu)")
        if not library.current_user or library.current_user.role != "librarian":
            print("Chi thu thu moi co the tra sach!")
            return
        
        active_loans = [loan for loan in library.loans if not loan.is_returned]
        if not active_loans:
            print("Khong co sach nao dang duoc muon!")
            return
        
        print("Danh sach phieu muon dang hoat dong:")
        for i, loan in enumerate(active_loans, 1):
            print(f"{i}. {loan}")
        
        try:
            choice = int(input("\nChon so thu tu phieu muon de tra: ")) - 1
            if 0 <= choice < len(active_loans):
                loan = active_loans[choice]
                success, message = library.return_book(loan.loan_id)
                print(message)
            else:
                print("Lua chon khong hop le!")
        except ValueError:
            print("Vui long nhap so!")

    @staticmethod
    def show_users(library):
        print("\nDANH SACH NGUOI DUNG")
        for user in library.users:
            print(f"• {user}")

    @staticmethod
    def show_all_loans(library):
        print("\nDANH SACH PHIEU MUON")
        active_loans = [loan for loan in library.loans if not loan.is_returned]
        returned_loans = [loan for loan in library.loans if loan.is_returned]
        
        print("Dang muon:")
        for loan in active_loans:
            print(f"  • {loan}")
        
        print("\nDa tra:")
        for loan in returned_loans:
            print(f"  • {loan}")

    @staticmethod
    def show_stats(library):
        print("\nTHONG KE HE THONG")
        stats = library.get_stats()
        for key, value in stats.items():
            print(f"• {key.replace('_', ' ').title()}: {value}")

class BookManagementHandler:
    @staticmethod
    def add_book(library):
        print("\nTHEM SACH MOI")
        title = input("Tieu de: ").strip()
        author = input("Tac gia: ").strip()
        subject = input("Chu de: ").strip()
        publication_year = input("Nam xuat ban: ").strip()
        isbn = input("ISBN: ").strip()
        total_copies = input("So luong (mac dinh 1): ").strip()
        location = input("Vi tri: ").strip()
        
        if not total_copies:
            total_copies = 1
        else:
            try:
                total_copies = int(total_copies)
            except ValueError:
                print("So luong phai la so!")
                return
        
        new_book = Book(isbn, title, author, int(publication_year), subject, total_copies, location)
        success, message = library.add_book(new_book)
        print(message)

    @staticmethod
    def edit_book(library):
        print("\nCHINH SUA SACH")
        print("Danh sach sach:")
        for i, book in enumerate(library.books, 1):
            print(f"{i}. ISBN: {book.isbn} - '{book.title}' by {book.author}")
        
        isbn = input("\nNhap ISBN cua sach can sua: ").strip()
        book = next((b for b in library.books if b.isbn == isbn), None)
        if not book:
            print("Khong tim thay sach!")
            return
        
        print(f"\nThong tin hien tai cua '{book.title}':")
        print(f"  ISBN: {book.isbn}")
        print(f"  Tieu de: {book.title}")
        print(f"  Tac gia: {book.author}")
        print(f"  Chu de: {book.subject}")
        print(f"  Nam xuat ban: {book.year}")
        print(f"  So luong: {book.total_copies}")
        print(f"  Vi tri: {book.location}")
        
        print("\nNhap thong tin moi (Enter de giu nguyen):")
        new_title = input(f"Tieu de [{book.title}]: ").strip()
        new_author = input(f"Tac gia [{book.author}]: ").strip()
        new_subject = input(f"Chu de [{book.subject}]: ").strip()
        new_year = input(f"Nam xuat ban [{book.year}]: ").strip()
        new_copies = input(f"So luong [{book.total_copies}]: ").strip()
        new_location = input(f"Vi tri [{book.location}]: ").strip()
        
        updates = {}
        if new_title: updates['title'] = new_title
        if new_author: updates['author'] = new_author
        if new_subject: updates['subject'] = new_subject
        if new_year: 
            try:
                updates['year'] = int(new_year)
            except ValueError:
                print("Nam xuat ban phai la so!")
                return
        if new_copies:
            try:
                updates['total_copies'] = int(new_copies)
                if int(new_copies) < book.total_copies:
                    book.available_copies = max(0, book.available_copies - (book.total_copies - int(new_copies)))
                else:
                    book.available_copies += (int(new_copies) - book.total_copies)
            except ValueError:
                print("So luong phai la so!")
                return
        if new_location: updates['location'] = new_location
        
        if updates:
            success, message = library.edit_book(isbn, **updates)
            print(message)
        else:
            print("Khong co thay doi nao!")

    @staticmethod
    def remove_book(library):
        print("\nXOA SACH")
        print("Danh sach sach:")
        for i, book in enumerate(library.books, 1):
            print(f"{i}. ISBN: {book.isbn} - '{book.title}' by {book.author}")
        
        isbn = input("\nNhap ISBN cua sach can xoa: ").strip()
        book = next((b for b in library.books if b.isbn == isbn), None)
        if not book:
            print("Khong tim thay sach!")
            return
        
        active_loans = [loan for loan in library.loans if loan.book.isbn == isbn and not loan.is_returned]
        if active_loans:
            print("Khong the xoa sach dang duoc muon!")
            return
        
        active_reservations = [r for r in library.reservations if r.book.isbn == isbn and r.is_active]
        if active_reservations:
            print("Khong the xoa sach dang co dat truoc!")
            return
        
        print(f"\nBan co chac muon xoa sach '{book.title}'?")
        print(f"    Tac gia: {book.author}")
        print(f"    ISBN: {book.isbn}")
        confirm = input("\nNhap 'YES/NO' de xac nhan xoa/khong xoa: ").strip()
        
        if confirm == 'YES':
            library.books.remove(book)
            print(f"Sach '{book.title}' da duoc xoa thanh cong!")
        else:
            print("Da huy thao tac xoa!")

    @staticmethod
    def manage_books(library):
        print("\nQUAN LY SACH")
        print("1. Them sach moi")
        print("2. Chinh sua sach")
        print("3. Xoa sach")
        print("4. Quay lai")
        
        choice = input("Chon chuc nang (1-4): ").strip()
        
        if choice == '1':
            BookManagementHandler.add_book(library)
        elif choice == '2':
            BookManagementHandler.edit_book(library)
        elif choice == '3':
            BookManagementHandler.remove_book(library)
        elif choice == '4':
            return
        else:
            print("Lua chon khong hop le!")

    @staticmethod
    def send_reminders(library):
        print("\nGUI NHAC NHO HAN TRA SACH")
        upcoming_loans = []
        for loan in library.loans:
            if not loan.is_returned and not loan.is_overdue():
                days_until_due = (loan.due_date - datetime.now()).days
                if 0 <= days_until_due <= 2:
                    upcoming_loans.append(loan)
        
        if not upcoming_loans:
            print("Khong co sach nao sap het han!")
            return
        
        print(f"\nGUI NHAC NHO CHO {len(upcoming_loans)} THANH VIEN:")
        
        for i, loan in enumerate(upcoming_loans, 1):
            days_until_due = (loan.due_date - datetime.now()).days
            
            if days_until_due == 0:
                status = "HAN TRA HOM NAY"
            elif days_until_due == 1:
                status = "Con 1 ngay"
            else:
                status = f"Con {days_until_due} ngay"
                
            print(f"  {i}. {loan.member.name}")
            print(f"     Sach: '{loan.book.title}'")
            print(f"     Han tra: {loan.due_date.strftime('%d/%m/%Y')} - {status}")
            print()
        
        print(f"Da gui nhac nho cho {len(upcoming_loans)} thanh vien!")

# === DỮ LIỆU MẪU ===
def load_sample_data(library):
    sample_books = [
        Book("001", "Python Programming", "John Smith", 2023, "Programming", 3, "Shelf A1"),
        Book("002", "Data Science", "Jane Doe", 2022, "Science", 2, "Shelf B2"),
        Book("003", "To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", 1, "Shelf C3"),
        Book("004", "1984", "George Orwell", 1949, "Fiction", 2, "Shelf C4"),
        Book("005", "Effective Python", "Brett Slatkin", 2019, "Programming", 2, "Shelf A2")
    ]

    sample_users = [
        Member("M001", "John Doe", "john@email.com", "123456"),
        Member("M002", "Jane Smith", "jane@email.com", "234567"), 
        Member("M003", "Bob Johnson", "bob@email.com", "345678"),
        Librarian("L001", "Admin User", "admin@email.com", "admin1")
    ]

    for book in sample_books:
        library.add_book(book)

    for user in sample_users:
        library.register_user(user)

    print("THU VIEN DA SAN SANG!")

# === VÒNG LẶP CHÍNH ===
def main():
    load_sample_data(library)
    
    while True:
        if not library.current_user:
            MenuManager.show_guest_menu()
            choice = input("\nChon chuc nang (0-5): ").strip()
            
            if choice == '1':
                BookHandler.search_books(library)
            elif choice == '2':
                BookHandler.show_books(library)
            elif choice == '3':
                AuthHandler.register_member(library)
            elif choice == '4':
                AuthHandler.login(library)
            elif choice == '5':
                AuthHandler.forgot_password_flow(library)
            elif choice == '0':
                break
            else:
                print("Lua chon khong hop le!")
        
        elif library.current_user.role == "member":
            MenuManager.show_member_menu(library.current_user.name)
            choice = input("\nChon chuc nang (1-9): ").strip()

            if choice == '1':
                BookHandler.search_books(library)
            elif choice == '2':
                BookHandler.show_books(library)
            elif choice == '3':
                MemberHandler.borrow_book(library)
            elif choice == '4':
                MemberHandler.return_book(library)
            elif choice == '5':
                MemberHandler.make_reservation(library)
            elif choice == '6':
                MemberHandler.renew_loan(library)
            elif choice == '7':
                MemberHandler.show_my_loans(library)
            elif choice == '8':
                MemberHandler.manage_profile(library)
            elif choice == '9':
                library.logout()
                print("Da dang xuat!")
            else:
                print("Lua chon khong hop le!")
        
        else:  # Librarian
            MenuManager.show_librarian_menu(library.current_user.name)
            choice = input("\nChon chuc nang (0-10): ").strip()
    
            if choice == '1':
                BookHandler.search_books(library)
            elif choice == '2':
                BookHandler.show_books(library)
            elif choice == '3':
                LibrarianHandler.borrow_book_for_member(library)
            elif choice == '4':
                LibrarianHandler.return_book_for_member(library)
            elif choice == '5':
                LibrarianHandler.show_users(library)
            elif choice == '6':
                LibrarianHandler.show_all_loans(library)
            elif choice == '7':
                LibrarianHandler.show_stats(library)
            elif choice == '8':
                BookManagementHandler.manage_books(library)
            elif choice == '9':
                BookManagementHandler.send_reminders(library)
            elif choice == '10':
                library.logout()
                print("Da dang xuat!")
            elif choice == '0':
                break
            else:
                print("Lua chon khong hop le!")
        
        input("\nNhan Enter de tiep tuc...")

if __name__ == "__main__":
    main()