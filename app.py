from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- LİG VE TAKIM VERİ SETİ (Kullanıcı Kolaylığı İçin) ---
SUPPORTED_LEAGUES = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"},
        {"id": 2821, "name": "Başakşehir"}, {"id": 4153, "name": "Eyüpspor"},
        {"id": 2824, "name": "Konyaspor"}, {"id": 2826, "name": "Antalyaspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Manchester City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Manchester United"},
        {"id": 40, "name": "Chelsea"}, {"id": 33, "name": "Tottenham"},
        {"id": 34, "name": "Aston Villa"}, {"id": 39, "name": "Newcastle"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"},
        {"id": 2836, "name": "Atletico Madrid"}, {"id": 2816, "name": "Girona"},
        {"id": 2825, "name": "Real Sociedad"}, {"id": 2833, "name": "Villarreal"}
    ],
    "Bundesliga": [
        {"id": 2673, "name": "Bayern München"}, {"id": 2671, "name": "Bayer Leverkusen"},
        {"id": 2677, "name": "Borussia Dortmund"}, {"id": 2672, "name": "RB Leipzig"},
        {"id": 2670, "name": "Stuttgart"}, {"id": 2674, "name": "Eintracht Frankfurt"}
    ],
    "Şampiyonlar Ligi": [
        {"id": 2673, "name": "Real Madrid"}, {"id": 2675, "name": "Man City"},
        {"id": 2671, "name": "Inter"}, {"id": 2674, "name": "PSG"},
        {"id": 2677, "name": "Dortmund"}, {"id": 2829, "name": "Barcelona"}
    ],
    "Avrupa Ligi": [
        {"id": 2818, "name": "Fenerbahçe"}, {"id": 2819, "name": "Beşiktaş"},
        {"id": 42, "name": "Arsenal"}, {"id": 38, "name": "Man United"},
        {"id": 2714, "name": "Roma"}, {"id": 2674, "name": "Lyon"}
    ],
    "Konferans Ligi": [
        {"id": 2822, "name": "Başakşehir"}, {"id": 40, "name": "Chelsea"},
        {"id": 2714, "name": "Fiorentina"}, {"id": 2684, "name": "Panathinaikos"}
    ]
}

@app.route('/')
def index():
    # Ana sayfada lig listesini HTML'e gönderiyoruz
    return render_template('index.html', leagues=SUPPORTED_LEAGUES)

@app.route('/analiz', methods=['POST'])
def analiz():
    team_id = request.form.get('team_id')
    
    if not team_id:
        return "Hata: Lütfen bir takım seçin!", 400

    # API İsteği ve Hata Kontrolü
    api_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    headers = {
        "User-Agent": "Mozilla/5.0", # API engellemesini önlemek için
        # Eğer varsa API anahtarını buraya ekle: "X-RapidAPI-Key": "ANAHTARIN"
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        # 401: Yetkisiz, 403: Yasaklı, 429: Kota Dolu
        if response.status_code != 200:
            return f"Veri çekilemedi. Hata kodu: {response.status_code}. API anahtarın bitmiş olabilir veya ID yanlış.", 500
            
        data = response.json()
        
        # Analiz mantığını burada çalıştır (Örn: Poisson Analizi)
        # result = poisson_analizi(data)
        
        return jsonify({"durum": "Başarılı", "team_id": team_id, "data": data})

    except requests.exceptions.RequestException as e:
        return f"Bağlantı Hatası: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
