import tkinter as tk
from tkinter import messagebox, ttk
import keyboard
import os
import gem_ops
from PIL import ImageGrab, Image
import win32api, win32con, win32ui, win32gui
import markdown
from tkhtmlview import HTMLLabel
import time

# Global değişkenler
last_keypress_time = 0
DOUBLE_PRESS_INTERVAL = 0.5  # İki basış arası maksimum süre (saniye)
user_token = "local_test_token"  # Yerel token (Firebase yerine kullanılıyor)
assigned_key = None
#server_url = "http://127.0.0.1:5000"  # Sunucu URL'si
active_popup = None  # Aktif popup referansı
start_stop_button = None  # Yeni global değişken
program_running = False  # Program durumunu takip etmek için
current_font_size = 11  # Varsayılan font boyutu

def save_font_size(size):
    """Font boyutunu kaydet."""
    with open('font_size.txt', 'w') as f:
        f.write(str(size))

def load_font_size():
    """Kaydedilmiş font boyutunu yükle."""
    global current_font_size
    try:
        with open('font_size.txt', 'r') as f:
            current_font_size = int(f.read())
    except:
        current_font_size = 11  # Dosya yoksa varsayılan boyut


def start_stop_program():
    """Programı başlat/durdur."""
    global program_running, start_stop_button, assigned_key
    
    if not program_running:  # Program başlatılacak
        if not assigned_key:
            messagebox.showerror("Error", "No key assigned. Please assign a key first.")
            return
        program_running = True
        start_stop_button.config(text="Stop Program", bg="#dc3545")
        root.iconify()
        keyboard.add_hotkey(assigned_key, handle_hotkey)
        print("Program running in background...")
    else:  # Program durdurulacak
        program_running = False
        if assigned_key:
            keyboard.remove_hotkey(assigned_key)
        start_stop_button.config(text="Start Program", bg="#28a745")
        print("Program stopped.")


def logout():
    """Kullanıcı çıkışı."""
    global assigned_key, active_popup, program_running, key_button
    if assigned_key:
        keyboard.unhook_all()
        assigned_key = None
    active_popup = None
    program_running = False
    if key_button and key_button.winfo_exists():
        key_button.config(text="Assign Key")
    gem_ops.reset_chat()  # Sohbet geçmişini sıfırla
    switch_to_login()


def switch_to_login():
    """Giriş ekranına geçiş."""
    for widget in root.winfo_children():
        widget.destroy()
    create_login_screen()


def switch_to_main():
    """Ana ekrana geçiş."""
    for widget in root.winfo_children():
        widget.destroy()
    create_main_screen()


def on_key_press(e):
    """Tuş atama işlemi."""
    global assigned_key, key_button
    if e.name == "esc":
        print("Key assignment cancelled.")
        keyboard.unhook_all()
        if key_button and key_button.winfo_exists():
            key_button.config(text="Assign Key")
    else:
        assigned_key = e.name
        if key_button and key_button.winfo_exists():
            key_button.config(text=f"Assigned Key: {assigned_key}")
        print(f"Key '{assigned_key}' assigned.")
        keyboard.unhook_all()

def assign_key():
    """Tuş atama başlat."""
    global assigned_key, key_button
    assigned_key = None
    if key_button and key_button.winfo_exists():
        key_button.config(text="Press any key to assign it\n(press ESC to cancel)...", wraplength=200)  # Added wraplength to wrap the text
    print("Press any key to assign it (press ESC to cancel)...")
    keyboard.on_press(on_key_press)

def start_program():
    """Programı başlat."""
    if not assigned_key:
        messagebox.showerror("Error", "No key assigned. Please assign a key first.")
        return
    root.iconify()  # Minimize to taskbar
    keyboard.add_hotkey(assigned_key, handle_hotkey)
    print("Program running in background...")


def take_screenshot():
    """Seçilen alanın ekran görüntüsünü al ve sunucuya gönder."""
    file_path = capture_selected_area()
    if file_path:
        create_prompt_popup(file_path)
    else:
        print("Screenshot alınmadı veya işlem iptal edildi.")

def capture_selected_area():
    """Kullanıcının seçtiği alanın ekran görüntüsünü al ve kaydet."""
    global program_running  # Program durumunu kontrol etmek için ekle

    selection_root = tk.Tk()

    virtual_screen_left = win32api.GetSystemMetrics(76)
    virtual_screen_top = win32api.GetSystemMetrics(77)
    virtual_screen_width = win32api.GetSystemMetrics(78)
    virtual_screen_height = win32api.GetSystemMetrics(79)

    selection_root.geometry(f"{virtual_screen_width}x{virtual_screen_height}+{virtual_screen_left}+{virtual_screen_top}")
    selection_root.attributes("-alpha", 0.3)
    selection_root.attributes("-topmost", True)
    selection_root.configure(bg="black")
    selection_root.title("Ekran Alıntısı Aracı")
    selection_root.focus_force()  # Pencereye focus'u zorla

    start_x = start_y = end_x = end_y = 0
    rect_id = None
    file_path = None

    def capture_area(x1, y1, x2, y2):
        # Win32 API kullanarak ekran görüntüsü al
        hwin = win32gui.GetDesktopWindow()
        width = x2 - x1
        height = y2 - y1

        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)
        memdc.BitBlt((0, 0), (width, height), srcdc, (x1, y1), win32con.SRCCOPY)

        # Bitmap'i PIL Image'e dönüştür
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # Temizlik
        win32gui.DeleteObject(bmp.GetHandle())
        memdc.DeleteDC()
        srcdc.DeleteDC()
        win32gui.ReleaseDC(hwin, hwindc)

        return img

    def on_mouse_press(event):
        nonlocal start_x, start_y, rect_id
        start_x = event.x + virtual_screen_left
        start_y = event.y + virtual_screen_top
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)

    def on_mouse_drag(event):
        nonlocal rect_id
        canvas.coords(rect_id,
                     event.x - (event.x + virtual_screen_left - start_x),
                     event.y - (event.y + virtual_screen_top - start_y),
                     event.x, event.y)

    def on_mouse_release(event):
        nonlocal start_x, start_y, end_x, end_y, file_path
        end_x = event.x + virtual_screen_left
        end_y = event.y + virtual_screen_top
        selection_root.destroy()

        x1, x2 = sorted([start_x, end_x])
        y1, y2 = sorted([start_y, end_y])

        if x2 - x1 > 0 and y2 - y1 > 0:
            screenshot = capture_area(x1, y1, x2, y2)
            file_path = os.path.join(os.getcwd(), "screenshot.png")
            screenshot.save(file_path)
        else:
            messagebox.showwarning("Geçersiz Alan", "Geçerli bir alan seçilmedi.")

    def on_escape(event):
        nonlocal file_path
        file_path = None
        selection_root.destroy()
        print("Screenshot cancelled with ESC")

    canvas = tk.Canvas(selection_root, cursor="cross", takefocus=0) # takefocus=0 eklendi
    canvas.pack(fill="both", expand=True)

    canvas.bind("<ButtonPress-1>", on_mouse_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_release)
    selection_root.bind("<Escape>", on_escape)

    selection_root.mainloop()
    return file_path

def create_prompt_popup(file_path):
    """Modern prompt girişi popup'ı."""
    global active_popup
    active_popup = tk.Toplevel()
    active_popup.title("Screenshot and Prompt")
    active_popup.configure(bg="#f5f5f5")
    active_popup.geometry("400x200")
    
    main_frame = tk.Frame(active_popup, bg="#f5f5f5")
    main_frame.pack(expand=True, fill="both", padx=20, pady=15)

    tk.Label(
        main_frame,
        text="Enter your prompt:",
        font=("Arial", 12, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(anchor="w")

    prompt_entry = tk.Entry(
        main_frame,
        font=("Arial", 11),
        relief="flat",
        bg="white",
        highlightthickness=1,
        highlightbackground="#dddddd",
        highlightcolor="#007bff"
    )
    prompt_entry.pack(fill="x", pady=(10, 20), ipady=8)

    def send_to_ai():
        prompt = prompt_entry.get().strip()
        if prompt:
            active_popup.withdraw()
            process_image_with_gemini(file_path, prompt)
        else:
            messagebox.showwarning("Warning", "Please enter a prompt")

    tk.Button(
        main_frame,
        text="Send",
        command=send_to_ai,
        bg="#007bff",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8
    ).pack()

    prompt_entry.bind("<Return>", lambda e: send_to_ai())
    active_popup.bind("<Escape>", lambda e: active_popup.destroy())  # Close the popup when ESC is pressed
    center_window(active_popup)
    active_popup.after(100, lambda: enforce_window_focus(active_popup, prompt_entry))


def process_image_with_gemini(file_path, prompt):
    """Sunucuya isteği gönder."""
    global active_popup
    name = "scsht"
    file = gem_ops.upload_file(file_path, name)
    response_text = gem_ops.generate_content(file, prompt)
    if response_text != None:
        create_response_popup(response_text)


def create_response_popup(response_text):
    """Sunucu yanıtını göstermek için modern bir popup oluştur."""
    global active_popup, current_font_size

    if active_popup and active_popup.winfo_exists():
        active_popup.destroy()

    # Font boyutunu yükle
    load_font_size()

    active_popup = tk.Toplevel()
    active_popup.title("AI Response")
    active_popup.geometry("600x800")
    active_popup.configure(bg="#f5f5f5")
    active_popup.resizable(True, True)  # Pencereyi yeniden boyutlandırılabilir yap

    main_frame = tk.Frame(active_popup, bg="#f5f5f5")
    main_frame.pack(expand=True, fill="both", padx=20, pady=15)

    # Üst kontrol paneli
    control_frame = tk.Frame(main_frame, bg="#f5f5f5")
    control_frame.pack(fill="x", pady=(0, 10))

    tk.Label(
        control_frame,
        text="Answer:",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#333333",
    ).pack(side="left")

    # Font kontrol butonları
    font_frame = tk.Frame(control_frame, bg="#f5f5f5")
    font_frame.pack(side="right")

    # Font kontrol butonları bölümünü güncelle
    def change_font_size(delta):
        global current_font_size
        new_size = max(8, min(20, current_font_size + delta))  # 8-20 arası sınırla
        if new_size != current_font_size:
            current_font_size = new_size
            save_font_size(current_font_size)
            # HTML içeriğini yeni font boyutuyla yeniden oluştur
            html_with_style = f'''
                <div style="font-family: Arial; font-size: {current_font_size}px;">
                    {html_content}
                </div>
            '''
            response_label.set_html(html_with_style)

    tk.Button(
        font_frame,
        text="A+",
        command=lambda: change_font_size(1),
        bg="#007bff",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        padx=10
    ).pack(side="left", padx=2)

    tk.Button(
        font_frame,
        text="A-",
        command=lambda: change_font_size(-1),
        bg="#007bff",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        padx=10
    ).pack(side="left", padx=2)

    # Markdown formatını HTML'e çevir
    html_content = markdown.markdown(response_text)
    
    # Başlangıç HTML içeriği
    initial_html = f'''
        <div style="font-family: Arial; font-size: {current_font_size}px;">
            {html_content}
        </div>
    '''

    # Yanıt metin alanı
    response_label = HTMLLabel(
        main_frame,
        html=initial_html,
        padx=10,
        pady=10,
        
    )
    response_label.pack(expand=True, fill="both")
    # response_label.config(state="normal")
    
    # Yeni soru bölümü
    question_frame = tk.Frame(main_frame, bg="#f5f5f5")
    question_frame.pack(fill="x", pady=(20, 0))

    tk.Label(
        question_frame,
        text="Ask a new question:",
        font=("Arial", 12, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(anchor="w")

    new_question_entry = tk.Entry(
        question_frame,
        font=("Arial", 11),
        relief="flat",
        bg="white",
        highlightthickness=1,
        highlightbackground="#dddddd",
        highlightcolor="#007bff"
    )
    new_question_entry.pack(fill="x", pady=(5, 15), ipady=8)

    # Butonlar
    button_frame = tk.Frame(main_frame, bg="#f5f5f5")
    button_frame.pack(fill="x", pady=(0, 10))

    def send_new_question(event=None):
        question = new_question_entry.get().strip()
        if question:
            active_popup.withdraw()
            new_answer = gem_ops.generate_text_content(response_text, question)
            create_response_popup(new_answer)
        else:
            messagebox.showwarning("Warning", "Please enter a question.")

    ask_button = tk.Button(
        button_frame,
        text="Ask",
        command=send_new_question,
        bg="#007bff",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8
    )
    ask_button.pack(side="left", padx=(0, 10))

    close_button = tk.Button(
        button_frame,
        text="Close",
        command=active_popup.destroy,
        bg="#dc3545",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8
    )
    close_button.pack(side="left")

    # Kısayol tuşları
    active_popup.bind("<Escape>", lambda e: active_popup.destroy())
    new_question_entry.bind("<Return>", send_new_question)
    active_popup.focus_set()

    # Popup'ı ekranın ortasında göster
    center_window(active_popup)

def center_window(window):
    """Pencereyi ekranın ortasında konumlandır."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")



def create_login_screen():
    """Responsive giriş ekranı."""
    root.geometry("400x500")  # Başlangıç boyutu
    root.minsize(350, 450)    # Minimum boyut

    main_frame = tk.Frame(root, bg="#f5f5f5")
    main_frame.pack(expand=True, fill="both")

    content_frame = tk.Frame(main_frame, bg="#f5f5f5")
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        content_frame,
        text="Login to Continue",
        font=("Arial", 18, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(pady=(0, 30))

    username_entry = tk.Entry(
        content_frame,
        font=("Arial", 11),
        relief="flat",
        width=30,
        bg="white",
        highlightthickness=1,
        highlightbackground="#dddddd"
    )
    username_entry.pack(ipady=8, pady=(0, 15))
    #username_entry.insert(0, "Username")
    username_entry.insert(0, "test") ## deneme sürümünde otomatik gelsin diye, productionda kaldırılacak
    username_entry.bind("<FocusIn>", lambda e: clear_placeholder(username_entry, "Username"))
    username_entry.bind("<FocusOut>", lambda e: restore_placeholder(username_entry, "Username"))

    password_entry = tk.Entry(
        content_frame,
        font=("Arial", 11),
        relief="flat",
        width=30,
        bg="white",
        highlightthickness=1,
        highlightbackground="#dddddd",
        show="•"
    )
    password_entry.pack(ipady=8, pady=(0, 25))
    #password_entry.insert(0, "Password")
    password_entry.insert(0, "test") ## deneme sürümünde otomatik gelsin diye, productionda kaldırılacak
    password_entry.bind("<FocusIn>", lambda e: clear_placeholder(password_entry, "Password", True))
    password_entry.bind("<FocusOut>", lambda e: restore_placeholder(password_entry, "Password", True))

    # bu kısımda firebase auth eklenecek
    def login(event=None):
        username = username_entry.get()
        password = password_entry.get()
        if username != "Username" and password != "Password":
            if username == "test" and password == "test":
                global user_token
                user_token = "local_test_token"
                switch_to_main()
            else:
                messagebox.showerror("Error", "Invalid credentials")

    login_button = tk.Button(
        content_frame,
        text="Login",
        command=login,
        bg="#007bff",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        width=25
    )
    login_button.pack(ipady=8)

    root.bind('<Return>', login)

def clear_placeholder(entry, placeholder, is_password=False):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        if is_password:
            entry.config(show="•")

def restore_placeholder(entry, placeholder, is_password=False):
    if entry.get() == "":
        entry.insert(0, placeholder)
        if is_password:
            entry.config(show="")



def enforce_window_focus(window, widget_to_focus):
    """Pencereyi aktif hale getir ve bir widget'e odaklan."""
    window.lift()  # Pencereyi diğerlerinin üstüne taşı
    window.focus_force()  # Pencereyi sistem tarafından aktif yap
    widget_to_focus.focus_set()  # Belirtilen widget'e odaklan


def handle_reset_chat():
    """Sohbet geçmişini sıfırlama işlemini yönetir ve kullanıcıyı bilgilendirir."""
    if messagebox.askyesno("Onay", "Mevcut sohbet geçmişi silinecek. Emin misiniz?"):
        gem_ops.reset_chat()
        messagebox.showinfo("Başarılı", "Sohbet geçmişi başarıyla sıfırlandı.")


def handle_delete_files():
    """Yüklenen tüm dosyaları silme işlemini yönetir ve kullanıcıyı bilgilendirir."""
    if messagebox.askyesno("DİKKAT", "Yüklenen tüm görüntüler sunucudan silinecek. Bu işlem geri alınamaz. Emin misiniz?"):
        gem_ops.delete_all_files()
        messagebox.showinfo("Başarılı", "Tüm dosyalar başarıyla silindi.")


def create_main_screen():
    """Responsive ana ekran."""
    global key_button, start_stop_button
    # Pencere yüksekliğini yeni butonlar ve başlık için ayarlayalım
    root.geometry("400x600") 
    root.minsize(350, 550)

    main_frame = tk.Frame(root, bg="#f5f5f5")
    main_frame.pack(expand=True, fill="both")

    content_frame = tk.Frame(main_frame, bg="#f5f5f5")
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Kullanım talimatları
    tk.Label(
        content_frame,
        text="1) Bir kısayol tuşu ata\n2) Programı başlat\n3) Atadığın tuşa çift basarak kullan!",
        font=("Arial", 14),
        bg="#f5f5f5",
        fg="#333333",
        justify="left"
    ).pack(pady=(0, 20), fill="x", padx=20)

    # --- Ana Kontrol Butonları ---
    key_button = tk.Button(content_frame, text="Tuş Ata", command=assign_key, bg="#007bff", fg="white", font=("Arial", 11, "bold"), relief="flat", width=30)
    key_button.pack(ipady=8, pady=5)

    start_stop_button = tk.Button(content_frame, text="Programı Başlat", command=start_stop_program, bg="#28a745", fg="white", font=("Arial", 11, "bold"), relief="flat", width=30)
    start_stop_button.pack(ipady=8, pady=5)

    logout_button = tk.Button(content_frame, text="Çıkış Yap", command=logout, bg="#6c757d", fg="white", font=("Arial", 11, "bold"), relief="flat", width=30)
    logout_button.pack(ipady=8, pady=10)
    
    # --- Ayırıcı ---
    # Widget'ları görsel olarak gruplamak için. padx ile kenarlardan boşluk bırakıyoruz.
    ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=10, padx=20)

    # --- Yardımcı Fonksiyon Butonları (Araçlar) ---
    tk.Label(
        content_frame,
        text="Araçlar",
        font=("Arial", 12, "bold"),
        bg="#f5f5f5",
        fg="#333333"
    ).pack(pady=(5, 10))

    reset_chat_button = tk.Button(
        content_frame, 
        text="Sohbet Geçmişini Sıfırla", 
        command=handle_reset_chat, 
        bg="#ffc107", # Uyarı rengi (sarı)
        fg="black", 
        font=("Arial", 10, "bold"), 
        relief="flat", 
        width=30
    )
    reset_chat_button.pack(ipady=8, pady=5)

    delete_files_button = tk.Button(
        content_frame, 
        text="Yüklenen Dosyaları Sil", 
        command=handle_delete_files, 
        bg="#dc3545", # Tehlike rengi (kırmızı)
        fg="white", 
        font=("Arial", 10, "bold"), 
        relief="flat", 
        width=30
    )
    delete_files_button.pack(ipady=8, pady=5)


def handle_hotkey():
    """Hotkey işlevi (çift basma kontrolü ile)."""
    global active_popup, program_running, last_keypress_time
    current_time = time.time()

    if not program_running:  # Program durdurulmuşsa hiçbir şey yapma
        return

    if current_time - last_keypress_time < DOUBLE_PRESS_INTERVAL:
        # Aktif popup varsa kapat
        if active_popup and active_popup.winfo_exists():
            active_popup.destroy()
            return
        take_screenshot()
    last_keypress_time = current_time


if __name__ == "__main__":
    root = tk.Tk()
    root.title("AskGPT")
    root.geometry("400x300")
    root.wm_attributes("-topmost", True)  # Her zaman üstte
    switch_to_login()
    root.mainloop()
