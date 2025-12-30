# Telegram Bot Setup Guide

## Prerequisites

1. A Telegram account
2. Access to @BotFather on Telegram

## Creating Your Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "FinTrack Bot")
   - Choose a username (must end in 'bot', e.g., "fintrack_expenses_bot")
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Copy this token to your `.env` file:
   \`\`\`
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   \`\`\`

## Running the Bot

### Option 1: Polling Mode (Recommended for Development)

Run the bot as a standalone service:

\`\`\`bash
# Using Docker Compose
docker-compose up telegram-bot

# Or run directly
cd backend
python run_bot.py
\`\`\`

The bot will continuously poll Telegram for new messages.

**Pros:**
- Easy setup, no public URL needed
- Works behind NAT/firewall
- Good for development and testing

**Cons:**
- Uses more resources (constant polling)
- Slightly higher latency

### Option 2: Webhook Mode (Recommended for Production)

Set up a webhook to receive messages:

1. Deploy your FastAPI server with HTTPS (Telegram requires HTTPS)
2. Set the webhook URL:

\`\`\`bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/api/telegram/webhook"
\`\`\`

3. Verify webhook is set:

\`\`\`bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
\`\`\`

**Pros:**
- Instant message delivery
- More efficient (push vs poll)
- Lower resource usage

**Cons:**
- Requires public HTTPS URL
- More complex setup

## Testing Your Bot

1. Start your bot (using either polling or webhook mode)
2. Open Telegram and search for your bot by username
3. Send `/start` to begin
4. Try sending transactions:
   - `100 groceries`
   - `50.5 coffee at starbucks`
   - `taxi 25`

## Bot Commands

- `/start` - Initialize the bot and see welcome message
- `/help` - Get help on how to use the bot
- `/stats` - View your transaction statistics

## Message Formats

The bot accepts various formats:

- `<amount> <description>` - e.g., "100 groceries"
- `<description> <amount>` - e.g., "groceries 100"
- `<amount>` - Just the amount (labeled as "Transaction")

Examples:
- ✅ `100 groceries at whole foods`
- ✅ `50.5 uber ride to office`
- ✅ `coffee 5`
- ✅ `100`

## Troubleshooting

### Bot doesn't respond

1. Check that `TELEGRAM_BOT_TOKEN` is set correctly in `.env`
2. Verify the bot is running:
   \`\`\`bash
   docker-compose logs telegram-bot
   \`\`\`
3. Make sure the database is running and migrations have been applied

### Messages not being categorized

The categorization engine learns from your corrections. Initially, most transactions will be categorized as "Other". As you correct categories in the dashboard, the bot will learn and improve.

### Webhook not working

1. Ensure your server is accessible via HTTPS
2. Check webhook status:
   \`\`\`bash
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
   \`\`\`
3. Remove webhook and switch to polling:
   \`\`\`bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"
   \`\`\`

## Security Best Practices

1. Never commit your bot token to version control
2. Use environment variables for sensitive data
3. Implement rate limiting on webhook endpoint
4. Validate webhook requests (optional: verify Telegram's IP ranges)
5. Use HTTPS for webhook mode

## Next Steps

After setting up the bot:

1. Start using it to track expenses
2. Check the dashboard at http://localhost:3000
3. Correct categories to train the ML model
4. Export your data as CSV when needed
