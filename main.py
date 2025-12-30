import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from whatsapp_sender import WhatsAppSender


class WhatsAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Mesaj Gönderme")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        self.whatsapp_sender = None
        self.image_path = ""
        
        self.create_widgets()
        
    def create_widgets(self):
        """GUI bileşenlerini oluşturur"""
        
        # Başlık
        title_label = tk.Label(
            self.root, 
            text="WhatsApp Mesaj Gönderme Uygulaması",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # WhatsApp Bağlantısı Butonu
        self.connect_button = tk.Button(
            self.root,
            text="WhatsApp Bağlantısı",
            command=self.open_whatsapp_web,
            bg="#25D366",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10,
            cursor="hand2"
        )
        self.connect_button.pack(fill=tk.X, padx=20, pady=10)
        
        # Fotoğraf Seçici Frame
        photo_frame = tk.Frame(self.root)
        photo_frame.pack(fill=tk.X, padx=20, pady=10)
        
        photo_label = tk.Label(
            photo_frame,
            text="Fotoğraf:",
            font=("Arial", 10, "bold")
        )
        photo_label.pack(side=tk.LEFT)
        
        self.photo_path_label = tk.Label(
            photo_frame,
            text="Fotoğraf seçilmedi",
            fg="gray",
            font=("Arial", 9)
        )
        self.photo_path_label.pack(side=tk.LEFT, padx=10)
        
        photo_button = tk.Button(
            photo_frame,
            text="Fotoğraf Seç",
            command=self.select_image,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        photo_button.pack(side=tk.RIGHT)
        
        # Mesaj Metin Alanı
        message_label = tk.Label(
            self.root,
            text="Mesaj Metni:",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        message_label.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        self.message_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.message_text.pack(fill=tk.BOTH, padx=20, pady=(0, 10))
        
        # Telefon Numaraları Alanı
        phone_label = tk.Label(
            self.root,
            text="Telefon Numaraları (virgül veya satır ile ayırın):",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        phone_label.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        self.phone_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.phone_text.pack(fill=tk.BOTH, padx=20, pady=(0, 10))
        
        # Gönder Butonu
        self.send_button = tk.Button(
            self.root,
            text="Mesajları Gönder",
            command=self.send_messages,
            bg="#128C7E",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.send_button.pack(fill=tk.X, padx=20, pady=10)
        
        # Durum Göstergesi
        status_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=2)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_title = tk.Label(
            status_frame,
            text="Durum:",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        status_title.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Hazır",
            font=("Arial", 9),
            anchor="w",
            fg="green",
            wraplength=560
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
    def update_status(self, message):
        """Durum mesajını günceller (thread-safe)"""
        self.root.after(0, lambda: self.status_label.config(text=message))
        
    def open_whatsapp_web(self):
        """WhatsApp Web'i açan buton handler'ı"""
        def run():
            try:
                self.update_status("WhatsApp Web açılıyor...")
                self.whatsapp_sender = WhatsAppSender(status_callback=self.update_status)
                
                if self.whatsapp_sender.open_whatsapp_web():
                    self.root.after(0, lambda: self.connect_button.config(
                        text="WhatsApp Açık ✓",
                        bg="#128C7E",
                        state=tk.DISABLED
                    ))
                    self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
                    
                    # Giriş yapılmasını bekle
                    self.whatsapp_sender.wait_for_login()
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Hata",
                        "WhatsApp Web açılamadı. ChromeDriver'ın kurulu olduğundan emin olun."
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}"))
                self.update_status(f"Hata: {str(e)}")
        
        # Threading ile çalıştır (GUI blocking önleme)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def select_image(self):
        """Fotoğraf seçme dialog'unu açar"""
        file_path = filedialog.askopenfilename(
            title="Fotoğraf Seç",
            filetypes=[
                ("Resim dosyaları", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Tüm dosyalar", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            # Dosya adını göster (tam yol çok uzun olabilir)
            filename = file_path.split("/")[-1]
            self.photo_path_label.config(text=filename, fg="black")
            self.update_status(f"Fotoğraf seçildi: {filename}")
    
    def send_messages(self):
        """Mesaj gönderme buton handler'ı"""
        # Validasyon
        if not self.image_path:
            messagebox.showwarning("Uyarı", "Lütfen bir fotoğraf seçin!")
            return
        
        phone_numbers = self.phone_text.get("1.0", tk.END).strip()
        if not phone_numbers:
            messagebox.showwarning("Uyarı", "Lütfen telefon numaraları girin!")
            return
        
        message_text = self.message_text.get("1.0", tk.END).strip()
        
        if not self.whatsapp_sender:
            messagebox.showwarning("Uyarı", "Önce WhatsApp bağlantısı yapın!")
            return
        
        # Onay dialog'u
        response = messagebox.askyesno(
            "Onay",
            "Mesajları göndermek istediğinizden emin misiniz?"
        )
        
        if not response:
            return
        
        def run():
            try:
                self.root.after(0, lambda: self.send_button.config(state=tk.DISABLED, text="Gönderiliyor..."))
                self.whatsapp_sender.send_messages(
                    phone_numbers,
                    self.image_path,
                    message_text
                )
                self.root.after(0, lambda: self.send_button.config(
                    state=tk.NORMAL,
                    text="Mesajları Gönder"
                ))
                self.root.after(0, lambda: messagebox.showinfo("Tamamlandı", "Mesaj gönderme işlemi tamamlandı!"))
            except Exception as e:
                self.root.after(0, lambda: self.send_button.config(
                    state=tk.NORMAL,
                    text="Mesajları Gönder"
                ))
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}"))
                self.update_status(f"Hata: {str(e)}")
        
        # Threading ile çalıştır
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Uygulama kapanırken WebDriver'ı temizle"""
        if self.whatsapp_sender:
            self.whatsapp_sender.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WhatsAppGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

