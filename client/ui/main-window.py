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
        self.update_ui()

    def update_ui(self):
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
        self.update_ui()

    def update_ui(self):
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
        details_window = self.controller.frames[Hotel_details_window]
        details_window.load_hotel_data(hotel_id)

        self.controller.show_frame(Hotel_details_window)

class Hotel_details_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        self.back_btn = CTk.CTkButton(self, text="← Назад к поиску", width=150, fg_color="gray", hover_color="darkgray", command=self.go_back)
        self.back_btn.place(relx=0.1, rely=0.05, anchor=CTk.W)

        self.main_scroll = CTk.CTkScrollableFrame(self, width=750, height=500, fg_color="transparent")
        self.main_scroll.place(relx=0.5, rely=0.55, anchor=CTk.CENTER)

        self.image_label = CTk.CTkLabel(self.main_scroll, text="Загрузка фото...", width=600, height=300, fg_color="gray20", corner_radius=10)
        self.image_label.pack(pady=(10, 20))

        self.title_label = CTk.CTkLabel(self.main_scroll, text="", font=("Arial", 26, "bold"))
        self.title_label.pack(anchor=CTk.W, padx=20)

        self.rating_label = CTk.CTkLabel(self.main_scroll, text="", text_color="gold", font=("Arial", 16))
        self.rating_label.pack(anchor=CTk.W, padx=20, pady=(0, 10))

        self.location_label = CTk.CTkLabel(self.main_scroll, text="", text_color="lightgray", font=("Arial", 14))
        self.location_label.pack(anchor=CTk.W, padx=20, pady=(0, 15))

        self.desc_label = CTk.CTkLabel(self.main_scroll, text="", font=("Arial", 14), justify="left", wraplength=700)
        self.desc_label.pack(anchor=CTk.W, padx=20, pady=(0, 30))

        CTk.CTkLabel(self.main_scroll, text="Доступные номера:", font=("Arial", 20, "bold")).pack(anchor=CTk.W, padx=20, pady=(10, 10))

        self.rooms_frame = CTk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.rooms_frame.pack(fill=CTk.X, padx=20, pady=10)

    def load_hotel_data(self, hotel_id):
        for widget in self.rooms_frame.winfo_children():
            widget.destroy()
            
        self.title_label.configure(text="Загрузка данных...")

        try:
            response = requests.get(f"{SERVER_URL}/hotel_details/{hotel_id}")
            if response.status_code == 200:
                hotel = response.json()
                self.fill_hotel_data(hotel)
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные об отеле")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Сервер недоступен!")

    def fill_hotel_data(self, hotel):
        self.title_label.configure(text=f"{hotel['name']}")
        self.rating_label.configure(text=f"⭐ Рейтинг: {hotel['rating']} / 5.0")
        self.location_label.configure(text=f"📍 {hotel['city']}, {hotel['location']}")
        self.desc_label.configure(text=hotel['description'] or "Описание отсутствует.")

        ctk_img = self.get_large_image(hotel.get("image_path"))
        if ctk_img:
            self.image_label.configure(image=ctk_img, text="")
        else:
            self.image_label.configure(text="Нет фото", image="")

        rooms = hotel.get("rooms", [])
        if not rooms:
            CTk.CTkLabel(self.rooms_frame, text="К сожалению, в этом отеле пока нет номеров.", text_color="gray").pack()
        else:
            for room in rooms:
                room_card = CTk.CTkFrame(self.rooms_frame, fg_color="#444444", corner_radius=8)
                room_card.pack(fill=CTk.X, pady=5)

                room_info = f"Номер: {room['room_num']} | Тип: {room['room_type']}"
                CTk.CTkLabel(room_card, text=room_info, font=("Arial", 16, "bold")).pack(side=CTk.LEFT, padx=15, pady=15)
                
                CTk.CTkLabel(room_card, text=f"{room['price']} руб/сутки", text_color="lightgreen", font=("Arial", 16)).pack(side=CTk.LEFT, padx=20)

                state = "normal" if room['is_available'] else "disabled"
                btn_text = "Забронировать" if room['is_available'] else "Занят"
                btn_color = "#1f538d" if room['is_available'] else "gray"

                CTk.CTkButton(room_card, text=btn_text, state=state, fg_color=btn_color, command=lambda r_id=room['id']: self.book_room(r_id)).pack(side=CTk.RIGHT, padx=15)

    def get_large_image(self, image_path):
        if not image_path: return None
        clean_path = image_path.replace("\\", "/")
        try:
            response = requests.get(f"{SERVER_URL}/{clean_path}")
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return CTk.CTkImage(light_image=image, dark_image=image, size=(600, 300))
        except:
            pass
        return None

    def book_room(self, room_id):
        print(f"Пользователь хочет забронировать комнату ID: {room_id}")

    def go_back(self):
        self.controller.show_frame(Search_window)

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

        self.btn_add = CTk.CTkButton(master=self, text="Добавить отель", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Add_hotel_window), anchor=CTk.CENTER)
        self.btn_add.place(anchor=CTk.CENTER, relx=0.5, rely=0.2)
        
        self.btn_add = CTk.CTkButton(master=self, text="Добавить номер", font=("", 15, "bold"), command=lambda: self.controller.show_frame(Add_room_window), anchor=CTk.CENTER)
        self.btn_add.place(anchor=CTk.CENTER, relx=0.5, rely=0.3)

class Add_hotel_window(CTk.CTkFrame):
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

class Add_room_window(CTk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller
        
        self.hotels_mapping = {}

        self.nav_plane = Nav_plane(self, controller=self.controller, fg_color="#2b2b2b", corner_radius=15, width=780, height=60)
        self.nav_plane.place(anchor=CTk.CENTER, relx=0.5, rely=0.06)

        self.title_label = CTk.CTkLabel(master=self, text="Добавление нового номера", font=("Arial", 20, "bold"))
        self.title_label.place(anchor=CTk.CENTER, relx=0.5, rely=0.15)

        self.hotel_label = CTk.CTkLabel(master=self, text="Отель: ", font=("", 15), anchor=CTk.CENTER)
        self.hotel_label.place(anchor=CTk.E, relx=0.35, rely=0.3)

        self.hotel_combo = CTk.CTkOptionMenu(master=self, values=["Загрузка..."], width=250)
        self.hotel_combo.place(anchor=CTk.W, relx=0.4, rely=0.3)

        self.num_label = CTk.CTkLabel(master=self, text="Номер комнаты: ", font=("", 15), anchor=CTk.CENTER)
        self.num_label.place(anchor=CTk.E, relx=0.35, rely=0.4)

        self.room_num_entry = CTk.CTkEntry(master=self, font=("", 15), width=250, height=30)
        self.room_num_entry.place(anchor=CTk.W, relx=0.4, rely=0.4)

        self.type_label = CTk.CTkLabel(master=self, text="Тип номера: ", font=("", 15), anchor=CTk.CENTER)
        self.type_label.place(anchor=CTk.E, relx=0.35, rely=0.5)

        self.room_type_combo = CTk.CTkOptionMenu(master=self, values=["Стандарт", "Улучшенный", "Люкс", "Апартаменты", "Президентский"], width=250)
        self.room_type_combo.place(anchor=CTk.W, relx=0.4, rely=0.5)
        self.room_type_combo.set("Стандарт")

        self.price_label = CTk.CTkLabel(master=self, text="Цена (руб/сутки): ", font=("", 15), anchor=CTk.CENTER)
        self.price_label.place(anchor=CTk.E, relx=0.35, rely=0.6)

        self.price_entry = CTk.CTkEntry(master=self, font=("", 15), width=250, height=30)
        self.price_entry.place(anchor=CTk.W, relx=0.4, rely=0.6)

        self.btn_submit = CTk.CTkButton(master=self, text="Добавить комнату", font=("", 15, "bold"), command=self.save_room)
        self.btn_submit.place(anchor=CTk.CENTER, relx=0.5, rely=0.8)


    def update_ui(self):
        try:
            response = requests.get(f"{SERVER_URL}/hotels_list/")
            if response.status_code == 200:
                hotels = response.json()
                
                self.hotels_mapping.clear()
                combo_values = []
                
                for h in hotels:
                    display_name = f"{h['name']} (ID: {h['id']})"
                    combo_values.append(display_name)
                    self.hotels_mapping[display_name] = h['id']
                
                if combo_values:
                    self.hotel_combo.configure(values=combo_values)
                    self.hotel_combo.set(combo_values[0])
                else:
                    self.hotel_combo.configure(values=["Нет доступных отелей"])
                    self.hotel_combo.set("Нет доступных отелей")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить список отелей")
        except requests.exceptions.ConnectionError:
             messagebox.showerror("Ошибка", "Сервер недоступен!")


    def save_room(self):
        selected_hotel_str = self.hotel_combo.get()
        
        hotel_id = self.hotels_mapping.get(selected_hotel_str)

        if not hotel_id:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите отель из списка!")
            return

        room_num_text = self.room_num_entry.get().strip()
        room_price_text = self.price_entry.get().strip()
        room_type = self.room_type_combo.get()

        if not room_num_text or not room_price_text:
            messagebox.showwarning("Внимание", "Заполните номер комнаты и цену!")
            return

        try:
            room_num = int(room_num_text)
            price = int(room_price_text)
        except ValueError:
            messagebox.showerror("Ошибка", "Номер комнаты и цена должны быть числами!")
            return

        data = {
            "hotel_id": hotel_id,
            "room_num": room_num,
            "room_type": room_type,
            "price": price
        }

        try:
            response = requests.post(f"{SERVER_URL}/add_room/", json=data)

            if response.status_code == 200:
                messagebox.showinfo("Успешно", f"Комната №{room_num} добавлена в {selected_hotel_str}!")
                self.room_num_entry.delete(0, 'end') 
            else:
                try:
                    error_data = response.json().get("detail", "Неизвестная ошибка")
                    messagebox.showerror("Ошибка", error_data)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Критическая ошибка: {response.status_code}")

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
        for F in (Main_window, Search_window, Hotel_details_window, Account_window, Register_window, Login_window, Admin_window, Add_hotel_window, Add_room_window):
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