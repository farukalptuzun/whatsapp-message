import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def parse_phone_numbers(phone_input):
    """
    Telefon numaralarını parse eder. Virgül ve satır sonu ile ayrılmış numaraları destekler.
    
    Args:
        phone_input: Kullanıcının girdiği telefon numaraları string'i
        
    Returns:
        list: Temizlenmiş telefon numaraları listesi
    """
    # Satır sonlarını virgül ile değiştir
    normalized = phone_input.replace('\n', ',').replace('\r', ',')
    # Virgül ile ayır
    numbers = [num.strip() for num in normalized.split(',')]
    # Boş string'leri filtrele
    numbers = [num for num in numbers if num]
    return numbers


class WhatsAppSender:
    def __init__(self, status_callback=None):
        """
        WhatsApp Web otomasyon sınıfı
        
        Args:
            status_callback: Durum güncellemeleri için callback fonksiyonu (optional)
        """
        self.driver = None
        self.status_callback = status_callback
        self.user_data_dir = os.path.join(os.path.expanduser("~"), ".whatsapp_automation")
        
    def _update_status(self, message):
        """Durum mesajını callback ile gönderir"""
        if self.status_callback:
            self.status_callback(message)
    
    def _setup_driver(self):
        """Chrome WebDriver'ı yapılandırır ve başlatır"""
        chrome_options = Options()
        
        # User data directory ile oturumun kalıcı olmasını sağla
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # WhatsApp Web'in düzgün çalışması için gerekli ayarlar
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            return True
        except Exception as e:
            self._update_status(f"ChromeDriver hatası: {str(e)}")
            return False
    
    def open_whatsapp_web(self):
        """WhatsApp Web'i Chrome'da açar"""
        if not self.driver:
            if not self._setup_driver():
                return False
        
        try:
            self._update_status("WhatsApp Web açılıyor...")
            self.driver.get("https://web.whatsapp.com")
            
            # QR kod sayfasının yüklenmesini bekle
            time.sleep(3)
            self._update_status("WhatsApp Web açıldı. Lütfen QR kodu tarayın.")
            return True
        except Exception as e:
            self._update_status(f"WhatsApp Web açılırken hata: {str(e)}")
            return False
    
    def wait_for_login(self, timeout=60):
        """Kullanıcının WhatsApp'ı taramasını bekler"""
        try:
            self._update_status("QR kod taraması bekleniyor...")
            # QR kod görüntüsünün kaybolmasını bekle (giriş yapıldığında)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="chat-list"]'))
            )
            self._update_status("Giriş başarılı! Mesaj göndermeye hazırsınız.")
            return True
        except TimeoutException:
            self._update_status("Giriş zaman aşımına uğradı. Lütfen tekrar deneyin.")
            return False
    
    def search_contact(self, phone_number):
        """URL kullanarak belirtilen telefon numarasının sohbet penceresini açar"""
        try:
            # Telefon numarasını temizle (boşluk, tire, parantez vb. karakterleri kaldır)
            cleaned_number = ''.join(filter(str.isdigit, phone_number))
            
            if not cleaned_number:
                self._update_status(f"Geçersiz telefon numarası: {phone_number}")
                return False
            
            # WhatsApp Web URL formatı ile sohbet penceresini aç
            whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_number}"
            self.driver.get(whatsapp_url)
            
            # Sayfanın yüklenmesini ve sohbet penceresinin açılmasını bekle
            time.sleep(3)
            
            # Sohbet penceresinin açıldığını kontrol et (mesaj kutusu görünüyor mu?)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
                )
                return True
            except TimeoutException:
                self._update_status(f"Sohbet penceresi açılamadı: {phone_number}")
                return False
                
        except Exception as e:
            self._update_status(f"Kişi aranırken hata: {str(e)}")
            return False
    
    def send_message_with_image(self, image_path, message_text):
        """Fotoğraf ve mesaj gönderir"""
        try:
            # Ek (attachment) butonunu bul ve tıkla
            # WhatsApp Web'de farklı ikonlar kullanılabiliyor (attach, clip, paperclip)
            try:
                attach_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-icon="attach"], span[data-icon="clip"], span[data-icon="paperclip"]'))
                )
            except TimeoutException:
                # Alternatif: buton yerine doğrudan input'a tıklamayı dene
                attach_button = self.driver.find_element(By.CSS_SELECTOR, 'div[title*="Attach"], div[title*="Ekle"]')
            attach_button.click()
            time.sleep(1)
            
            # Fotoğraf seçeneğini bul (file input genellikle gizli olduğu için presence kullanıyoruz)
            try:
                # Fotoğraf/video input elementi bul
                photo_option = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[accept*="image"], input[type="file"]'))
                )
            except TimeoutException:
                # Alternatif: doğrudan input elementi bul
                try:
                    photo_option = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                except NoSuchElementException:
                    raise Exception("Fotoğraf yükleme input'u bulunamadı")
            
            # Fotoğrafı yükle
            photo_option.send_keys(os.path.abspath(image_path))
            time.sleep(2)  # Fotoğrafın yüklenmesini bekle
            
            # Mesaj metnini yaz (varsa)
            if message_text:
                message_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
                )
                message_box.click()
                message_box.send_keys(message_text)
                time.sleep(0.5)
            
            # Gönder butonuna tıkla
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-icon="send"]'))
            )
            send_button.click()
            time.sleep(2)  # Mesajın gönderilmesini bekle
            
            return True
            
        except Exception as e:
            self._update_status(f"Mesaj gönderilirken hata: {str(e)}")
            return False
    
    def send_messages(self, phone_numbers, image_path, message_text):
        """Tüm numaralara mesaj gönderir (her mesaj arasında 5 saniye bekler)"""
        if not self.driver:
            self._update_status("Önce WhatsApp Web'i açın!")
            return False
        
        # Telefon numaralarını parse et
        numbers = parse_phone_numbers(phone_numbers)
        
        if not numbers:
            self._update_status("Geçerli telefon numarası bulunamadı!")
            return False
        
        if not os.path.exists(image_path):
            self._update_status(f"Fotoğraf dosyası bulunamadı: {image_path}")
            return False
        
        total = len(numbers)
        successful = 0
        failed = 0
        
        for idx, phone_number in enumerate(numbers, 1):
            self._update_status(f"Mesaj gönderiliyor ({idx}/{total}): {phone_number}")
            
            # Kişiyi ara ve seç
            if self.search_contact(phone_number):
                # Fotoğraf ve mesajı gönder
                if self.send_message_with_image(image_path, message_text):
                    successful += 1
                    self._update_status(f"Mesaj gönderildi: {phone_number}")
                else:
                    failed += 1
                    self._update_status(f"Mesaj gönderilemedi: {phone_number}")
            else:
                failed += 1
            
            # Son mesaj değilse 5 saniye bekle
            if idx < total:
                self._update_status("5 saniye bekleniyor...")
                time.sleep(5)
        
        self._update_status(f"Tamamlandı! Başarılı: {successful}, Başarısız: {failed}")
        return True
    
    def close(self):
        """WebDriver'ı kapatır"""
        if self.driver:
            self.driver.quit()
            self.driver = None

