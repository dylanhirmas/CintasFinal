import os
import json
import logging
import requests
import google.generativeai as genai

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Team

# Initialize logger
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# API keys and settings
API_FOOTBALL_KEY     = os.getenv("API_FOOTBALL_KEY")
FOOTBALL_DATA_KEY    = os.getenv("FOOTBALL_DATA_KEY")
LOCK_SCREEN_PASSWORD = os.getenv("LOCK_SCREEN_PASSWORD", "changeme")

# League mapping
LEAGUE_NAMES = {
    39:  "Premier League",
    140: "La Liga",
    78:  "Bundesliga",
    135: "Serie A",
    2:   "UEFA Champions League",
    3:   "UEFA Europa League",
}

# Complete knowledge base
KNOWLEDGE_BASE = {
    "Real Madrid": {
        "coach": "Carlo Ancelotti",
        "nickname": "Los Blancos",
        "most_titles": "14 UEFA Champions League titles",
        "greatest_player": "Cristiano Ronaldo",
        "main_rival": "Barcelona",
        "most_expensive_signing": "Eden Hazard",
        "city": "Madrid, Spain",
    },
    "Barcelona": {
        "coach": "Xavi Hernandez",
        "nickname": "Blaugrana",
        "most_titles": "27 La Liga titles",
        "greatest_player": "Lionel Messi",
        "main_rival": "Real Madrid",
        "most_expensive_signing": "Philippe Coutinho",
        "city": "Barcelona, Spain",
    },
    "Atletico Madrid": {
        "coach": "Diego Simeone",
        "nickname": "Los Colchoneros",
        "most_titles": "11 La Liga titles",
        "greatest_player": "Fernando Torres",
        "main_rival": "Real Madrid",
        "most_expensive_signing": "João Félix",
        "city": "Madrid, Spain",
    },
    "Real Betis": {
        "coach": "Manuel Pellegrini",
        "nickname": "Los Verdiblancos",
        "most_titles": "3 Copa del Rey titles",
        "greatest_player": "Joaquín",
        "main_rival": "Sevilla FC",
        "most_expensive_signing": "Nabil Fekir",
        "city": "Seville, Spain",
    },
    "Arsenal": {
        "coach": "Mikel Arteta",
        "nickname": "The Gunners",
        "most_titles": "14 FA Cups",
        "greatest_player": "Thierry Henry",
        "main_rival": "Tottenham Hotspur",
        "most_expensive_signing": "Declan Rice",
        "city": "London, England",
    },
    "Liverpool": {
        "coach": "Jürgen Klopp",
        "nickname": "The Reds",
        "most_titles": "19 English league titles",
        "greatest_player": "Steven Gerrard",
        "main_rival": "Manchester United",
        "most_expensive_signing": "Darwin Núñez",
        "city": "Liverpool, England",
    },
    "Manchester United": {
        "coach": "Erik ten Hag",
        "nickname": "The Red Devils",
        "most_titles": "20 English league titles",
        "greatest_player": "Ryan Giggs",
        "main_rival": "Liverpool",
        "most_expensive_signing": "Paul Pogba",
        "city": "Manchester, England",
    },
    "Manchester City": {
        "coach": "Pep Guardiola",
        "nickname": "The Citizens",
        "most_titles": "9 English league titles",
        "greatest_player": "Sergio Agüero",
        "main_rival": "Manchester United",
        "most_expensive_signing": "Jack Grealish",
        "city": "Manchester, England",
    },
    "AC Milan": {
        "coach": "Stefano Pioli",
        "nickname": "Rossoneri",
        "most_titles": "7 UEFA Champions League titles",
        "greatest_player": "Paolo Maldini",
        "main_rival": "Inter Milan",
        "most_expensive_signing": "Leonardo Bonucci",
        "city": "Milan, Italy",
    },
    "Inter Milan": {
        "coach": "Simone Inzaghi",
        "nickname": "Nerazzurri",
        "most_titles": "19 Serie A titles",
        "greatest_player": "Giuseppe Meazza",
        "main_rival": "AC Milan",
        "most_expensive_signing": "Romelu Lukaku",
        "city": "Milan, Italy",
    },
    "Juventus": {
        "coach": "Massimiliano Allegri",
        "nickname": "La Vecchia Signora",
        "most_titles": "36 Serie A titles",
        "greatest_player": "Alessandro Del Piero",
        "main_rival": "Torino",
        "most_expensive_signing": "Cristiano Ronaldo",
        "city": "Turin, Italy",
    },
    "Napoli": {
        "coach": "Francesco Calzona",
        "nickname": "Gli Azzurri",
        "most_titles": "3 Serie A titles",
        "greatest_player": "Diego Maradona",
        "main_rival": "Roma",
        "most_expensive_signing": "Victor Osimhen",
        "city": "Naples, Italy",
    },
    "Bayern Munich": {
        "coach": "Thomas Tuchel",
        "nickname": "Die Roten",
        "most_titles": "33 Bundesliga titles",
        "greatest_player": "Franz Beckenbauer",
        "main_rival": "Borussia Dortmund",
        "most_expensive_signing": "Harry Kane",
        "city": "Munich, Germany",
    },
    "Borussia Dortmund": {
        "coach": "Edin Terzic",
        "nickname": "Die Schwarzgelben",
        "most_titles": "8 Bundesliga titles",
        "greatest_player": "Marco Reus",
        "main_rival": "Bayern Munich",
        "most_expensive_signing": "Ousmane Dembélé",
        "city": "Dortmund, Germany",
    },
    "Bayer Leverkusen": {
        "coach": "Xabi Alonso",
        "nickname": "Die Werkself",
        "most_titles": "1 Bundesliga title (2024)",
        "greatest_player": "Michael Ballack",
        "main_rival": "1. FC Köln",
        "most_expensive_signing": "Moussa Diaby",
        "city": "Leverkusen, Germany",
    },
    "RB Leipzig": {
        "coach": "Marco Rose",
        "nickname": "Die Roten Bullen",
        "most_titles": "2 DFB-Pokal titles",
        "greatest_player": "Emil Forsberg",
        "main_rival": "Bayer Leverkusen",
        "most_expensive_signing": "Joško Gvardiol",
        "city": "Leipzig, Germany",
    },
}

def get_team_top_scorers_football_data(league_code):
    url = f"https://api.football-data.org/v4/competitions/{league_code}/scorers"
    headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return [
            {
                "player": {"name": s["player"]["name"], "nationality": s["player"]["nationality"]},
                "goals": s["goals"],
                "team": {"name": s["team"]["name"]},
            }
            for s in resp.json().get("scorers", [])
        ]
    except Exception as e:
        logger.error(f"Top Scorers Fetch Error: {e}")
        return []

def get_team_squad(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/players/squads"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    try:
        resp = requests.get(url, headers=headers, params={"team": team_id})
        resp.raise_for_status()
        data = resp.json()
        return data["response"][0]["players"] if data.get("response") else []
    except Exception as e:
        logger.error(f"Squad Fetch Error: {e}")
        return []

def get_player_statistics(player_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/players"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    params = {"id": player_id, "season": 2024}
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get("response"):
            stats = data["response"][0]["statistics"][0]
            info = data["response"][0]["player"]
            return {
                "name": info.get("name", "Unknown"),
                "position": stats.get("games", {}).get("position", "Unknown"),
                "appearances": stats.get("games", {}).get("appearences", "N/A"),
                "goals": stats.get("goals", {}).get("total", "N/A"),
                "assists": stats.get("goals", {}).get("assists", "N/A"),
                "yellow_cards": stats.get("cards", {}).get("yellow", "N/A"),
                "red_cards": stats.get("cards", {}).get("red", "N/A"),
                "nationality": info.get("nationality", "Unknown"),
                "age": info.get("age", "N/A"),
                "photo": info.get("photo", ""),
            }
    except Exception as e:
        logger.error(f"Player stats fetch error: {e}")
    return {
        "name": "Unknown", "position": "Unknown", "appearances": "N/A",
        "goals": "N/A", "assists": "N/A", "yellow_cards": "N/A",
        "red_cards": "N/A", "nationality": "Unknown", "age": "N/A",
        "photo": "",
    }

def get_team_fixtures(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    try:
        last = requests.get(url, headers=headers, params={"team": team_id, "last": 6})
        nxt  = requests.get(url, headers=headers, params={"team": team_id, "next": 6})
        return {
            "last": last.json().get("response", []),
            "next": nxt.json().get("response", []),
        }
    except Exception as e:
        logger.error(f"Fixtures Fetch Error: {e}")
        return {"last": [], "next": []}

def get_league_standings(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    try:
        resp = requests.get(url, headers=headers, params={"league": league_id, "season": 2024})
        resp.raise_for_status()
        data = resp.json()
        return data["response"][0]["league"]["standings"][0] if data.get("response") else []
    except Exception as e:
        logger.error(f"Standings Fetch Error: {e}")
        return []

from django.shortcuts import render
from django.core.paginator import Paginator

def team_list(request):
    # ─── LOCK SCREEN ───
    if not request.session.get('authenticated'):
        error = None
        if request.method == "POST":
            pwd = request.POST.get("password", "")
            if pwd == LOCK_SCREEN_PASSWORD:
                request.session['authenticated'] = True
            else:
                error = "❌ Incorrect password."
        if not request.session.get('authenticated'):
            return render(request, 'teams/lock_screen.html', {'error': error})

    # ─── HOME PAGE ─── no pagination, show all teams
    teams = Team.objects.all().order_by('name')

    # Group by league name
    league_teams = {}
    for team in teams:
        lid = team.api_league_id
        lname = LEAGUE_NAMES.get(lid, f"League {lid}")
        league_teams.setdefault(lname, []).append(team)

    return render(request, 'teams/team_list.html', {
        'league_teams': league_teams,
        # no page_obj needed
    })


def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    squad = get_team_squad(team.api_football_id) if team.api_football_id else []
    scorers = get_team_top_scorers_football_data(team.football_data_league_code) if team.football_data_league_code else []
    fixtures = get_team_fixtures(team.api_football_id) if team.api_football_id else {"last": [], "next": []}
    standings = get_league_standings(team.api_league_id) if team.api_league_id else None

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'fixtures': fixtures,
        'standings': standings,
        'squad': squad,
        'top_scorers': scorers,
    })


def player_detail(request, player_id, team_id):
    stats = get_player_statistics(player_id)
    return render(request, 'teams/player_detail.html', {
        'player_id':    player_id,
        'team_id':      team_id,
        'name':         stats['name'],
        'position':     stats['position'],
        'appearances':  stats['appearances'],
        'goals':        stats['goals'],
        'assists':      stats['assists'],
        'yellow_cards': stats['yellow_cards'],
        'red_cards':    stats['red_cards'],
        'nationality':  stats['nationality'],
        'photo':        stats['photo'],
    })


@csrf_exempt
def ask_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            team_id = data.get("team_id")
            if not question or not team_id:
                return JsonResponse({"response": "Missing team ID or question."})
            team = get_object_or_404(Team, id=team_id)
            tn = team.name
            ql = question.lower()
            info = KNOWLEDGE_BASE.get(tn)
            if info and any(k in ql for k in ["coach","nickname","titles","trophies","player","rival","expensive","city"]):
                if "coach" in ql:
                    ans = f"The head coach of {tn} is {info['coach']}."
                elif "nickname" in ql:
                    ans = f"{tn}'s nickname is {info['nickname']}."
                elif any(x in ql for x in ["titles","trophies"]):
                    ans = f"{tn} has won {info['most_titles']}."
                elif "player" in ql:
                    ans = f"The greatest player for {tn} is {info['greatest_player']}."
                elif "rival" in ql:
                    ans = f"The main rival of {tn} is {info['main_rival']}."
                elif "expensive" in ql:
                    ans = f"The most expensive signing for {tn} was {info['most_expensive_signing']}."
                elif "city" in ql:
                    ans = f"{tn} is based in {info['city']}."
                else:
                    ans = "Sorry, I don't have that info."
            else:
                prompt = f"{tn} is a football club based in {team.country}. {team.description}\n\nQ:{question}\nA:"
                ans = model.generate_content(prompt).text.strip()
            return JsonResponse({"response": ans})
        except Exception as e:
            logger.error(f"ask_ai error: {e}")
            return JsonResponse({"response": "Error generating AI response."})


@csrf_exempt
def ask_player_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pid = data.get("player_id")
            q = data.get("question","")
            if not pid or not q:
                return JsonResponse({"response":"Missing player ID or question."})
            ans = model.generate_content(f"User question about player: {q}").text.strip()
            return JsonResponse({"response": ans})
        except Exception as e:
            logger.error(f"ask_player_ai error: {e}")
            return JsonResponse({"response":"Error generating AI response."})


def compare_teams(request):
    teams = Team.objects.all().order_by("name")
    return render(request, "teams/compare_teams.html", {"teams": teams})


@csrf_exempt
def ask_compare_ai(request):
    if request.method=="POST":
        try:
            data = json.loads(request.body)
            team1 = get_object_or_404(Team, id=data.get("team1_id"))
            team2 = get_object_or_404(Team, id=data.get("team2_id"))
            q = data.get("question","")
            prompt = (
                f"Team A: {team1.name}\n"
                f"Nickname: {KNOWLEDGE_BASE.get(team1.name,{}).get('nickname','Unknown')}\n"
                f"Most Titles: {KNOWLEDGE_BASE.get(team1.name,{}).get('most_titles','Unknown')}\n"
                f"Greatest Player: {KNOWLEDGE_BASE.get(team1.name,{}).get('greatest_player','Unknown')}\n\n"
                f"Team B: {team2.name}\n"
                f"Nickname: {KNOWLEDGE_BASE.get(team2.name,{}).get('nickname','Unknown')}\n"
                f"Most Titles: {KNOWLEDGE_BASE.get(team2.name,{}).get('most_titles','Unknown')}\n"
                f"Greatest Player: {KNOWLEDGE_BASE.get(team2.name,{}).get('greatest_player','Unknown')}\n\n"
                f"Question: {q}\nA:"
            )
            ans = model.generate_content(prompt).text.strip()
            return JsonResponse({"response": ans})
        except Exception as e:
            logger.error(f"ask_compare_ai error: {e}")
            return JsonResponse({"response":"Error generating AI comparison."})


def league_standings(request, league_id):
    standings = get_league_standings(league_id)
    if not standings:
        return render(request,"teams/league_standings.html",{"error":"Unable to fetch league standings."})
    return render(request,"teams/league_standings.html",{"standings":standings,"league_id":league_id})


def league_ai(request):
    return render(request,"teams/league_ai.html",{"league_names": LEAGUE_NAMES.items()})


@csrf_exempt
def ask_league_ai(request):
    if request.method=="POST":
        try:
            data = json.loads(request.body)
            lid = int(data.get("league_id"))
            q = (data.get("question") or "").lower()
            st = get_league_standings(lid)
            if not st:
                return JsonResponse({"response":"Could not retrieve league data."})
            if "leading" in q or "first" in q:
                top=st[0]
                return JsonResponse({"response":f"The current leader is {top['team']['name']} with {top['points']} points."})
            if "last" in q or "bottom" in q:
                bot=st[-1]
                return JsonResponse({"response":f"The bottom team is {bot['team']['name']} with {bot['points']} points."})
            if "most goals" in q:
                mg=max(st,key=lambda x:x["all"]["goals"]["for"])
                return JsonResponse({"response":f"{mg['team']['name']} has scored the most goals ({mg['all']['goals']['for']})."})
            if "best defense" in q:
                bd=min(st,key=lambda x:x["all"]["goals"]["against"])
                return JsonResponse({"response":f"{bd['team']['name']} has conceded the fewest goals ({bd['all']['goals']['against']})."})
            if "goal difference" in q:
                gd=max(st,key=lambda x:x["goalsDiff"])
                return JsonResponse({"response":f"{gd['team']['name']} has the best goal difference ({gd['goalsDiff']})."})
            if "top 5" in q or "five" in q:
                names=", ".join(item["team"]["name"] for item in st[:5])
                return JsonResponse({"response":f"Top 5 teams: {names}."})
            prompt=f"User asks about {LEAGUE_NAMES.get(lid,'this league')}: {data.get('question')}. Answer based on current standings."
            ans=model.generate_content(prompt).text.strip()
            return JsonResponse({"response":ans})
        except Exception as e:
            logger.error(f"ask_league_ai error: {e}")
            return JsonResponse({"response":"Error processing league question."})

# -----------------------
# Trivia Quiz
# -----------------------

TRIVIA_QUESTIONS = [
    {"id":1,"question":"Which club has won the most UEFA Champions League titles?"},
    {"id":2,"question":"Who is known as 'The Gunners'?"},
    {"id":3,"question":"Which team is nicknamed 'Los Blancos'?"},
    {"id":4,"question":"Which Bundesliga side is called 'Die Roten'?"},
    {"id":5,"question":"Which club is nicknamed 'The Red Devils'?"},
    {"id":6,"question":"Who are called 'Die Roten Bullen'?"},
    {"id":7,"question":"Which club goes by 'Blaugrana'?"},
]

TRIVIA_ANSWERS={
    1:"Real Madrid",2:"Arsenal",3:"Real Madrid",4:"Bayern Munich",
    5:"Manchester United",6:"RB Leipzig",7:"Barcelona",
}

def trivia_quiz(request):
    return render(request,'teams/trivia_quiz.html',{'questions':TRIVIA_QUESTIONS})

@csrf_exempt
def submit_trivia(request):
    if request.method=="POST":
        try:
            data=json.loads(request.body)
            qid=data.get("question_id")
            ans=(data.get("answer") or "").strip()
            correct=(TRIVIA_ANSWERS.get(qid,"").lower()==ans.lower())
            return JsonResponse({"correct":correct,"correct_answer":TRIVIA_ANSWERS.get(qid,"")})
        except Exception as e:
            logger.error(f"submit_trivia error: {e}")
            return JsonResponse({"error":"Error processing trivia answer."},status=500)
    return JsonResponse({"error":"Invalid request method."},status=400)
