"""Botning barcha matnlari shu yerda. Gaplarni o'zgartirmoqchi bo'lsangiz — faqat shu faylni tahrirlang.

Matnlar HTML formatda: <b>qalin</b>, <i>qiya</i>, <code>nusxa olinadigan</code>.
{...} ichidagi so'zlarni (masalan {name}) bot o'zi to'ldiradi — ularni o'zgartirmang.
"""

# ====================== Pastki menyu tugmalari ======================
BTN_EXAMS = "📚 Imtihonlar"
BTN_SEARCH = "🔎 Qidiruv"
BTN_HELP = "ℹ️ Yordam"
BTN_ADD_EXAM = "➕ Imtihon qo'shish"
BTN_ADD_SUBJECT = "📖 Fan qo'shish"
BTN_USERS = "👥 Ustozlar"
BTN_ADMINS = "🛡 Adminlar"

# ====================== Ro'yxatdan o'tish ======================
WELCOME_NEW = (
    "👋 Assalomu alaykum! Men maktabning imtihon yordamchisiman.\n\n"
    "Tanishib olamiz: <b>ism va familiyangizni</b> yozing 😊"
)
ASK_NAME_AGAIN = (
    "🤔 Ism juda qisqa yoki juda uzun ko'rinyapti.\n"
    "Ism-familiyangizni to'liq yozing, masalan: <b>Dilnoza Karimova</b>"
)
REQUEST_SENT = (
    "✅ Rahmat, <b>{name}</b>! So'rovingiz direktorga yuborildi.\n"
    "Tasdiqlanishi bilan o'zim xabar beraman 🔔"
)
WAITING = "⏳ So'rovingiz hali ko'rib chiqilmoqda. Sal sabr qiling, tez orada javob beraman 😊"
BLOCKED = "🔒 Afsuski, sizga botdan foydalanish yopilgan. Savol bo'lsa, direktorga murojaat qiling."
NOT_STARTED = "👋 Salom! Boshlash uchun /start tugmasini bosing."
NO_ACCESS = "🔒 Bu eshik hali yopiq. So'rovingiz tasdiqlangach ochiladi."
STALE_BUTTON = "Bu tugma eskirgan 🙈 /start bosib, qaytadan boshlang."

WELCOME_BACK = "👋 Xush kelibsiz, <b>{name}</b>! Pastdagi menyudan tanlang 👇"
CANCELLED = "🙅 Bekor qilindi."
MENU_HINT = "Pastdagi menyudan tanlang 👇"

NEW_REQUEST = (
    "🔔 <b>Yangi ustoz so'rovi</b>\n\n"
    "👤 {name}\n"
    "🆔 <code>{uid}</code>{username}\n\n"
    "Qabul qilamizmi?"
)
REQUEST_APPROVED_ADMIN = "✅ <b>{name}</b> qabul qilindi."
REQUEST_REJECTED_ADMIN = "❌ <b>{name}</b> rad etildi."
REQUEST_ALREADY_DONE = "Bu so'rov allaqachon ko'rib chiqilgan 🙂"

APPROVED_USER = (
    "🎉 Xush kelibsiz, <b>{name}</b>! Endi barcha imtihonlar sizga ochiq.\n"
    "Pastdagi menyudan boshlang 👇"
)
REJECTED_USER = (
    "😔 Afsuski, so'rovingiz qabul qilinmadi.\n"
    "Adashgan bo'lsangiz, /start bosib qaytadan urinib ko'ring."
)
BLOCKED_NOTICE = "🔒 Sizga botdan foydalanish yopildi."
UNBLOCKED_NOTICE = "🔓 Botdan foydalanish yana ochildi! /start bosing 😊"

# ====================== Yordam va qidiruv ======================
HELP_TEACHER = (
    "ℹ️ <b>Yordam</b>\n\n"
    "📚 <b>Imtihonlar</b> — fan, sinf va turni tanlab, imtihonni oching.\n"
    "🔎 <b>Qidiruv</b> — shunchaki yozing, men topaman. Masalan: <code>7 algebra bsb 3</code>\n\n"
    "Biror narsa ishlamasa, /start bosing."
)
HELP_STAFF_EXTRA = (
    "\n\n<b>Admin uchun:</b>\n"
    "➕ <b>Imtihon qo'shish</b> — yangi BSB/CHSB yuklash\n"
    "📖 <b>Fan qo'shish</b> — ro'yxatda yo'q fanni qo'shish\n"
    "👥 <b>Ustozlar</b> — so'rovlarni tasdiqlash, bloklash"
)
HELP_OWNER_EXTRA = "\n🛡 <b>Adminlar</b> — yangi admin qo'shish yoki olib tashlash"

SEARCH_HINT = (
    "🔎 <b>Tezkor qidiruv</b>\n\n"
    "Shunchaki yozing, men topaman! Masalan:\n"
    "• <code>7 algebra bsb 3</code>\n"
    "• <code>9 fizika chsb</code>\n"
    "• <code>mat 6 bsb</code> (fan nomining boshi ham yetadi)\n\n"
    "Hozir yozib ko'ring 👇"
)
SEARCH_NOT_UNDERSTOOD = (
    "🤔 Tushunmadim. Masalan, <code>7 algebra bsb 3</code> deb yozing "
    "yoki «📚 Imtihonlar» tugmasini bosing."
)
SEARCH_NONE = "📭 Bunday {what} hali yo'q. Boshqacha yozib ko'ring yoki menyudan tanlang 😊"
SEARCH_FOUND = "🔎 Topildi: <b>{count}</b> ta. Birini tanlang 👇"

# ====================== Imtihonlarni ko'rish ======================
NO_SUBJECTS = "📭 Hali birorta fan yo'q."
PICK_SUBJECT = "📚 Qaysi fandan?"
PICK_GRADE = "🏫 <b>{subject}</b> — qaysi sinf?"
PICK_KIND = "📝 <b>{grade}-sinf · {subject}</b>\nQaysi imtihon?"
NOT_FOUND_KIND = (
    "📭 Bu yerda hali bo'sh.\n"
    "<b>{grade}-sinf {subject}</b> uchun {kind} hali yuklanmagan."
)
LIST_BSB = "📝 <b>{grade}-sinf · {subject} · BSB</b>\nKerakli raqamni tanlang 👇"
LIST_CHSB = (
    "🗓 <b>{grade}-sinf · {subject} · CHSB</b>\n"
    "Chorakni tanlang 👇\n✅ — bor, ➖ — hali yo'q"
)
CHSB_MISSING = "📭 {quarter}-chorak CHSB si hali yuklanmagan."
EXAM_HEADER = "📘 <b>{title}</b>\n🗓 {year} o'quv yili"
QUESTIONS_LABEL = "📝 <b>Savollar:</b>"
ANSWERS_LABEL = "✅ <b>Javoblar:</b>"
NO_ANSWERS = "📭 Bu imtihon uchun javoblar hali yuklanmagan."
EXAM_AFTER = "Yana nima qilamiz? 👇"
EXAM_NOT_FOUND = "Bu imtihon topilmadi (o'chirilgan bo'lishi mumkin) 🙈"
FILE_FAILED = "⚠️ Bitta faylni ochib bo'lmadi. Direktorga xabar bering."

# ====================== Imtihon qo'shish (admin) ======================
ADD_PICK_SUBJECT = "➕ <b>Yangi imtihon</b>\n\nQaysi fan?"
ADD_PICK_GRADE = "🏫 <b>{subject}</b> — qaysi sinf?"
ADD_PICK_KIND = (
    "Qaysi tur?\n\n"
    "• <b>BSB</b> — tartib raqamini o'zim beraman (BSB-1, BSB-2...)\n"
    "• <b>CHSB</b> — chorak bo'yicha (yiliga 4 ta)"
)
ADD_PICK_QUARTER = "Nechanchi chorak CHSB si?"
ADD_CHSB_EXISTS = (
    "⚠️ <b>{grade}-sinf {subject}</b> uchun <b>{quarter}-chorak CHSB</b> allaqachon bor.\n"
    "Eskisini yangisi bilan almashtiraymi?"
)
ADD_SEND_QUESTIONS = (
    "📝 Endi <b>SAVOLLARNI</b> yuboring.\n\n"
    "Matn, rasm yoki fayl (PDF, Word) yuborishingiz mumkin. "
    "Bir nechta xabar yuborsangiz ham bo'ladi.\n"
    "Har xabardan keyin «✅ Tayyor» tugmasi chiqadi. Hammasini yuborib bo'lgach, shuni bosing 👇"
)
ADD_SEND_ANSWERS = (
    "✅ Savollar qabul qilindi!\n\n"
    "Endi <b>JAVOBLARNI</b> yuboring (matn, rasm yoki fayl).\n"
    "Javoblar hozir yo'q bo'lsa, «Javobsiz saqlash» ni bosing."
)
ADD_ITEM_OK = "👍 Qabul qilindi ({n})"
ADD_NEED_QUESTIONS = "Avval kamida bitta savol yuboring 🙂"
ADD_SAVED = "🎉 Saqlandi!\n<b>{title}</b>\n\nUstozlarga xabar yuboryapman 📣"
ADD_DUPLICATE = "⚠️ Bunday imtihon allaqachon bor. Boshqatdan boshlang: «➕ Imtihon qo'shish»."
ADD_CANCELLED = "🙅 Bekor qilindi."
ADD_SLASH = "Bekor qilish uchun /cancel deb yozing 🙂"
ADD_BAD_CONTENT = "Faqat matn, rasm yoki fayl yuboring 🙂"

NEW_EXAM_NOTICE = (
    "📚 <b>Yangilik!</b> {title} qo'shildi.\n\n"
    "Ko'rish uchun «📚 Imtihonlar» ni bosing yoki yozing: <code>{query}</code>"
)

CONFIRM_DELETE_EXAM = "🗑 <b>{title}</b>\n\nShu imtihonni o'chiraymi? Buni qaytarib bo'lmaydi."
EXAM_DELETED = "🗑 O'chirildi."

# ====================== Fan qo'shish ======================
SUBJECT_ASK = "📖 Yangi fan nomini yozing (masalan: <b>Texnologiya</b>)"
SUBJECT_ADDED = "✅ «{name}» fani qo'shildi."
SUBJECT_EXISTS = "Bunday fan allaqachon bor 🙂"
SUBJECT_BAD = "Fan nomi 2 tadan 40 tagacha belgi bo'lishi kerak. Qaytadan yozing."
SUBJECT_TEXT_ONLY = "Fan nomini matn bilan yozing 🙂"

# ====================== Ustozlarni boshqarish ======================
USERS_TITLE = (
    "👥 <b>Ustozlar</b>\n"
    "⏳ Kutayotgan: {pending}\n"
    "✅ Faol: {approved}\n"
    "🚫 Bloklangan: {blocked}\n\n"
    "Birini tanlang 👇"
)
USERS_EMPTY = "Hali hech kim ro'yxatdan o'tmagan 🙂"
USERS_MORE = "\n\n(Faqat birinchi {limit} tasi ko'rsatildi.)"
USER_CARD = "👤 <b>{name}</b>\n🆔 <code>{uid}</code>{username}\nHolati: {status}"
USER_NOT_FOUND = "Foydalanuvchi topilmadi 🙈"
USER_NO_RIGHT = "Bu foydalanuvchini boshqarish huquqingiz yo'q."
USER_BLOCKED_ADMIN = "🚫 <b>{name}</b> bloklandi."
USER_UNBLOCKED_ADMIN = "🔓 <b>{name}</b> blokdan chiqarildi."
USER_CONFIRM_DELETE = "🗑 <b>{name}</b> ni ro'yxatdan o'chiraymi?"
USER_DELETED_ADMIN = "🗑 <b>{name}</b> o'chirildi."
STATUS_LABELS = {
    "pending": "⏳ kutmoqda",
    "approved": "✅ faol",
    "blocked": "🚫 bloklangan",
}

# ====================== Adminlar (faqat ega) ======================
ADMINS_TITLE = "🛡 <b>Adminlar</b>\n\n{lines}"
ADMINS_NONE = "Hali admin yo'q. «➕ Admin qo'shish» ni bosing."
ADMIN_ASK_ID = (
    "🛡 Yangi adminning <b>Telegram ID</b> raqamini yozing.\n\n"
    "U o'z ID sini @userinfobot dan bilib oladi."
)
ADMIN_BAD_ID = "ID faqat raqamlardan iborat bo'ladi. Qaytadan yozing yoki /cancel."
ADMIN_IS_OWNER = "Bu — siz o'zingizsiz 😄 Ega allaqachon hamma narsani qila oladi."
ADMIN_ADDED = "✅ <code>{uid}</code> admin qilindi."
ADMIN_ADDED_NOTICE = "🛡 Siz botda admin etib tayinlandingiz! /start bosing."
ADMIN_CONFIRM_REMOVE = "➖ <b>{name}</b> ni adminlikdan olib tashlaymi?"
ADMIN_REMOVED = "➖ <b>{name}</b> endi admin emas."
ADMIN_REMOVED_NOTICE = "Siz endi admin emassiz. /start bosing."
