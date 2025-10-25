# Start Quiz Bot - Windows Version
Write-Host "🚀 Starting Quiz Bot..." -ForegroundColor Green

# Set environment variable
$env:TELEGRAM_BOT_TOKEN="8236591484:AAE89yIh5amaGK7q36mkUFmnkODDCwWExmY"

# Check if data directory exists
if (-not (Test-Path "data")) {
    Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" -Force
}

# Start the bot
Write-Host "🤖 Starting Quiz Bot..." -ForegroundColor Green
python quiz_bot.py