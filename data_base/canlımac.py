import requests
from pymongo import MongoClient

# API bilgileri
url = "https://footapi7.p.rapidapi.com/api/matches/live"
headers = {
    "X-RapidAPI-Key": "c8cab33e7bmshf6f28c18d5baab9p173872jsn9ee7c30dbf5d",
    "X-RapidAPI-Host": "footapi7.p.rapidapi.com"
}

# MongoDB Atlas bağlantısı
# <username>, <password>, ve <cluster_url> bilgilerini kendi Atlas veritabanınıza göre güncelleyin.
mongo_uri = "mongodb+srv://cagaptay09:Futbolist12345678@futbolist.z3qcm.mongodb.net/?retryWrites=true&w=majority&appName=futbolist"
client = MongoClient(mongo_uri)
db = client["match_schedules"]  # Veritabanı adı
collection = db["schedules"]  # Koleksiyon adı

try:
    # API'den veri çekme
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()  # JSON formatında veriyi al

    # MongoDB'ye kaydetme
    if isinstance(data, list):  # Eğer veri bir liste ise
        collection.insert_many(data)
    elif isinstance(data, dict):  # Eğer veri bir sözlük ise
        collection.insert_one(data)

    print("Veriler başarıyla MongoDB Atlas'a kaydedildi.")
except requests.exceptions.RequestException as e:
    print(f"API isteği başarısız oldu: {e}")
except Exception as e:
    print(f"MongoDB işlemi sırasında hata oluştu: {e}")
