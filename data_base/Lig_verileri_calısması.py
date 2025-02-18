
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB bağlantısı
MONGODB_URI = "mongodb+srv://cagaptay09:Futbolist12345678@futbolist.z3qcm.mongodb.net/?retryWrites=true&w=majority&appName=futbolist"
try:
    client = MongoClient(MONGODB_URI)
    db = client["lig_durumu"]
    collection = db["Lig_Durumu"]
    print("MongoDB'ye başarıyla bağlanıldı ve koleksiyon erişildi.")
except Exception as e:
    print(f"MongoDB bağlantı hatası: {e}")
    exit()

# Lig verilerini çekmek için URL ve header
ligler = [
    {"_id": "GB-1", "lig_adi": "Premier League", "url": "https://fbref.com/en/comps/9/Premier-League-Stats"},
    {"_id": "ES-1", "lig_adi": "La Liga", "url": "https://fbref.com/en/comps/12/La-Liga-Stats"},
    {"_id": "IT-1", "lig_adi": "Serie A", "url": "https://fbref.com/en/comps/11/Serie-A-Stats"},
    {"_id": "DE-1", "lig_adi": "Bundesliga", "url": "https://fbref.com/en/comps/20/Bundesliga-Stats"},
    {"_id": "FR-1", "lig_adi": "Ligue 1", "url": "https://fbref.com/en/comps/13/Ligue-1-Stats"}
]

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3"
}

for lig in ligler:
    try:
        print(f"{lig['lig_adi']} verileri çekiliyor...")
        # Web sayfasını çekme
        response = requests.get(lig["url"], headers=header)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Doğru tabloyu bulma
        table = soup.find("table", {"class": "stats_table"})
        if table:
            teams = []
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                takim_amblem = row.find("td", {"data-stat": "team"}).find("img")["src"] if row.find("td", {"data-stat": "team"}) and row.find("td", {"data-stat": "team"}).find("img") else None
                team_name = row.find("td", {"data-stat": "team"}).find("a").text.strip() if row.find("td", {"data-stat": "team"}) and row.find("td", {"data-stat": "team"}).find("a") else None
                played = row.find("td", {"data-stat": "games"}).text.strip() if row.find("td", {"data-stat": "games"}) else None
                wins = row.find("td", {"data-stat": "wins"}).text.strip() if row.find("td", {"data-stat": "wins"}) else None
                draws = row.find("td", {"data-stat": "ties"}).text.strip() if row.find("td", {"data-stat": "ties"}) else None
                losses = row.find("td", {"data-stat": "losses"}).text.strip() if row.find("td", {"data-stat": "losses"}) else None
                goals_for = row.find("td", {"data-stat": "goals_for"}).text.strip() if row.find("td", {"data-stat": "goals_for"}) else None
                goals_against = row.find("td", {"data-stat": "goals_against"}).text.strip() if row.find("td", {"data-stat": "goals_against"}) else None
                goal_diff = row.find("td", {"data-stat": "goal_diff"}).text.strip() if row.find("td", {"data-stat": "goal_diff"}) else None
                points = row.find("td", {"data-stat": "points"}).text.strip() if row.find("td", {"data-stat": "points"}) else None
                mac_basi_puan = row.find("td", {"data-stat": "points_avg"}).text.strip() if row.find("td", {"data-stat": "points_avg"}) else None
                beklenen_gol = row.find("td", {"data-stat": "xg_for"}).text.strip() if row.find("td", {"data-stat": "xg_for"}) else None
                beklenen_gol_sayisi_karsiti = row.find("td", {"data-stat": "xg_against"}).text.strip() if row.find("td", {"data-stat": "xg_against"}) else None
                beklenen_gol_farki = row.find("td", {"data-stat": "xg_diff"}).text.strip() if row.find("td", {"data-stat": "xg_diff"}) else None
                beklenen_gol_farki_90 = row.find("td", {"data-stat": "xg_diff_per90"}).text.strip() if row.find("td", {"data-stat": "xg_diff_per90"}) else None
                son_5_mac_div = row.find("td", {"data-stat": "last_5"})
                if son_5_mac_div:
                    son_5_mac = ''.join([a.text for a in son_5_mac_div.find_all("a")])
                else:
                    son_5_mac = None
                seyirci = row.find("td", {"data-stat": "attendance_per_g"}).text.strip() if row.find("td", {"data-stat": "attendance_per_g"}) else None
                top_scorer_div = row.find("td", {"data-stat": "top_team_scorers"})
                if top_scorer_div:
                    top_scorers = top_scorer_div.find_all("a")
                    top_scorer_names = [scorer.text.strip() for scorer in top_scorers]
                    top_scorer_score = top_scorer_div.find("span").text.strip() if top_scorer_div.find("span") else None
                else:
                    top_scorer_names = []
                    top_scorer_score = None
                goalkeepers_div = row.find("td", {"data-stat": "top_keeper"})
                if goalkeepers_div:
                    goalkeepers = goalkeepers_div.find_all("a")
                    goalkeeper_names = [keeper.text.strip() for keeper in goalkeepers]
                else:
                    goalkeeper_names = []

                if team_name:
                    teams.append({
                        "team_name": team_name,
                        "team_logo": takim_amblem,
                        "played": played,
                        "wins": wins,
                        "draws": draws,
                        "losses": losses,
                        "goals_for": goals_for,
                        "goals_against": goals_against,
                        "goal_diff": goal_diff,
                        "points": points,
                        "points_per_match": mac_basi_puan,
                        "xg_for": beklenen_gol,
                        "xg_against": beklenen_gol_sayisi_karsiti,
                        "xg_diff": beklenen_gol_farki,
                        "xg_diff_per90": beklenen_gol_farki_90,
                        "last_5_matches": son_5_mac,
                        "attendance_per_game": seyirci,
                        "top_scorers": {
                            "names": top_scorer_names,
                            "score": top_scorer_score
                        },
                        "goalkeepers": goalkeeper_names
                    })

            # Veritabanına kaydetme
            lig_document = {
                "_id": lig["_id"],
                "lig_adi": lig["lig_adi"],
                "teams": teams
            }
            collection.update_one({"_id": lig["_id"]}, {"$set": lig_document}, upsert=True)
            print(f"{lig['lig_adi']} bilgileri başarıyla kaydedildi.")

    except Exception as e:
        print(f"Hata oluştu: {e}")

print("Tüm lig verileri başarıyla işlendi ve MongoDB'ye kaydedildi.")

