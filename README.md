README.md
# Оптимизация изображений / Image Optimization Script

Скрипт на Python для массовой оптимизации изображений на серверах Ubuntu.  
Поддерживаются форматы **JPG, PNG, GIF**.  

Создаёт резервные копии (по желанию), пропускает уже оптимизированные файлы и позволяет исключать папки из обработки (например, `backup`, `cache`, `tmp`).

---

## Возможности / Features

- Оптимизация **JPG, PNG, GIF**
- Резервное копирование оригинальных файлов (опционально)
- Пропуск уже оптимизированных файлов (`.optimized`)
- Исключение папок из обработки (`backup`, `cache`, `tmp` и любые другие)
- Поддержка запуска на всей директории сайтов или конкретном сайте
- Вывод отчета об экономии места
- CLI с гибкими опциями:
  - `--root` — корневая директория
  - `--no-backup` — отключение бэкапов
  - `--force` — принудительная оптимизация даже с маркером `.optimized`
  - `--dry-run` — показать что было бы сделано, без изменений
  - `--exclude` — список папок для исключения
  - `--log` — путь к лог-файлу

---

## Требования / Requirements

- Ubuntu / Debian
- Python 3.x
- Утилиты:
  ```bash
  sudo apt install jpegoptim optipng gifsicle

Установка / Installation

Скопировать скрипт на сервер, например в /var/www/optimize_images.py:

sudo nano /var/www/optimize_images.py


Сделать исполняемым:

sudo chmod +x /var/www/optimize_images.py


Проверить наличие утилит (jpegoptim, optipng, gifsicle):

sudo apt install jpegoptim optipng gifsicle -y

Использование / Usage
Оптимизация всех сайтов с резервными копиями:
sudo python3 /var/www/optimize_images.py

Оптимизация конкретного сайта без бэкапа:
sudo python3 /var/www/optimize_images.py --root /var/www/site/www --no-backup

Исключить дополнительные папки (cache, tmp):
sudo python3 /var/www/optimize_images.py --root /var/www --exclude cache tmp

Dry-run (только показать что будет сделано):
sudo python3 /var/www/optimize_images.py --dry-run

Принудительная оптимизация:
sudo python3 /var/www/optimize_images.py --force

Примечания / Notes

Резервные копии создаются в backup/ рядом с папкой сайта.

Оптимизация пропускает уже обработанные файлы с маркером .optimized.

Исключаемые папки можно расширять через опцию --exclude.

Логи записываются в /var/www/image_optimization.log по умолчанию, путь можно менять через --log.

Язык / Language

README написан на русском и английском языке.

Image Optimization Script

Python script for mass image optimization on Ubuntu servers.
Supports JPG, PNG, GIF formats.

Optionally creates backups, skips already optimized files, and allows folder exclusions (backup, cache, tmp, etc).

Features

Optimize JPG, PNG, GIF

Optional backup of original files

Skip already optimized files (.optimized)

Folder exclusions (backup, cache, tmp or any others)

Can run on full sites directory or a specific site

Reports space saved

CLI options:

--root — root directory

--no-backup — disable backups

--force — force optimization even if .optimized exists

--dry-run — show what would be done without changes

--exclude — folders to exclude

--log — log file path

Requirements

Ubuntu / Debian

Python 3.x

Tools:

sudo apt install jpegoptim optipng gifsicle

Installation

Copy the script to server, for example /var/www/optimize_images.py:

sudo nano /var/www/optimize_images.py


Make it executable:

sudo chmod +x /var/www/optimize_images.py


Check required tools:

sudo apt install jpegoptim optipng gifsicle -y

Usage
Optimize all sites with backups:
sudo python3 /var/www/optimize_images.py

Optimize a specific site without backup:
sudo python3 /var/www/optimize_images.py --root /var/www/site/www --no-backup

Exclude folders (cache, tmp):
sudo python3 /var/www/optimize_images.py --root /var/www --exclude cache tmp

Dry-run (preview):
sudo python3 /var/www/optimize_images.py --dry-run

Force optimization:
sudo python3 /var/www/optimize_images.py --force

Notes

Backups are created in backup/ folder next to site folder.

Already optimized files are skipped (marked with .optimized).

Excluded folders can be customized via --exclude.

Logs are written to /var/www/image_optimization.log by default (can be changed with --log).
