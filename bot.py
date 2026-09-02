import os
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# រក្សាទុកស្ថានភាពនិងទិន្នន័យរបស់អ្នកប្រើប្រាស់
user_states = {}

# ជំនួស Token Bot ថ្មីរបស់បងនៅទីនេះ
TOKEN = "8817584810:AAF43FoF97UW99wDminBH_cqU0Syz7sHl3M"
GROUP_CHAT_ID = "-1003950979639"  # លេខ ID គ្រុបដែលត្រូវឱ្យបាញ់សារចូល

# មុខងារចាប់ផ្តើម /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛍️ មើលផលិតផល / សេវាកម្ម", "🪪 ព័ត៌មានគណនី"],
        ["📞 ទំនាក់ទំនង Admin"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 សួស្តីស្វាគមន៍មកកាន់ហាងអនឡាញរបស់យើង!\n\n👇 សូមជ្រើសរើសជម្រើសខាងក្រោម៖",
        reply_markup=reply_markup
    )

# មុខងារគ្រប់គ្រងសារអត្ថបទ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # បើអតិថិជនកំពុងស្ថិតក្នុងដំណាក់កាលផ្ញើ Link ឬព័ត៌មានផលិតផល
    if user_id in user_states and user_states[user_id].get('step') == 'waiting_info':
        product_name = user_states[user_id].get('product')
        user_info = text
        
        await update.message.reply_text("✅ អរគុណ! ការបញ្ជាទិញរបស់អ្នកត្រូវបានបញ្ជូនជូន Admin រួចរាល់ហើយ។")

        # ប៊ូតុងសម្រាប់ Admin ក្នុងគ្រុបចុចផ្ទៀងផ្ទាត់
        admin_keyboard = [
            [
                InlineKeyboardButton("Approve ✅", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("Reject ❌", callback_data=f"reject_{user_id}")
            ]
        ]
        admin_markup = InlineKeyboardMarkup(admin_keyboard)

        user = update.effective_user
        caption = (
            "🔔 **មានការបញ្ជាទិញទំនិញ/សេវាកម្មថ្មី!**\n\n"
            f"• ផលិតផល: {product_name}\n"
            f"• ព័ត៌មាន/តំណរ: {user_info}\n"
            f"• អតិថិជន: {user.first_name} (@{user.username if user.username else 'None'})\n"
            f"• User ID: {user.id}"
        )
        try:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=caption, reply_markup=admin_markup, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to group: {e}")

        del user_states[user_id]
        return

    # ការរុករកម៉ឺនុយหลัก
    if text == "🛍️ មើលផលិតផល / សេវាកម្ម":
        inline_keyboard = [
            [InlineKeyboardButton("🔥 ផលិតផល A (តម្លៃ $1.00)", callback_data="prod_A")],
            [InlineKeyboardButton("🔥 ផលិតផល B (តម្លៃ $2.00)", callback_data="prod_B")],
            [InlineKeyboardButton("🔥 សេវាកម្ម C (តម្លៃ $5.00)", callback_data="prod_C")]
        ]
        await update.message.reply_text("📌 សូមជ្រើសរើសផលិតផល ឬសេវាកម្មដែលលោកអ្នកចង់ទិញ៖", reply_markup=InlineKeyboardMarkup(inline_keyboard))

    elif text == "🪪 ព័ត៌មានគណនី":
        user = update.effective_user
        await update.message.reply_text(
            f"🪪 **ព័ត៌មានរបស់អ្នក**\n\n• ឈ្មោះ: {user.first_name}\n• User ID: {user.id}\n• Username: @{user.username if user.username else 'None'}",
            parse_mode="Markdown"
        )

    elif text == "📞 ទំនាក់ទំនង Admin":
        await update.message.reply_text("📞 ទំនាក់ទំនងផ្ទាល់មកកាន់ Admin តាមរយៈ Telegram: @NEAKKROBKRONG")

    else:
        await update.message.reply_text("សូមជ្រើសរើសជម្រើសដែលមានក្នុងប៊ូតុងម៉ឺនុយខាងក្រោម។")

# មុខងារពេលអតិថិជនចុចជ្រើសរើសផលិតផលតាមរយៈ Inline Button
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data.startswith("prod_"):
        prod_map = {
            "prod_A": "ផលិតផល A",
            "prod_B": "ផលិតផល B",
            "prod_C": "សេវាកម្ម C"
        }
        selected_product = prod_map.get(data, "ទំនិញទូទៅ")
        
        # កំណត់ស្ថានភាពថា Bot កំពុងរង់ចាំអតិថិជនវាយបញ្ចូល Link ឬព័ត៌មានផលិតផល
        user_states[user_id] = {'step': 'waiting_info', 'product': selected_product}
        
        await query.edit_message_text(
            text=f"🛒 អ្នកបានជ្រើសរើស: **{selected_product}**\n\n🔗 សូមផ្ញើតំណរ (Link) ឬព័ត៌មានលម្អិតរបស់អ្នកមកទីនេះ៖",
            parse_mode="Markdown"
        )

    elif data.startswith("approve_") or data.startswith("reject_"):
        action, target_user_id = data.split("_")
        target_user_id = int(target_user_id)
        original_caption = query.message.text or ""

        if action == "approve":
            await query.edit_message_text(text=original_caption + "\n\nStatus: Approved ✅", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=target_user_id, text="✅ ការបញ្ជាទិញរបស់អ្នកត្រូវបាន Admin អនុម័ត (Approved) រួចរាល់ហើយ!")
            except: pass
        elif action == "reject":
            await query.edit_message_text(text=original_caption + "\n\nStatus: Rejected ❌", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=target_user_id, text="❌ ការបញ្ជាទិញរបស់អ្នកត្រូវបានបដិសេធ (Rejected)។")
            except: pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Online Shop Bot is running...")
    app.run_polling()
