# AskGPT: Ekran Görüntüsü Tabanlı AI Asistan

## Proje Hakkında
-AskGPT, kullanıcıların ekran görüntüsü alarak yapay zeka ile etkileşime geçmesini sağlayan bir masaüstü uygulamasıdır. -Google'ın Gemini AI modeli kullanılarak geliştirilmiştir.
-Chat yapısı sayesinde kullanıcının eski sorularını da hafızasında tutar.
-Birden fazla ekranı destekler.
-Herhangi bir işlem yaparken ekranın istediğiniz kısmının görüntüsünü alarak tetiklenir.

## Özellikler
- 🖼️ Kolay ekran görüntüsü alma
- ⌨️ Özelleştirilebilir kısayol tuşu
- 💬 Doğal dil modeli ile sohbet
- 🔄 Devam eden sohbet desteği
- 📝 Markdown formatında yanıtlar
- 🎨 Modern ve kullanıcı dostu arayüz
- 💬 İstenildiğinde temizlenebilen sohbet geçmişi
- 📝 Sunucudan İstenildiğinde temizlenebilen ekran resimleri (siz silmeseniz de google birkaç gün sonra otomatik olarak siler)
- ⌨️ Gelen cevabın görüntü büyüklüğünü değiştirme ve hafızada tutma

## Teknolojiler
- Python 3.x
- Tkinter (GUI)
- Google Gemini AI API
- PIL (Python Imaging Library)
- Win32API (Windows ekran yakalama)

## Kurulum
1. Depoyu klonlayın
```bash
git clone https://github.com/drdoof2019/AskGpt-Btk-Hackatlon.git
```

2. Gerekli paketleri yükleyin
```bash
pip install -r requirements.txt
```

3. `.env` dosyası oluşturun ve Google API anahtarınızı ekleyin
```
GOOGLE_API_KEY=your_api_key_here
```

4. Uygulamayı çalıştırın
```bash
python inty.py
```

## Kullanım
1. Programı başlatın ve giriş yapın
2. Bir kısayol tuşu atayın
3. "Programı Başlat" butonuna tıklayın
4. Atadığınız tuşa çift basarak ekran görüntüsü alın
5. Sorunuzu yazın ve AI'dan yanıt alın

## Lisans
Bu proje MIT lisansı altında lisanslanmıştır.