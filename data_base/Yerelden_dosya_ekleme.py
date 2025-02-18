from pymongo import MongoClient
import bson

# MongoDB Atlas bağlantısını yapın
client = MongoClient("mongodb+srv://cagaptay09:Futbolist12345678@futbolist.z3qcm.mongodb.net/?retryWrites=true&w=majority&appName=futbolist")
db = client["most_valuable_player"]  # Veritabanı adı
collection = db["list"]  # Koleksiyon adı

# BSON dosyasını okuyun ve MongoDB'ye yükleyin
bson_file_path = "C:\\Users\\Gökhan\\Desktop\\transfermarkt_db\\players.bson"

with open(bson_file_path, "rb") as bson_file:
    data = bson.decode_all(bson_file.read())  # BSON verisini çözümle
    collection.insert_many(data)  # Veriyi MongoDB'ye ekle

print("BSON dosyası MongoDB'ye başarıyla yüklendi.")
