import customtkinter as CTk
import requests
from tkinter import messagebox

SERVER_URL = "http://127.0.0.1:8000"

class Session:
    current_user = None

    @classmethod
    def is_user(cls):
        if cls.current_user:
            return cls.current_user.get("role") == "CLIENT"
        return False
    
    @classmethod
    def is_admin(cls):
        if cls.current_user:
            return cls.current_user.get("role") == "ADMIN"
        return False

class Nav_plane(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.btn_main = CTk.CTkButton(master=self, text="Главная", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Main_window), anchor=CTk.CENTER)
        self.btn_main.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

        self.btn_account = CTk.CTkButton(master=self, text="Аккаунт", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Account_window), anchor=CTk.CENTER)
        self.btn_account.place(anchor=CTk.CENTER, relx=0.3, rely=0.5)

        self.btn_search = CTk.CTkButton(master=self, text="Поиск", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Search_window), anchor=CTk.CENTER)
        self.btn_search.place(anchor=CTk.CENTER, relx=0.7, rely=0.5)

class Main_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)


        self.welcome_lable = CTk.CTkLabel(master=self, text="Добро пожаловать!", font=("", 26, "bold"), anchor=CTk.CENTER)
        self.welcome_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

        self.status_lable = CTk.CTkLabel(master=self, text="Ваш статус: Classic", font=("", 17, "bold"), anchor=CTk.CENTER)
        self.status_lable.place(anchor=CTk.W, relx=0.2, rely=0.3)

        self.search_lable = CTk.CTkLabel(master=self, text="Давайте перейдём к поиску отелей!", font=("", 17, "bold"), anchor=CTk.CENTER)
        self.search_lable.place(anchor=CTk.W, relx=0.2, rely=0.4)

        self.search_btn = CTk.CTkButton(master=self, text="К поиску", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Search_window), anchor=CTk.CENTER)
        self.search_btn.place(anchor=CTk.W, relx=0.2, rely=0.5)

class Search_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

class Account_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller
        self.update_ui()

    def update_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        if Session.is_user():
            self.lable = CTk.CTkLabel(master=self, text=f"Добро пожаловать {Session.current_user.get('first_name')}!", font=("", 23, "bold"), anchor=CTk.CENTER)
            self.lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

        elif Session.is_admin():
            self.lable = CTk.CTkLabel(master=self, text=f"Добро пожаловать {Session.current_user.get('first_name')}!\n Вы админ!", font=("", 23, "bold"), anchor=CTk.CENTER)
            self.lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

        else:
            self.lable = CTk.CTkLabel(master=self, text="Вы ещё не вошли в аккаунт.\n Пожалуйста, выберите действае ниже", font=("", 23, "bold"), anchor=CTk.CENTER)
            self.lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

            self.button = CTk.CTkButton(master=self, text="Войти", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Login_window), anchor=CTk.CENTER)
            self.button.place(anchor=CTk.CENTER, relx=0.4, rely=0.4)

            self.button = CTk.CTkButton(master=self, text="Зарегистрироваться", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Register_window), anchor=CTk.CENTER)
            self.button.place(anchor=CTk.CENTER, relx=0.6, rely=0.4)

class Register_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

    def update_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.title_lable = CTk.CTkLabel(master=self, text="Регистрация", font=("", 26, "bold"), anchor=CTk.CENTER)
        self.title_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

        self.first_name_lable = CTk.CTkLabel(master=self, text="Имя:", font=("", 15), anchor=CTk.CENTER)
        self.first_name_lable.place(anchor=CTk.E, relx=0.2, rely=0.3)

        self.first_name_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.first_name_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

        self.last_name_lable = CTk.CTkLabel(master=self, text="Фамилия:", font=("", 15), anchor=CTk.CENTER)
        self.last_name_lable.place(anchor=CTk.E, relx=0.2, rely=0.4)

        self.last_name_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.last_name_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.4)

        self.email_lable = CTk.CTkLabel(master=self, text="Почта:", font=("", 15), anchor=CTk.CENTER)
        self.email_lable.place(anchor=CTk.E, relx=0.2, rely=0.5)

        self.email_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.email_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

        self.password_lable = CTk.CTkLabel(master=self, text="Пароль:", font=("", 15), anchor=CTk.CENTER)
        self.password_lable.place(anchor=CTk.E, relx=0.2, rely=0.6)

        self.password_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.password_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.6)

        self.btn_submit = CTk.CTkButton(master=self, text="Зарегистрироваться", font=("", 15, "bold"), command=self.register)
        self.btn_submit.place(anchor=CTk.CENTER, relx=0.5, rely=0.7)

    def register(self):
        data = {
            "first_name": self.first_name_textbox.get(),
            "last_name": self.last_name_textbox.get(),
            "email": self.email_textbox.get(),
            "password": self.password_textbox.get()
        }

        try:
            response = requests.post(f"{SERVER_URL}/register/", json=data)

            if response.status_code == 200:
                Session.current_user = response.json().get("user")
                self.controller.show_frame(Account_window)
            else:
                try:
                    error_data = response.json().get("detail")
                    self.error_lable = CTk.CTkLabel(master=self, text=f"{error_data}", font=("", 15), anchor=CTk.CENTER)
                    self.error_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.25)
                except ValueError:
                    error_msg = f"Критическая ошибка сервера ({response.status_code}).\n Ответ: {response.text}"
                    messagebox.showerror("Ошибка регистрации", error_msg)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Сервер недоступен. Запустите сервер!")

class Login_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

    def update_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.title_lable = CTk.CTkLabel(master=self, text="Вход в аккаунт", font=("", 26, "bold"), anchor=CTk.CENTER)
        self.title_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

        self.email_lable = CTk.CTkLabel(master=self, text="Почта:", font=("", 15), anchor=CTk.CENTER)
        self.email_lable.place(anchor=CTk.E, relx=0.2, rely=0.4)

        self.email_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.email_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.4)

        self.password_lable = CTk.CTkLabel(master=self, text="Пароль:", font=("", 15), anchor=CTk.CENTER)
        self.password_lable.place(anchor=CTk.E, relx=0.2, rely=0.5)

        self.password_textbox = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.password_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

        self.btn_submit = CTk.CTkButton(master=self, text="Войти", font=("", 15, "bold"), command=self.login)
        self.btn_submit.place(anchor=CTk.CENTER, relx=0.5, rely=0.6)

    def login(self):
        data = {
            "email": self.email_textbox.get(),
            "password": self.password_textbox.get()
        }

        try:
            response = requests.post(f"{SERVER_URL}/login/", json=data)

            if response.status_code == 200:
                Session.current_user = response.json().get("user")
                self.controller.show_frame(Account_window)
            else:
                try:
                    error_data = response.json().get("detail")
                    self.error_lable = CTk.CTkLabel(master=self, text=f"{error_data}", font=("", 15), anchor=CTk.CENTER)
                    self.error_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.35)
                except ValueError:
                    error_msg = f"Критическая ошибка сервера ({response.status_code}).\n Ответ: {response.text}"
                    messagebox.showerror("Ошибка входа", error_msg)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Сервер недоступен. Запустите сервер!")

class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        CTk.set_default_color_theme("dark-blue")

        self.frames = {}
        for F in (Main_window, Search_window, Account_window, Register_window, Login_window):
            frame = F(master=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.show_frame(Main_window)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        
        if hasattr(frame, "update_ui"):
            frame.update_ui()

        frame.tkraise()

app = App()
app.mainloop()