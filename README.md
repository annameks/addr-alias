# addr-alias

**addr-alias** — простая утилита, которая генерирует человекочитаемый alias и ASCII-identicon для крипто-адреса (Ethereum-style hex).  
Удобно для пометок в блокнотах, UI, тестовой генерации меток и фиксации адресов.

## Что делает
- Детеминированно генерирует короткий произносимый alias из адреса.
- Генерирует маленький ASCII identicon (7×7) по хешу адреса.
- Выводит короткий fingerprint (SHA256) и грубую оценку энтропии hex-строки.

## Файлы
- `addr_alias.py` — основной скрипт (CLI).
- `README.md` — это описание.
- `requirements.txt` — список зависимостей (пусто — стандартная библиотека).

## Установка и запуск
Файл `requirements.txt` пустой (скрипт использует только стандартную библиотеку), поэтому достаточно:

```bash
# сделать исполняемым (опционально)
chmod +x addr_alias.py

# пример
python addr_alias.py 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF

# или через stdin
echo "0xDEADBEEFDEADBEEF..." | python addr_alias.py
