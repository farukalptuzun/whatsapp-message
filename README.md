# WhatsApp Mesaj Gönderme Uygulaması

WhatsApp Web üzerinden toplu mesaj gönderme uygulaması. Python, Tkinter ve Selenium kullanılarak geliştirilmiştir.

## Özellikler

- WhatsApp Web'i Chrome tarayıcısında otomatik açma
- Fotoğraf ve metin mesajı gönderme
- Birden fazla telefon numarasına toplu mesaj gönderme
- Her mesaj arasında 5 saniye otomatik bekleme
- Kullanıcı dostu GUI arayüzü
- Virgül veya satır sonu ile ayrılmış telefon numaraları desteği

## Gereksinimler

- Python 3.7 veya üzeri
- Chrome tarayıcısı
- ChromeDriver (Selenium ile kullanım için)

## Kurulum

1. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

2. ChromeDriver'ı kurun:
   - ChromeDriver'ı [ChromeDriver indirme sayfasından](https://chromedriver.chromium.org/downloads) indirin
   - Sistem PATH'inize ekleyin veya proje dizinine koyun
   - Alternatif olarak, `webdriver-manager` kullanabilirsiniz (gelecekte eklenebilir)

## Kullanım

1. Uygulamayı başlatın:
```bash
python main.py
```

2. **WhatsApp Bağlantısı** butonuna tıklayın
   - Chrome tarayıcısında WhatsApp Web açılacak
   - QR kodu telefonunuzla tarayın

3. Fotoğraf seçin:
   - **Fotoğraf Seç** butonuna tıklayın
   - Göndermek istediğiniz fotoğrafı seçin

4. Mesaj metnini yazın (isteğe bağlı)

5. Telefon numaralarını girin:
   - Virgül ile ayrılmış: `5551234567, 5559876543, 5551112233`
   - Satır sonu ile ayrılmış: Her satıra bir numara
   - Karışık: Her ikisini de kullanabilirsiniz

6. **Mesajları Gönder** butonuna tıklayın

## Önemli Notlar

- İlk kullanımda WhatsApp Web'e giriş yapmanız gerekecektir (QR kod)
- Oturum bilgileri `~/.whatsapp_automation` dizininde saklanır
- Her mesaj arasında 5 saniye bekleme süresi vardır (spam önleme)
- Telefon numaraları ülke kodu olmadan girilmelidir (örn: 5551234567)
- WhatsApp'ın hizmet şartlarına uygun kullanın

## Sorun Giderme

- **ChromeDriver bulunamıyor**: ChromeDriver'ın sistem PATH'inde olduğundan emin olun
- **Mesaj gönderilemiyor**: WhatsApp Web'e başarıyla giriş yaptığınızdan emin olun
- **Numara bulunamıyor**: Telefon numarasının doğru formatta olduğundan ve WhatsApp'ta kayıtlı olduğundan emin olun

## Güvenlik

- Bu uygulama yalnızca kişisel kullanım içindir
- WhatsApp'ın hizmet şartlarına uyun
- Spam göndermeyin
