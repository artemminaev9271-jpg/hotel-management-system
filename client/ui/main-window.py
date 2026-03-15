import customtkinter as CTk
import requests
from tkinter import messagebox, filedialog
from PIL import Image
import io

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

        self.update_ui()

    def update_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.btn_main = CTk.CTkButton(master=self, text="Главная", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Main_window), anchor=CTk.CENTER)
        self.btn_main.place(anchor=CTk.CENTER, relx=0.5, rely=0.5)

        self.btn_account = CTk.CTkButton(master=self, text="Аккаунт", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Account_window), anchor=CTk.CENTER)
        self.btn_account.place(anchor=CTk.CENTER, relx=0.3, rely=0.5)

        self.btn_search = CTk.CTkButton(master=self, text="Поиск", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Search_window), anchor=CTk.CENTER)
        self.btn_search.place(anchor=CTk.CENTER, relx=0.7, rely=0.5)

        if Session.is_admin():
            self.btn_admin = CTk.CTkButton(master=self, text=("Администраторская"), font=("", 15, "bold"), command=lambda: self.controller.show_frame(Admin_window), anchor=CTk.CENTER)
            self.btn_admin.place(anchor=CTk.CENTER, relx=0.9, rely=0.5)

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

        self.search_frame = CTk.CTkFrame(self, fg_color="transparent")
        self.search_frame.place(relx=0.5, rely=0.15, anchor=CTk.CENTER)

        self.city_entry = CTk.CTkEntry(self.search_frame, placeholder_text="Введите город (например: Москва)", width=300)
        self.city_entry.pack(side=CTk.LEFT, padx=10)

        self.search_btn = CTk.CTkButton(self.search_frame, text="Найти отели", command=self.perform_search)
        self.search_btn.pack(side=CTk.LEFT)

        self.results_scroll_frame = CTk.CTkScrollableFrame(self, width=750, height=450)
        self.results_scroll_frame.place(relx=0.5, rely=0.6, anchor=CTk.CENTER)

        self.perform_search()

    def perform_search(self):
        city_query = self.city_entry.get().strip()
        
        params = {}
        if city_query:
            params["city"] = city_query

        try:
            response = requests.get(f"{SERVER_URL}/search_hotels/", params=params)
            
            if response.status_code == 200:
                hotels_data = response.json()
                self.display_results(hotels_data)
            else:
                messagebox.showerror("Ошибка сервера", f"Не удалось выполнить поиск. Код: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Сервер недоступен. Запустите сервер FastAPI!")


    def display_results(self, hotels_data):
        for widget in self.results_scroll_frame.winfo_children():
            widget.destroy()

        if not hotels_data:
            no_result_label = CTk.CTkLabel(self.results_scroll_frame, text="Отели по вашему запросу не найдены 😔", font=("", 18))
            no_result_label.pack(pady=50)
            return

        for hotel in hotels_data:
            card = CTk.CTkFrame(self.results_scroll_frame, fg_color="#333333", corner_radius=10)
            card.pack(fill=CTk.X, pady=10, padx=10)

            img_label = CTk.CTkLabel(card, text="Загрузка...", width=160, height=120, fg_color="gray20", corner_radius=8)
            img_label.pack(side=CTk.LEFT, padx=15, pady=15)

            ctk_img = self.get_image_from_url(hotel.get("image_path"))
            if ctk_img:
                img_label.configure(image=ctk_img, text="")
            else:
                img_label.configure(text="Нет фото")

            info_frame = CTk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side=CTk.LEFT, fill=CTk.Y, pady=15)

            title_label = CTk.CTkLabel(info_frame, text=f"🏨 {hotel['name']} ({hotel['city']})", font=("Arial", 18, "bold"))
            title_label.pack(anchor=CTk.W)

            rating_label = CTk.CTkLabel(info_frame, text=f"⭐ Рейтинг: {hotel['rating']}", text_color="gold", font=("Arial", 14))
            rating_label.pack(anchor=CTk.W, pady=(5, 0))

            price_label = CTk.CTkLabel(info_frame, text=f"💵 От: {hotel['min_price']} руб/сутки", text_color="lightgreen", font=("Arial", 14))
            price_label.pack(anchor=CTk.W, pady=(5, 0))

            book_btn = CTk.CTkButton(card, text="Выбрать номера", font=("Arial", 14, "bold"), command=lambda h_id=hotel['id']: self.open_hotel_details(h_id))
            book_btn.pack(side=CTk.RIGHT, padx=20)

    def get_image_from_url(self, image_path):
        if not image_path:
            return None

        clean_path = image_path.replace("\\", "/")
        url = f"{SERVER_URL}/{clean_path}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))

                return CTk.CTkImage(light_image=image, dark_image=image, size=(160, 120))
        except Exception as e:
            print(f"Не удалось загрузить фото: {e}")
            
        return None

    def open_hotel_details(self, hotel_id):
        print(f"Пользователь хочет открыть отель с ID: {hotel_id}")

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

class Admin_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.btn_add = CTk.CTkButton(master=self, text="Добавить", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Add_window), anchor=CTk.CENTER)
        self.btn_add.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)

class Add_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.foto_lable = CTk.CTkLabel(master=self, text="Фото: ", font=("", 15), anchor=CTk.CENTER)
        self.foto_lable.place(anchor=CTk.E, relx=0.2, rely=0.4)

        self.image_lable = CTk.CTkLabel(master=self, text="Фото не выбрано", width=150, height=150, fg_color=("gray20"), font=("", 15), corner_radius=10, anchor=CTk.CENTER)
        self.image_lable.place(anchor=CTk.CENTER, relx=0.4, rely=0.4)

        self.btn_image = CTk.CTkButton(master=self, text="Выбрать", font=("", 15, "bold"), command=self.add_image)
        self.btn_image.place(anchor=CTk.CENTER, relx=0.7, rely=0.4)

        self.name_lable = CTk.CTkLabel(master=self, text="Название: ", font=("", 15), anchor=CTk.CENTER)
        self.name_lable.place(anchor=CTk.E, relx=0.2, rely=0.6)

        self.name_enrty = CTk.CTkEntry(master=self, font=("", 15), width=400, height=30)
        self.name_enrty.place(anchor=CTk.CENTER, relx=0.5, rely=0.6)

        self.location_lable = CTk.CTkLabel(master=self, text="Расположение: ", font=("", 15), anchor=CTk.CENTER)
        self.location_lable.place(anchor=CTk.E, relx=0.2, rely=0.7)

        self.city_combo = CTk.CTkOptionMenu(master=self, values=["Париж", "Милан", "Рим", "Берлин", "Нью-Йорк", "Лондон", "Гонконг", "Москва"])
        self.city_combo.place(anchor=CTk.CENTER, relx=0.335, rely=0.7)
        self.city_combo.set("Выберите город")

        self.location_entry = CTk.CTkEntry(master=self, font=("", 15), width=240, height=30)
        self.location_entry.place(anchor=CTk.CENTER, relx=0.6, rely=0.7)

        self.description_lable = CTk.CTkLabel(master=self, text="Описание: ", font=("", 15), anchor=CTk.CENTER)
        self.description_lable.place(anchor=CTk.E, relx=0.2, rely=0.8)

        self.description_textbox = CTk.CTkTextbox(master=self, font=("", 15), width=400, height=30)
        self.description_textbox.place(anchor=CTk.CENTER, relx=0.5, rely=0.8)

        self.btn_submit = CTk.CTkButton(master=self, text="Сохранить", font=("", 15, "bold"), command=self.save)
        self.btn_submit.place(anchor=CTk.CENTER, relx=0.5, rely=0.9)

    def add_image(self):
        self.file_path = filedialog.askopenfilename(
        title="Выберите фотографию",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
            ("All Files", "*.*")
        ]
        )

        if self.file_path:
            img_data = Image.open(self.file_path)
            ctk_image = CTk.CTkImage(light_image=img_data, dark_image=img_data, size=(150, 150))
            self.image_lable.configure(image=ctk_image, text="")

    def save(self):
        data = {
            "name": self.name_enrty.get(),
            "location": self.location_entry.get(),
            "city": self.city_combo.get(),
            "description": self.description_textbox.get("0.0", "end").strip()
        }

        try:
            with open(self.file_path, 'rb') as f:
                file = {
                    'image': (self.file_path.split("/")[-1], f, 'image/jpeg')
                }

                response = requests.post(f"{SERVER_URL}/add_hotel/", data=data, files=file)

            if response.status_code == 200:
                messagebox.showinfo("Успешно", "Успешно")
            else:
                try:
                    error_data = response.json().get("detail")
                    self.error_lable = CTk.CTkLabel(master=self, text=f"{error_data}", font=("", 15), anchor=CTk.CENTER)
                    self.error_lable.place(anchor=CTk.CENTER, relx=0.5, rely=0.95)
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
        for F in (Main_window, Search_window, Account_window, Register_window, Login_window, Admin_window, Add_window):
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