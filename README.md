# Basit Crawler Tabanlı Arama Motoru

Bu proje, başlangıç URL'lerinden yola çıkarak web sayfalarını tarayan ve içeriklerini indeksleyen basit bir komut satırı arama motoru sağlar. Taranan sayfalar in-memory TF-IDF indeksine eklenir ve hem tek seferlik sorgu hem de etkileşimli arama desteği sunar.

## Kurulum

Gerekli bağımlılıkları kurmak için Python 3.9+ ortamında aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

## Kullanım

Komut satırı arayüzünü `python -m crawler_search.cli` ile başlatabilirsiniz:

```bash
python -m crawler_search.cli https://ornek.com --max-pages 10 --allowed-domains ornek.com --interactive
```

Başlıca seçenekler:

- `start_urls`: Taramaya başlanacak URL listesi (zorunlu).
- `--max-pages`: Tarama sırasında ziyaret edilecek en fazla sayfa sayısı.
- `--allowed-domains`: Taramanın izinli olduğu alan adları.
- `--delay`: İstekler arasındaki bekleme süresi.
- `--timeout`: HTTP istek zaman aşımı süresi.
- `--interactive`: Taramadan sonra etkileşimli sorgu modunu başlatır.
- `--query`: Tek bir sorgu çalıştırır.
- `--export`: Taranan belgelerin kısa özetini JSON olarak dışa aktarır.

## Örnek

Tek seferlik bir sorgu çalıştırmak için:

```bash
python -m crawler_search.cli https://docs.python.org --max-pages 5 --allowed-domains python.org --query "asyncio"
```

## Gereksinimler

- `requests`
- `beautifulsoup4`

Bu bağımlılıklar `requirements.txt` dosyasında listelenmiştir.
