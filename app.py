from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- LİG VE TAKIM VERİ SETİ ---
SUPPORTED_LEAGUES = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"},
        {"id": 2821, "name": "Başakşehir"}, {"id": 4153, "name": "Eyüpspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Manchester City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Manchester United"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"},
        {"id": 2836, "name": "Atletico Madrid"}
    ],
    "Bundesliga": [
        {"id": 2673, "name": "Bayern München"}, {"id": 2671, "name": "Bayer Leverkusen"},
        {"id": 2677, "name": "Borussia Dortmund"}
    ],
    "Şampiyonlar Ligi": [
        {"id": 2673, "name": "Real Madrid"}, {"id": 2675, "name": "Man City"},
        {"id": 2671, "name": "Inter"}, {"id": 2674, "name": "PSG"}
    ],
    "Avrupa Ligi": [
        {"id": 2818, "name": "Fenerbahçe"}, {"id": 2819, "name": "Beşiktaş"},
        {"id": 42, "name": "Arsenal"}, {"id": 38, "name": "Man United"}
    ],
    "Konferans Ligi": [
        {"id": 2822, "name": "Başakşehir"}, {"id": 40, "name": "Chelsea"}
    ]
}

@app.route('/')
def index():
    # leagues değişkenini HTML tarafına gönderiyoruz
    return render_template('index.html', leagues=SUPPORTED_LEAGUES)

@app.route('/analiz', methods=['POST'])
def analiz():
    team_id = request.form.get('team_id')
    if not team_id:
        return jsonify({"hata": "Lütfen bir takım seçin!"}), 400

    api_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return jsonify({"hata": f"API Hatası: {response.status_code}. Kota dolmuş olabilir."}), 500
            
        data = response.json()
        return jsonify({"durum": "Başarılı", "data": data})

    except Exception as e:
        return jsonify({"hata": f"Sistem Hatası: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
