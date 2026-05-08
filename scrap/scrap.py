import requests
from bs4 import BeautifulSoup

def download_fight_club_script():
    url = "https://imsdb.com/scripts/Fight-Club.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Sur IMSDb, le script est généralement dans une balise <pre>
    script_content = soup.find('pre')
    
    if script_content:
        with open("fight_club_script.txt", "w", encoding="utf-8") as f:
            f.write(script_content.get_text())
        print("✅ Script récupéré avec succès dans 'fight_club_script.txt'")
    else:
        print("❌ Impossible de trouver le contenu du script.")

download_fight_club_script()