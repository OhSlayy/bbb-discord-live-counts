"""Live player counts in the Discord sidebar: renames the GAMES category and each game channel with the number playing now.

  🎮 GAMES · 🟢 57 PLAYING        🚗・the-big-drive・🟢41
One run = one update (fetch counts from games.roblox.com, rename only what changed). Discord allows ~2 renames per channel per
10 minutes, so run it every 10 minutes (Windows Task Scheduler) or with --loop (sleeps 10 min between runs).
Token: env DISCORD_BOT_TOKEN (never printed).
"""
import os, re, sys, time
import requests

API = "https://discord.com/api/v10"
GID = "1556959018994634762"
H = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"], "User-Agent": "BBBStudiosBuilder (local, 1.0)", "Content-Type": "application/json"}
# base channel name -> universe id
GAMES = {
    "🚗・the-big-drive": 10647852789,
    "🛷・sled-with-friends": 10768843976,
    "💻・be-a-game-dev": 10772650478,
    "🥷・stick-wars": 10772900938,
    "🪖・tank-wars": 10773125906,
}
CAT_BASE = "🎮 GAMES"
VISITS_PREFIX = "📈 "  # locked voice channel at the top of GAMES: "📈 61.4K Total Visits" (created on first run)
CONNECT = 1 << 20
SUFFIX = re.compile(r"・🟢\d+$")


def stats() -> tuple:
    ids = ",".join(str(u) for u in GAMES.values())
    r = requests.get(f"https://games.roblox.com/v1/games?universeIds={ids}", timeout=15)
    r.raise_for_status()
    data = r.json()["data"]
    return {g["id"]: int(g.get("playing") or 0) for g in data}, sum(int(g.get("visits") or 0) for g in data)


def short(n: int) -> str:
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if n >= div:
            return f"{n / div:.1f}".rstrip("0").rstrip(".") + suf
    return str(n)


def rename(cid: str, name: str) -> bool:
    r = requests.patch(f"{API}/channels/{cid}", headers=H, json={"name": name}, timeout=15)
    if r.status_code == 429:
        print("  rate limited, skipped:", name)
        return False
    r.raise_for_status()
    return True


def run_once():
    counts, visits = stats()
    chans = requests.get(f"{API}/guilds/{GID}/channels", headers=H, timeout=15).json()
    total = 0
    for c in chans:
        base = SUFFIX.sub("", c["name"])
        if c["type"] == 0 and base in GAMES:
            n = counts.get(GAMES[base], 0)
            total += n
            want = f"{base}・🟢{n}"
            if c["name"] != want:
                print("rename", c["name"], "->", want, "ok" if rename(c["id"], want) else "")
    cat = next((c for c in chans if c["type"] == 4 and c["name"].startswith(CAT_BASE)), None)
    if cat:
        want = f"{CAT_BASE} · 🟢 {total} PLAYING"
        if cat["name"] != want:
            print("rename category ->", want, "ok" if rename(cat["id"], want) else "")
        vname = f"{VISITS_PREFIX}{short(visits)} Total Visits"
        vc = next((c for c in chans if c["type"] == 2 and c.get("parent_id") == cat["id"] and c["name"].startswith(VISITS_PREFIX)), None)
        if not vc:
            r = requests.post(f"{API}/guilds/{GID}/channels", headers=H, timeout=15, json={
                "name": vname, "type": 2, "parent_id": cat["id"], "position": 0,
                "permission_overwrites": [{"id": GID, "type": 0, "allow": "0", "deny": str(CONNECT)}]})
            r.raise_for_status()
            print("created", vname)
        elif vc["name"] != vname:
            print("rename visits ->", vname, "ok" if rename(vc["id"], vname) else "")
    print(time.strftime("%H:%M"), "total playing", total, "visits", visits, {k: counts.get(v, 0) for k, v in GAMES.items()})


if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            try:
                run_once()
            except Exception as e:  # keep looping through network hiccups
                print("error:", e)
            time.sleep(600)
    else:
        run_once()
