# 📚 Maktab imtihon boti

Telegram bot: direktor BSB/CHSB imtihonlarini yuklaydi, ustozlar fan → sinf → tur bo'yicha topadi yoki tezkor qidiradi.

## Rollar
| Rol | Nima qila oladi |
|---|---|
| **Ega** (siz) | Hamma narsa + adminlarni qo'shish/olib tashlash |
| **Admin** (direktor) | Imtihon va fan qo'shish, ustozlarni qabul qilish/bloklash |
| **Ustoz** | Imtihonlarni ko'rish va qidirish |

## Ishga tushirish (Windows, VS Code)

1. **Python** o'rnating: https://www.python.org/downloads/ — o'rnatishda **"Add Python to PATH"** katakchasini belgilang!
2. VS Code'da **File → Open Folder** orqali shu papkani (`tgbot`) oching.
3. Terminal oching (**Terminal → New Terminal**) va yozing:
   ```
   pip install -r requirements.txt
   ```
4. `.env.example` faylidan nusxa olib, nomini **`.env`** qiling. Ichiga yozing:
   - `BOT_TOKEN=` dan keyin @BotFather bergan token
   - `OWNER_IDS=` dan keyin @userinfobot bergan ID raqamingiz
5. Botni ishga tushiring:
   ```
   python main.py
   ```
   Terminalda `Bot ishga tushdi: @sizning_botingiz` chiqsa, hammasi joyida.
6. Telegramda botingizga `/start` yozing.

Botni to'xtatish: terminalda `Ctrl + C`.
> Kompyuter o'chsa yoki terminal yopilsa, bot ham to'xtaydi. Doim ishlashi uchun keyinroq server kerak bo'ladi.

## Qidiruv misollari
`7 algebra bsb 3` · `9 fizika chsb` · `mat 6 bsb` · `5-sinf ona tili`

## Fayllar nima qiladi
| Fayl | Vazifasi |
|---|---|
| `main.py` | Botni ishga tushiradi |
| `config.py` | `.env` dan sozlamalarni o'qiydi |
| `texts.py` | **Bot gaplari.** Matnni o'zgartirmoqchi bo'lsangiz, shu yerga |
| `keyboards.py` | Tugmalar |
| `database.py` | Hamma ma'lumot saqlanadigan joy (`bot.db` fayli) |
| `utils.py` | O'quv yili va qidiruvni tushunish |
| `states.py` | Bot foydalanuvchidan nima kutayotganini eslab qolishi |
| `handlers/` | Botning ishlari: `common` (kirish), `teacher` (ko'rish, qidiruv), `admin` (qo'shish, boshqarish), `owner` (adminlar), `menu`, `gate` |

## Muhim
- `.env` faylini **hech kimga yubormang** — undagi token botingizni boshqarish kalitidir.
- Zaxira: `bot.db` faylini vaqti-vaqti bilan nusxalab qo'ying — barcha imtihonlar shu yerda.
- Yangi o'quv yili **1-sentabrda** avtomatik boshlanadi; eski imtihonlar bazada qoladi.
