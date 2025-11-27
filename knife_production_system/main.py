from database import db
from ui.main_window import MainWindow


def main():
    db.initialize_database()
    app = MainWindow(db)
    app.mainloop()


if __name__ == "__main__":
    main()
