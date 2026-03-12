import customtkinter as CTk

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

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)


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

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)


        self.title_lable = CTk.CTkLabel(master=self, text="Регистрация", font=("", 26, "bold"), anchor=CTk.CENTER)
        self.title_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

        self.first_name_lable = CTk.CTkLabel(master=self, text="Имя:", font=("", 15), anchor=CTk.CENTER)
        self.first_name_lable.place(anchor=CTk.E, relx=0.2, rely=0.3)

        self.first_name_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.first_name_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

        self.last_name_lable = CTk.CTkLabel(master=self, text="Фамилия:", font=("", 15), anchor=CTk.CENTER)
        self.last_name_lable.place(anchor=CTk.E, relx=0.2, rely=0.4)

        self.last_name_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.last_name_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.4)

        self.email_lable = CTk.CTkLabel(master=self, text="Почта:", font=("", 15), anchor=CTk.CENTER)
        self.email_lable.place(anchor=CTk.E, relx=0.2, rely=0.5)

        self.email_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.email_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

        self.password_lable = CTk.CTkLabel(master=self, text="Пароль:", font=("", 15), anchor=CTk.CENTER)
        self.password_lable.place(anchor=CTk.E, relx=0.2, rely=0.6)

        self.password_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.password_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.6)

class Login_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.title_lable = CTk.CTkLabel(master=self, text="Вход в аккаунт", font=("", 26, "bold"), anchor=CTk.CENTER)
        self.title_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

        self.email_lable = CTk.CTkLabel(master=self, text="Почта:", font=("", 15), anchor=CTk.CENTER)
        self.email_lable.place(anchor=CTk.E, relx=0.2, rely=0.4)

        self.email_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.email_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.4)

        self.password_lable = CTk.CTkLabel(master=self, text="Пароль:", font=("", 15), anchor=CTk.CENTER)
        self.password_lable.place(anchor=CTk.E, relx=0.2, rely=0.5)

        self.password_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.password_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        CTk.set_default_color_theme("dark-blue")

        self.frames = {}
        for F in (Main_window, Search_window, Account_window, Register_window, Login_window):
            frame = F(master=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.show_frame(Main_window)

    def show_frame(self, frame_class):
        # Достаем нужный фрейм из словаря
        frame = self.frames[frame_class]
        # tkraise() поднимает этот фрейм поверх остальных
        frame.tkraise()

app = App()
app.mainloop()