# AskGPT: Ekran Görüntüsü Tabanlı AI Asistan

Burada BTKAkademi bünyesindeki Hackatlon25 yarışmasına yönelik kısa tanıtım yapacağım.  
Programın versiyon dosyaları içinde readme'leri bulabilirsiniz.  

## Neden 2 versiyon?
2. versiyon MCP(Model Context Protocol) destekler. Bu teknolojiyi destekleyebilmek için gemini langchain kullanır.
Yarışma kurallarını okuduğumuzda mcp-use kütüphanesini kullanıp/kullanamayacağımız konusunda muallakta kaldık bu yüzden 2 versiyon çıkardık. Eğer olumsuz bir durum varsa 1. versiyonu baz alabilirsiniz.

## Kısaca ne işe yarar?
AskGPT windows desktopta birden fazla ekranla çalışabilir şekilde tasarlanmış bir AI asistan. Günümüzde llm'lerin en büyük problemlerinden bazıları knowledge cut-off tarihleri ve halüsinasyon görmeleridir.
AskGPT her 2 sorununda çözümü için geliştirilmiştir.   
Çözüm1: Kullanıcı anlık olarak yaşadığı problemi sadece chatbot'a yazarak açıklamaz, ekran görüntüsü ile destekler bu sayede daha gerçekçi ve tutarlı cevaplar alır.  
Çözüm2: Kullanıcı MCP desteği ile güncel dökümantasyonlara - anlık bilgilere ulaşabilir.  
Kısaca ister elektronik devre kartı tasarlayın, ister solidworkste çizim yapın, veya kıyafet tasarlayın, isterseniz chrome'da bir ayar arayın, kod yazın vs. hatta oyunlarda bir görevde cevabı arayın, istediğiniz her konuda destek olmak için AskGPT hazır.  

## Kısaca nasıl kullanılır?
Program çalıştığında k.adı şifre ile giriş yapılır (şuan için test-test), klavyeden istenilen bir tuş atanır.
Tuşa çift basıldığında program tetiklenir ve ekran(lar)ın istenilen yerinden ekran görüntüsü alınabilir. Müteakip olarak prompt girme ekranı çıkar ve istenilen prompt yazılıp enter'a basılır.
AI'dan cevap geldiğinde program belirir ve kullanıcı cevabı okur. İsterse yazıları büyütüp küçültebilir(1 kez ayarlayınca hep hatırlar). Ekstra bir sorusu yoksa esc tuşuna basarak kapatabilir,
varsa prompt girme ekranından sorusunu sorup chat'e devam edebilir.

## Tanıtım videoları:
Kısa süre limitine sığdırmak için olabildiğince hızlı bir şekilde çekildiler. Umarız anlaşılır olmuştur.
