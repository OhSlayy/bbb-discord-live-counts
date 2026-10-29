# Bros Being Bros Studios: live player counts

Every 10 minutes a GitHub Action reads how many people are playing each Bros Being Bros Studios Roblox game and shows it in
the Discord sidebar (`🎮 GAMES · 🟢 57 PLAYING`, `🚗・the-big-drive・🟢41`). Run it by hand: Actions > live-counts > Run workflow.
The Discord bot token is stored as the encrypted repository secret `DISCORD_BOT_TOKEN`; it is never in this code.
Add a game: put its channel name and Roblox universe id in `GAMES` in `live_counts.py`.
