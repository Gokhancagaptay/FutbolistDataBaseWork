import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from pymongo import MongoClient
import time
import logging

# Loglama Ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB bağlantısı (MongoDB Atlas)
client = MongoClient("mongodb+srv://cagaptay09:Futbolist12345678@futbolist.z3qcm.mongodb.net/?retryWrites=true&w=majority&appName=futbolist")
db = client['futbol-veri']

# Ligler
ligler = [
    {"_id": "ES-1", "lig_adi": "La Liga", "url": "https://fbref.com/en/comps/12/La-Liga-Stats"},
    {"_id": "IT-1", "lig_adi": "Serie A", "url": "https://fbref.com/en/comps/11/Serie-A-Stats"},
    {"_id": "DE-1", "lig_adi": "Bundesliga", "url": "https://fbref.com/en/comps/20/Bundesliga-Stats"},
    {"_id": "FR-1", "lig_adi": "Ligue 1", "url": "https://fbref.com/en/comps/13/Ligue-1-Stats"}
]

# Define the target teams
target_teams = [
    "Liverpool"
]

# URL ve header bilgileri
header = {
    "User  -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://fbref.com/"
}

session = requests.Session()
session.headers.update(header)

def fetch_url(url, sleep_time=2):
    """Verilen URL'den veri çek ve BeautifulSoup nesnesi döndür."""
    try:
        response = session.get(url)
        response.raise_for_status()
        time.sleep(sleep_time)  # İstekler arasında bekleme
        return BeautifulSoup(response.content, "lxml")
    except requests.exceptions.RequestException as e:
        logging.error(f"URL çekme hatası: {url} - {e}")
        return None

def fetch_season_stats(oyuncu_soup, is_goalkeeper=False):
    """Oyuncunun sezon bazındaki istatistiklerini döndür."""
    sezon_verileri = []

    # Doğru tabloyu seç (kaleci için "stats_keeper_dom_lg", diğer oyuncular için "stats_standard_dom_lg")
    tablo_id = "stats_keeper_dom_lg" if is_goalkeeper else "stats_standard_dom_lg"
    sezon_tablosu = oyuncu_soup.find("table", {"id": tablo_id})

    if sezon_tablosu:
        sezon_body = sezon_tablosu.find("tbody")
        sezon_satirlari = sezon_body.find_all("tr")

        for satir in sezon_satirlari:
            try:
                sezon = satir.find("th", {"data-stat": "year_id"}).get_text(strip=True)
                age = satir.find("td", {"data-stat": "age"}).get_text(strip=True) if satir.find("td", {"data-stat": "age"}) else None
                squad = satir.find("td", {"data-stat": "team"}).get_text(strip=True) if satir.find("td", {"data-stat": "team"}) else None
                country = satir.find("td", {"data-stat": "country"}).get_text(strip=True) if satir.find("td", {"data-stat": "country"}) else None
                comp = satir.find("td", {"data-stat": "comp_level"}).get_text(strip=True) if satir.find("td", {"data-stat": "comp_level"}) else None 
                lg_rank = satir.find("td", {"data-stat": "lg_finish"}).get_text(strip=True) if satir.find("td", {"data-stat": "lg_finish"}) else None

                if is_goalkeeper:
                    # Kaleciye özel istatistikler
                    mp = satir.find("td", {"data-stat": "gk_games"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_games"}) else None
                    starts = satir.find("td", {"data-stat": "gk_games_starts"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_games_starts"}) else None
                    mins = satir.find("td", {"data-stat": "gk_minutes"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_minutes"}) else None
                    ninetys = satir.find("td", {"data-stat": "minutes_90s"}).get_text(strip=True) if satir.find("td", {"data-stat": "minutes_90s"}) else None
                    gls = satir.find("td", {"data-stat": "gk_goals"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_goals"}) else None
                    ast = satir.find("td", {"data-stat": "gk_assists"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_assists"}) else None
                    g_a = satir.find("td", {"data-stat": "gk_goals_assists"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_goals_assists"}) else None
                    g_pk = satir.find("td", {"data-stat": "gk_goals_pen"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_goals_pen"}) else None
                    pk = satir.find("td", {"data-stat": "gk_pen_attempts"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_pen_attempts"}) else None
                    pkatt = satir.find("td", {"data-stat": "gk_pen_attempts_made"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_pen_attempts_made"}) else None
                    crdy = satir.find("td", {"data-stat": "gk_cards_yellow"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_cards_yellow"}) else None
                    crdr = satir.find("td", {"data-stat": "gk_cards_red"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_cards_red"}) else None
                    xg = satir.find("td", {"data-stat": "gk_xg"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_xg"}) else None
                    npxg = satir.find("td", {"data-stat": "gk_npxg"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_npxg"}) else None
                    xag = satir.find("td", {"data-stat": "gk_xg_assist"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_xg_assist"}) else None
                    npxg_xag = satir.find("td", {"data-stat": "gk_npxg_xg_assist"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_npxg_xg_assist"}) else None
                    prg_c = satir.find("td", {"data-stat": "gk_progressive_carries"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_progressive_carries"}) else None
                    prg_p = satir.find("td", {"data-stat": "gk_progressive_passes"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_progressive_passes"}) else None
                    prg_r = satir.find("td", {"data-stat": "gk_progressive_passes_received"}).get_text(strip=True) if satir.find("td", {"data-stat": "gk_progressive_passes_received"}) else None
                else:
                    # Diğer oyuncular için istatistikler
                    mp = satir.find("td", {" data-stat": "games"}).get_text(strip=True) if satir.find("td", {"data-stat": "games"}) else None
                    starts = satir.find("td", {"data-stat": "games_starts"}).get_text(strip=True) if satir.find("td", {"data-stat": "games_starts"}) else None
                    mins = satir.find("td", {"data-stat": "minutes"}).get_text(strip=True) if satir.find("td", {"data-stat": "minutes"}) else None
                    ninetys = satir.find("td", {"data-stat": "minutes_90s"}).get_text(strip=True) if satir.find("td", {"data-stat": "minutes_90s"}) else None
                    gls = satir.find("td", {"data-stat": "goals"}).get_text(strip=True) if satir.find("td", {"data-stat": "goals"}) else None
                    ast = satir.find("td", {"data-stat": "assists"}).get_text(strip=True) if satir.find("td", {"data-stat": "assists"}) else None
                    g_a = satir.find("td", {"data-stat": "goals_assists"}).get_text(strip=True) if satir.find("td", {"data-stat": "goals_assists"}) else None
                    g_pk = satir.find("td", {"data-stat": "goals_pens"}).get_text(strip=True) if satir.find("td", {"data-stat": "goals_pens"}) else None
                    pk = satir.find("td", {"data-stat": "pens_made"}).get_text(strip=True) if satir.find("td", {"data-stat": "pens_made"}) else None
                    pkatt = satir.find("td", {"data-stat": "pens_att"}).get_text(strip=True) if satir.find("td", {"data-stat": "pens_att"}) else None
                    crdy = satir.find("td", {"data-stat": "cards_yellow"}).get_text(strip=True) if satir.find("td", {"data-stat": "cards_yellow"}) else None
                    crdr = satir.find("td", {"data-stat": "cards_red"}).get_text(strip=True) if satir.find("td", {"data-stat": "cards_red"}) else None
                    xg = satir.find("td", {"data-stat": "xg"}).get_text(strip=True) if satir.find("td", {"data-stat": "xg"}) else None
                    npxg = satir.find("td", {"data-stat": "npxg"}).get_text(strip=True) if satir.find("td", {"data-stat": "npxg"}) else None
                    xag = satir.find("td", {"data-stat": "xg_assist"}).get_text(strip=True) if satir.find("td", {"data-stat": "xg_assist"}) else None
                    npxg_xag = satir.find("td", {"data-stat": "npxg_xg_assist"}).get_text(strip=True) if satir.find("td", {"data-stat": "npxg_xg_assist"}) else None
                    prg_c = satir.find("td", {"data-stat": "progressive_carries"}).get_text(strip=True) if satir.find("td", {"data-stat": "progressive_carries"}) else None
                    prg_p = satir.find("td", {"data-stat": "progressive_passes"}).get_text(strip=True) if satir.find("td", {"data-stat": "progressive_passes"}) else None
                    prg_r = satir.find("td", {"data-stat": "progressive_passes_received"}).get_text(strip=True) if satir.find("td", {"data-stat": "progressive_passes_received"}) else None

                sezon_verileri.append({
                    "season": sezon,
                    "age": age,
                    "squad": squad,
                    "country": country,
                    "comp": comp,
                    "lg_rank": lg_rank,
                    "mp": mp,
                    "starts": starts,
                    "mins": mins,
                    "90s": ninetys,
                    "goals": gls,
                    "assists": ast,
                    "g+a": g_a,
                    "g-pk": g_pk,
                    "pk": pk,
                    "pkatt": pkatt,
                    "xg": xg,
                    "npxg": npxg,
                    "xag": xag,
                    "npxg+xag": npxg_xag,
                    "yellow_cards": crdy,
                    "red_cards": crdr,
                    "prg_c": prg_c,
                    "prg_p": prg_p,
                    "prg_r": prg_r
                })
            except Exception as e:
                logging.error(f"Sezon verileri işlenirken hata oluştu: {e}")

    return sezon_verileri

# Ligler için döngü
for lig in ligler:
    lig_adi = lig["lig_adi"]
    lig_url = lig["url"]
    collection = db[lig_adi]
    # Takım detaylarını alma
    data = fetch_url(lig_url)
    if data:
        Takımlar = data.find("table", {"class": "stats_table"})
        if Takımlar:
            detay = Takımlar.find("tbody")
            takımlar_listesi = detay.find_all("tr")

            for takım in takımlar_listesi:
                takım_adı = takım.find("td", {"data-stat": "team"}).get_text(strip=True)    
                if takım_adı in target_teams:  # Only process teams in the target_teams list
                    Takım_url = takım.find("td", {"data-stat": "team"}).find("a")["href"] if takım.find("td", {"data-stat": "team"}) and takım.find("td", {"data-stat": "team"}).find("a") else None
                    collection2 = db[takım_adı]

                    if Takım_url:
                        Url_baslangıç = "https://fbref.com"
                        link_tamamı = Url_baslangıç + Takım_url
                        logging.info(f"Takım Sayfası: {link_tamamı}")

                        # Store team information in the team collection
                        team_data = {
                            "team_name": takım_adı,
                            "team_url": link_tamamı,
                            "players": []  # Initialize players array
                        }
                        team_collection_name = f"team_data-{lig_adi}-{takım_adı}"
                        team_collection = db[team_collection_name]

                        oyuncular_data = fetch_url(link_tamamı)
                        if oyuncular_data:
                            oyuncular_tablosu = oyuncular_data.find("table", {"class": "stats_table"})
                            if oyuncular_tablosu:
                                oyuncu_detay = oyuncular_tablosu.find("tbody")
                                oyuncular_listesi = oyuncu_detay.find_all("tr")

                                for oyuncu in oyuncular_listesi:
                                    time.sleep(2)
                                    oyuncu_link = oyuncu.find("th", {"data-stat": "player"}).find("a")["href"] if oyuncu.find("th", {"data-stat": "player"}) and oyuncu.find("a") else None

                                    if oyuncu_link:
                                        oyuncu_tamam_link = f"https://fbref.com{oyuncu_link}"
                                        logging.info(f"Oyuncu Linki: {oyuncu_tamam_link}")

                                        # Web ID çıkarma
                                        web_id = oyuncu_tamam_link.split("/")[5]  # Benzersiz ID'yi al
                                        logging.info(f"Web ID: {web_id}")

                                        oyuncu_soup = fetch_url(oyuncu_tamam_link)
                                        if oyuncu_soup:  # oyuncu_soup kontrolü yapılıyor
                                            oyuncu_bilgileri = oyuncu_soup.find("div", {"id": "meta"})
                                            if oyuncu_bilgileri:
                                                pozisyon = "Pozisyon bulunamadı"
                                                for p in oyuncu_bilgileri.find_all("p"):
                                                    text = p.get_text(strip=True)
                                                    if "Position:" in text:
                                                        pozisyon = text.split("▪")[0].replace("Position:", "").strip()
                                                pozisyon = pozisyon.split(",")[0].strip()
                                            is_goalkeeper = pozisyon == "GK"                   
                                            # Sezon verilerini çekme
                                            sezon_verileri = fetch_season_stats(oyuncu_soup, is_goalkeeper=is_goalkeeper)
                                            oyuncu_bilgileri = oyuncu_soup.find("div", {"id": "meta"})

                                            if oyuncu_bilgileri:
                                                try:
                                                    # Temel bilgiler
                                                    isim = oyuncu_bilgileri.find("h1").get_text(strip=True)
                                                    boy = "Boy bilgisi bulunamadı"
                                                    kilo = "Kilo bilgisi bulunamadı"
                                                    tercih_edilen_ayak = "Tercih edilen ayak bilgisi bulunamadı"
                                                    birth_date = None
                                                    yas = None
                                                    ulke = "Ülke bilgisi bulunamadı"
                                                    ulke_bayrak_url = None
                                                    maas = None
                                                    for p in oyuncu_bilgileri.find_all("p"):
                                                        text = p.get_text(strip=True)
                                                        if "cm" in text and "kg" in text:
                                                            boy_kilo_split = text.split(',')
                                                            boy = boy_kilo_split[0].strip()
                                                            kilo = boy_kilo_split[1].split("(")[0].strip()
                                                        if "Footed:" in text:
                                                            tercih_edilen_ayak = text.split("Footed:")[1].strip()

                                                    # Doğum Tarihi ve Yaş
                                                    birth_span = oyuncu_bilgileri.find("span", {"id": "necro-birth"})
                                                    if birth_span and 'data-birth' in birth_span.attrs:
                                                        birth_date = birth_span['data-birth']
                                                        birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
                                                        today = datetime.now()
                                                        yas = today.year - birth_datetime.year - ((today.month, today.day) < (birth_datetime.month, birth_datetime.day))
                                                        
                                                    # Maaş Bilgisi
                                                    maas_span = oyuncu_bilgileri.find("span", style=re.compile(r"color:#932a12"))
                                                    if maas_span:
                                                        maas = maas_span.get_text(strip=True)

                                                    # Ödülleri alma
                                                    oduller = []
                                                    oduller_listesi = oyuncu_soup.find("ul", {"id": "bling"})
                                                    if oduller_listesi:
                                                        oduller_li = oduller_listesi.find_all("li", {"class": "important poptip"})
                                                        for li in oduller_li:
                                                            odul = li.get("data-tip", "").strip()
                                                            if odul:
                                                                oduller.append(odul)
                                                    birth_location_spans = oyuncu_bilgileri.find_all("span")
                                                    for span in birth_location_spans:
                                                        text = span.get_text(strip=True)
                                                        if "in" in text and "," in text:
                                                            ulke_parts = text.split(",")
                                                            if len(ulke_parts) > 1:
                                                                ulke = ulke_parts[-1].strip()
                                                                break

                                                    ulke_span = oyuncu_bilgileri.find("span", class_="f-i")
                                                    if ulke_span and 'style' in ulke_span.attrs:
                                                        match = re.search(r"url\('([^']+)'\)", ulke_span['style'])
                                                        if match:
                                                            ulke_bayrak_url = match.group(1)

                                                    # Scouting raporu
                                                    scouting_verileri = []
                                                    scouting_tablolari = oyuncu_soup.find_all("table", {"class": "stats_table", "id": True})

                                                    if scouting_tablolari:
                                                        for tablo in scouting_tablolari:
                                                            try:
                                                                tablo_id = tablo.get("id")
                                                                if tablo_id and f"scout_summary" in tablo_id and not is_goalkeeper:  # Doğru tabloyu kontrol et ve kaleci değilse
                                                                    rows = tablo.find("tbody").find_all("tr")
                                                                    for row in rows:
                                                                        try:
                                                                            istatistik_adi = row.find("th", {"data-stat": "statistic"}).get_text(strip=True)
                                                                            istatistik_aciklama = row.find("th", {"data-stat": "statistic"}).get("data-tip", "").strip()
                                                                            per90 = row.find("td", {"data-stat": "per90"}).get_text(strip=True) if row.find("td", {"data-stat": "per90"}) else "Veri yok"
                                                                            percentile = row.find("td", {"data-stat": "percentile"}).get_text(strip=True) if row.find("td", {"data-stat": "percentile"}) else "Veri yok"

                                                                            scouting_verileri.append({
                                                                                "istatistik": istatistik_adi,
                                                                                "aciklama": istatistik_aciklama or "Açıklama bulunamadı",
                                                                                "per90": per90,
                                                                                "percentile": percentile
                                                                            })
                                                                        except Exception as row_error:
                                                                            logging.error(f"Satır işlenirken hata oluştu: {row_error}")

                                                            except Exception as table_error:
                                                                logging.error(f"Tablo işlenirken hata oluştu: {table_error}")

                                                    # **Kaleciye Özel Scouting Verileri**
                                                    if is_goalkeeper:
                                                        goalkeeper_scouting_verileri = []
                                                        gk_scouting_table = oyuncu_soup.find("table", {"id": "scout_summary_GK"})
                                                        if gk_scouting_table:
                                                            gk_rows = gk_scouting_table.find("tbody").find_all("tr")
                                                            for gk_row in gk_rows:
                                                                try:
                                                                    gk_stat_name = gk_row.find("th", {"data-stat": "statistic"}).get_text(strip=True)
                                                                    gk_stat_value = gk_row.find("td", {"data-stat": "per90"}).get_text(strip=True) if gk_row.find("td", {"data-stat": "per90"}) else "Veri yok"
                                                                    gk_percentile = gk_row.find("td", {"data-stat": "percentile"}).get_text(strip=True) if gk_row.find("td", {"data-stat": "percentile"}) else "Veri yok"
                                                                    
                                                                    goalkeeper_scouting_verileri.append({
                                                                        "istatistik": gk_stat_name,
                                                                        "per90": gk_stat_value,
                                                                        "percentile": gk_percentile
                                                                    })
                                                                except Exception as gk_row_error:
                                                                    logging.error(f"Kaleci satırı işlenirken hata oluştu: {gk_row_error}")

                                                    # Kaleciye özel scouting verilerini ana scouting verilerine ekleyin
                                                    scouting_verileri.extend(goalkeeper_scouting_verileri)

                                                    # MongoDB'ye veri ekleme
                                                    oyuncu_verisi = {
                                                        "isim": isim,
                                                        "pozisyon": pozisyon,
                                                        "boy": boy,
                                                        "kilo": kilo,
                                                        "dogum_tarihi": birth_date,
                                                        "yas": yas,
                                                        "ulke": ulke,
                                                        "tercih_edilen_ayak": tercih_edilen_ayak,
                                                        "oduller": oduller,
                                                        "maas": maas,
                                                        "ulke_bayrak_url": ulke_bayrak_url,
                                                        "web_id": web_id,
                                                        "scouting_raporu": scouting_verileri,
                                                        "sezon_verileri": sezon_verileri, 
                                                    }

                                                    # Update the team document to include the player with new naming convention
                                                    team_collection_name = f"oyuncu_verileri-{lig_adi}-{takım_adı}-data"
                                                    team_collection = db[team_collection_name]
                                                    collection.update_one(
                                                        {"team_name": takım_adı},
                                                        {"$set": {f"players.{isim}": oyuncu_verisi}},
                                                        upsert=True
                                                    )
                                                    logging.info(f"Oyuncu verisi eklendi: {isim} - Takım: {takım_adı} - Lig: {lig_adi}")
                                                except Exception as e:
                                                    logging.error(f"Bilgi çıkarma hatası: {e}")
    else:
        logging.error(f"{lig_adi} takımlar tablosu bulunamadı")