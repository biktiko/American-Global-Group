import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Путь к файлу с учетными данными Google
credentials_path = 'credentials.json'

# Настройка доступа к Google Sheets
creds = Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# Ссылки на таблицы
files = {
    "Air AM to USA": {"id": "1V8foxDTTOXzzw0dnJ3TIIjWrQHSU-oGOD0nRrDn3By8", "sheet": "List"},
    "Air USA to AM": {"id": "181OmCbyhfun3SdmQe7KPvlKpNnnLcl1aVzP7A2eYgSc", "sheet": "Sheet1"},
    "Ocean USA to AM": {"id": "1svNBQ6UtvR5jLsJJNDCx1YpCMfL4YB70sXz9lz9rJ18", "sheet": "Data"}
}

# Выбранное направление
user_choices = {}

# Функция обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Օդային առաքում Հայաստանից ԱՄՆ", callback_data="Air AM to USA")],
        [InlineKeyboardButton("Օդային առաքում ԱՄՆ-ից Հայաստան", callback_data="Air USA to AM")],
        [InlineKeyboardButton("Ծովային առաքում ԱՄՆ-ից Հայաստան", callback_data="Ocean USA to AM")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Բարի գալուստ Ամերիքան Գլոբալ Գրուփի առաքանիների ընթացքին հետևելու բոտ։\n\n"
        "Ընդամենը ընտրեք ուղղությունը և մուտքագրեք Ձեր ծանրոցի անհատական կոդը (waybill number)`՝ կարող եք տեսնել կարգավիճակը։",
        reply_markup=reply_markup
    )

async def handle_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_choices[query.from_user.id] = query.data  # Сохраняем направление

    keyboard = [
        [InlineKeyboardButton("Որտե՞ղ փնտրել ծանրոցի անհատական կոդը", callback_data="where_to_find")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    messages = {
        "Air AM to USA": "Օդային առաքում Հայաստանից ԱՄՆ\nՄուտքագրեք ծանրոցի անհատական կոդը ամբողջությամբ, ինչպես գրված է հաստատող փաստաթղթի վրա։ Օրինակ՝ 10500009346",
        "Air USA to AM": "Օդային առաքում ԱՄՆ-ից Հայաստան\nՄուտքագրեք ծանրոցի անհատական կոդը ամբողջությամբ, ինչպես գրված է հաստատող փաստաթղթի վրա։ Օրինակ՝ AM00017664US\n\n⚠️ Զգուշացում։՝Ձեր ծանրոցի կարգավիճակին կարող եք հետևել միայն այն դեպքում, երբ այն արդեն ուղարկվել է մեր պահեստից։",
        "Ocean USA to AM": "Ծովային առաքում ԱՄՆ-ից Հայաստան\nՄուտքագրե՛ք ծանրոցի նույնականացման անհատական կոդը ամբողջությամբ, ինչպես գրված է հաստատող փաստաթղթի վրա։ Օրինակ՝ AM10022001US։\n\n⚠️ Զգուշացում։՝՝Ձեր ծանրոցի կարգավիճակին կարող եք հետևել միայն այն դեպքում, երբ այն արդեն ուղարկվել է մեր պահեստից։"
    }
    await query.edit_message_text(messages[query.data], reply_markup=reply_markup)


# Обработка кнопки "Որտե՞ղ փնտրել"
async def handle_where_to_find(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем ID пользователя и его выбор направления
    user_id = query.from_user.id
    direction = user_choices.get(user_id)
    print(direction)

    # Логика формирования ответа в зависимости от направления
    if direction == "Air USA to AM":
        response = (
            "Գործարքի ստացականի վերին աջ անկյունում կգտնենք 12 նիշանոց նույնականացման համար:\n\n"
            "Հիմա կարող եք մուտքագրել Ձեր ծանրոցի անհատական կոդը:"
        )
    elif direction == "Ocean USA to AM":
        response = (
            "Գործարքի ստացականի վերին աջ անկյունում կգտնենք 12 նիշանոց նույնականացման համար:\n\n"
            "Հիմա կարող եք մուտքագրել Ձեր ծանրոցի անհատական կոդը:"
        )
    elif direction == "Air AM to USA":
        response = (
            "Գործարքի ստացականի վերին ձախ անկյունում կգտնենք 11 նիշանոց նույնականացման համար:\n\n"
            "Հիմա կարող եք մուտքագրել Ձեր ծանրոցի անհատական կոդը:"
        )
    else:
        response = (
            "Փոխադրման գործարքը կատարելիս Դուք ստանում եք հաստատող փաստաթուղթ, որի վերևի ձախ անկյունում կգտնեք Waybill համարը։\n\n"
            "Հիմա կարող եք մուտքագրել Ձեր ծանրոցի անհատական կոդը:"
        )

    # Отправляем соответствующий ответ
    await query.message.reply_text(response)

# Функция поиска данных в Google Sheets
def find_data(sheet_id, sheet_name, waybill):
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    # Получаем все строки с листа
    data = sheet.get_all_values()

    # Найти индекс столбца waybill по заголовку
    headers = data[0]  # Первая строка — заголовки
    try:
        waybill_index = headers.index("waybill")  # Найти индекс столбца waybill
    except ValueError:
        return "Ошибка: столбец 'waybill' отсутствует в таблице."

    # Индексы других столбцов по буквенным значениям
    ab_index = 27  # AB = 27 (1-based индекс в буквенном обозначении)
    ac_index = 28  # AC = 28
    ae_index = 30  # AE = 30
    af_index = 31  # AF = 31
    ag_index = 32  # AG = 32

    # Поиск строки с соответствующим waybill
    for row in data[1:]:  # Пропускаем заголовки
        if len(row) > waybill_index and str(row[waybill_index]).strip() == str(waybill).strip():
            # Извлекаем значения из нужных столбцов
            status = row[ac_index] if len(row) > ac_index else ""
            eta = row[ab_index] if len(row) > ab_index and status != "HOLD BY DESTINATION CUSTOMS" else "ETA unavailable"
            received = "Received by the Customer" if len(row) > ae_index and row[ae_index] == "✔" else "Not received by the Customer"
            extra_info = row[af_index] if len(row) > af_index and row[ae_index] == "✔" else None
            additional_value = row[ag_index] if len(row) > ag_index and row[ag_index] else None

            # Формируем результат
            result = f"Status: {status}\nETA: {eta}\n{received}"
            if extra_info:
                result += f"\nAdditional Info: {extra_info}"
            if additional_value:
                result += f"\nNote: {additional_value}"
            return result

    # Если ничего не найдено
    return "Նշված տվյալներով ծանրոց չի գտնվել։\n\nՀարգելի հաճախորդ, խնդրում ենք համոզվել, որ մուտքագրել եք ծանրոցի ճիշտ համարը։"

# Обработка ввода waybill
async def handle_waybill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_choices:
        await update.message.reply_text("Խնդրում ենք նախ ընտրել ուղղությունը։")
        return

    direction = user_choices[user_id]
    file_info = files.get(direction)

    if not file_info:
        await update.message.reply_text("Տվյալ ուղղությունը դեռևս ակտիվ չէ։")
        return

    waybill = update.message.text
    sheet_id = file_info['id']
    sheet_name = file_info['sheet']
    result = find_data(sheet_id, sheet_name, waybill)
    await update.message.reply_text(result)


# Запуск бота
if __name__ == "__main__":
    application = ApplicationBuilder().token("7570988275:AAFYD4F2mg5InA4jHY3zMAAgE4KzEXYYodM").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_direction, pattern="Air|Ocean"))
    application.add_handler(CallbackQueryHandler(handle_where_to_find, pattern="where_to_find"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waybill))


    application.run_polling()
