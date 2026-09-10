# Render deployment note

This bot is configured to expose a small HTTP health endpoint on Render's `$PORT` while the Telegram bot runs with polling.

For a quick test on Render Free, this is sufficient. Render Free services may spin down after inactivity, so this setup is intended for testing rather than guaranteed 24/7 availability.
