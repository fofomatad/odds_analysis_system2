import requests
import os

# Lista de times da NBA com suas abreviações
nba_teams = {
    'Atlanta Hawks': 'ATL',
    'Boston Celtics': 'BOS',
    'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NO',  # Ajustado
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTAH',  # Ajustado
    'Washington Wizards': 'WAS'
}

def download_logo(team_name, team_code):
    # URL base para os logos
    base_url = "https://a.espncdn.com/i/teamlogos/nba/500/"
    
    # Caminho para salvar o logo
    save_path = f"static/logos/{team_name.lower().replace(' ', '_')}.png"
    
    try:
        # Constrói a URL completa
        url = f"{base_url}{team_code.lower()}.png"
        
        # Adiciona headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Faz o download do logo
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Salva o logo
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Logo baixado com sucesso: {team_name}")
        else:
            print(f"Erro ao baixar logo para {team_name}: Status {response.status_code}")
    except Exception as e:
        print(f"Erro ao processar {team_name}: {str(e)}")

def main():
    # Cria o diretório se não existir
    os.makedirs("static/logos", exist_ok=True)
    
    # Download dos logos para cada time
    for team_name, team_code in nba_teams.items():
        download_logo(team_name, team_code)

if __name__ == "__main__":
    main()
