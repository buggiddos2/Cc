import random
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIGURATION ===
BOT_TOKEN = "7577718098:AAFM50BhpPQZb5z5Sp87qw5bLYj9hyRjJps"  # Replace with your actual bot token
admin_id = 7501870513 # Replace with your Telegram user ID
allowed_users = set()

# === BIN LOOKUP ===
def get_bin_info(bin_code):
    try:
        r = requests.get(f"https://lookup.binlist.net/{bin_code}")
        if r.status_code == 200:
            data = r.json()
            return {
                "bank": data.get("bank", {}).get("name", "Unknown"),
                "type": data.get("type", "Unknown").upper(),
                "category": data.get("scheme", "UNKNOWN").upper(),
                "country": data.get("country", {}).get("name", "Unknown")
            }
    except:
        pass
    return {
        "bank": "Unknown",
        "type": "Unknown",
        "category": "Unknown",
        "country": "Unknown"
    }

# === LUHN VALIDATION ===
def luhn_residue(card_number):
    def digits_of(n): return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def complete_luhn(bin_base):
    for i in range(0, 10000):
        candidate = bin_base + str(i).zfill(4)
        for j in range(10):
            card = candidate + str(j)
            if luhn_residue(card) == 0:
                return card
    return None

# === COMMAND: /grant @username ===
async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != admin_id:
        await update.message.reply_text("Only admin can grant access.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /grant @username")
        return
    username = context.args[0].lstrip("@")
    allowed_users.add(username)
    await update.message.reply_text(f"User @{username} granted /gen access.")

# === COMMAND: /gen 424242 5 ===
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username not in allowed_users and update.effective_user.id != admin_id:
        await update.message.reply_text("You are not allowed to use /gen.")
        return
    try:
        bin_input = context.args[0]
        count = int(context.args[1])
    except:
        await update.message.reply_text("Usage: /gen <bin> <count>")
        return

    cards = []
    for _ in range(count):
        base = bin_input + str(random.randint(100000, 999999))[:(12-len(bin_input))]
        cc = complete_luhn(base)
        exp_month = str(random.randint(1, 12)).zfill(2)
        exp_year = str(random.randint(2026, 2030))
        cvv = str(random.randint(100, 999))
        cards.append(f"{cc}|{exp_month}|{exp_year}|{cvv}")

    await update.message.reply_text("\n".join(cards))

# === COMMAND: /chk <cc|mm|yyyy|cvv> ===
async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /chk cc|mm|yyyy|cvv")
        return

    try:
        cc, mm, yyyy, cvv = context.args[0].split("|")
    except:
        await update.message.reply_text("Invalid format. Use cc|mm|yyyy|cvv")
        return

    start = time.time()
    bin_data = get_bin_info(cc[:6])
    time.sleep(random.uniform(1.0, 2.5))  # Simulated gateway delay
    end = time.time()

    # Simulated checker: random approval
    is_approved = random.choice([True, False, False])  # Mostly decline

    status = "Approved ✅" if is_approved else "Declined ❌"
    response = "Card added" if is_approved else "Do Not Honor"
    gateway = "Stripe (Simulated)"

    user = update.effective_user
    msg = f"""
<b>CC:</b> <code>{cc}|{mm}|{yyyy}|{cvv}</code>
<b>Status:</b> {status}
<b>Response:</b> {response}
<b>Gateway:</b> {gateway}
<b>Bank:</b> {bin_data['bank']}
<b>Category:</b> {bin_data['category']}
<b>Type:</b> {bin_data['type']}
<b>Country:</b> {bin_data['country']}
<b>Took:</b> {round(end - start, 2)}s
<b>Checked by:</b> @{user.username} [{user.id}]
"""
    await update.message.reply_html(msg)

# === BOT INITIALIZATION ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("grant", grant))
    app.run_polling()
