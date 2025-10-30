#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import argparse
import logging
from datetime import datetime

# --- Настройки по умолчанию ---
DEFAULT_ROOT = "/var/www"
DEFAULT_LOG = "/var/www/image_optimization.log"

JPEG_QUALITY = "90"
PNG_LEVEL = "2"
GIF_LEVEL = "3"
OPTIMIZED_MARKER = ".optimized"
REQUIRED_TOOLS = ["jpegoptim", "optipng", "gifsicle"]

# Папки, которые нужно исключить из обхода
DEFAULT_EXCLUDE_DIRS = ["backup"]  # можно добавлять, например ["backup", "cache", "tmp"]

# --- Настройка логирования ---
def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.info("=== Запуск %s ===", datetime.now().isoformat())

# --- Проверка инструментов ---
def check_tools():
    missing = [t for t in REQUIRED_TOOLS if shutil.which(t) is None]
    if missing:
        msg = f"Отсутствуют утилиты: {', '.join(missing)}. Установите: sudo apt install {' '.join(missing)}"
        logging.error(msg)
        raise SystemExit(msg)

# --- Вспомогательные функции ---
def human_size(size_bytes):
    for unit in ["B","KB","MB","GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def get_total_size(path, exts=(".jpg",".jpeg",".png",".gif"), exclude_dirs=None):
    total = 0
    exclude_dirs = exclude_dirs or []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f.lower().endswith(exts):
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
    return total

def already_optimized(file_path, force=False, marker=OPTIMIZED_MARKER):
    if force:
        return False
    return os.path.exists(file_path + marker)

def mark_as_optimized(file_path, marker=OPTIMIZED_MARKER):
    try:
        with open(file_path + marker, "w") as fh:
            fh.write(datetime.now().isoformat())
    except Exception as e:
        logging.warning("Не удалось создать маркер оптимизации для %s: %s", file_path, e)

def backup_file(src, base_www_dir, backup_dir):
    rel = os.path.relpath(src, base_www_dir)
    dst = os.path.join(backup_dir, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

def optimize_file(path, ext, log_handle, jpeg_q, png_lvl, gif_lvl):
    try:
        if ext in ("jpg","jpeg"):
            subprocess.run(["jpegoptim", "--strip-all", f"--max={jpeg_q}", path],
                           stdout=log_handle, stderr=log_handle, check=False)
        elif ext == "png":
            subprocess.run(["optipng", f"-o{png_lvl}", path],
                           stdout=log_handle, stderr=log_handle, check=False)
        elif ext == "gif":
            subprocess.run(["gifsicle", f"-O{gif_lvl}", "-b", path],
                           stdout=log_handle, stderr=log_handle, check=False)
        else:
            return False
        return True
    except Exception as e:
        logging.error("Ошибка при оптимизации %s: %s", path, e)
        return False

# --- Основная логика ---
def process_directory(target_dir, enable_backup=True, force=False, dry_run=False, log_file=DEFAULT_LOG, exclude_dirs=None):
    candidate_www = os.path.join(target_dir, "www")
    www_dir = candidate_www if os.path.isdir(candidate_www) else target_dir

    logging.info("Обрабатывается: %s", www_dir)
    before = get_total_size(www_dir, exclude_dirs=exclude_dirs)
    logging.info("Размер до: %s", human_size(before))

    backup_dir = os.path.join(www_dir, "backup")
    if enable_backup:
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except Exception as e:
            logging.error("Не удалось создать backup в %s: %s", backup_dir, e)
            enable_backup = False

    with open(log_file, "a") as log_handle:
        files_processed = 0
        for root, dirs, files in os.walk(www_dir):
            # Исключаем все директории из списка exclude_dirs
            if exclude_dirs:
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for f in files:
                low = f.lower()
                if not low.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    continue
                full = os.path.join(root, f)
                ext = low.rsplit(".", 1)[-1]

                if already_optimized(full, force=force):
                    continue

                logging.info("Файл: %s", full)
                if dry_run:
                    logging.info("  (dry-run) будет оптимизирован")
                    files_processed += 1
                    continue

                if enable_backup:
                    try:
                        backup_file(full, www_dir, backup_dir)
                    except Exception as e:
                        logging.warning("  Не удалось сделать резервную копию %s: %s", full, e)

                ok = optimize_file(full, ext, log_handle, JPEG_QUALITY, PNG_LEVEL, GIF_LEVEL)
                if ok:
                    mark_as_optimized(full)
                    files_processed += 1
                else:
                    logging.warning("  Оптимизация не удалась для %s", full)

    after = get_total_size(www_dir, exclude_dirs=exclude_dirs)
    diff = before - after
    pct = (diff / before * 100) if before > 0 else 0.0
    logging.info("Результат для %s: было %s, стало %s, сэкономлено %s (%.2f%%). Файлов обработано: %d",
                 www_dir, human_size(before), human_size(after), human_size(diff), pct, files_processed)

def find_and_process(root_path, enable_backup=True, force=False, dry_run=False, log_file=DEFAULT_LOG, exclude_dirs=None):
    exclude_dirs = exclude_dirs or []

    # Если директория сама содержит изображения
    if any(fname.lower().endswith((".jpg",".jpeg",".png",".gif"))
           for _, dirs, files in os.walk(root_path) if all(d not in exclude_dirs for d in dirs) for fname in files):
        process_directory(root_path, enable_backup, force, dry_run, log_file, exclude_dirs)
        return

    # Иначе проходим по подпапкам
    entries = sorted(os.listdir(root_path))
    for entry in entries:
        site_path = os.path.join(root_path, entry)
        if not os.path.isdir(site_path) or entry in exclude_dirs:
            continue
        if os.path.isdir(os.path.join(site_path, "www")) or any(
            fname.lower().endswith((".jpg",".jpeg",".png",".gif"))
            for _, dirs, files in os.walk(site_path) if all(d not in exclude_dirs for d in dirs) for fname in files
        ):
            try:
                process_directory(site_path, enable_backup, force, dry_run, log_file, exclude_dirs)
            except Exception as e:
                logging.exception("Ошибка при обработке %s: %s", site_path, e)

# --- CLI ---
def parse_args():
    p = argparse.ArgumentParser(description="Оптимизация изображений (jpg/png/gif).")
    p.add_argument("--root", "-r", default=DEFAULT_ROOT,
                   help="Корневая директория с сайтами или конкретная папка (по умолчанию /var/www).")
    p.add_argument("--no-backup", action="store_true", help="Отключить создание бэкапов.")
    p.add_argument("--force", action="store_true", help="Принудительно оптимизировать, даже если есть маркер.")
    p.add_argument("--dry-run", action="store_true", help="Только показать, что было бы сделано.")
    p.add_argument("--exclude", "-e", nargs="+", default=[], help="Список папок для исключения (например: backup cache tmp).")
    p.add_argument("--log", default=DEFAULT_LOG, help="Путь к лог-файлу.")
    return p.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log)
    exclude_dirs = list(set(DEFAULT_EXCLUDE_DIRS + args.exclude))
    logging.info("Параметры: root=%s, backup=%s, force=%s, dry_run=%s, exclude=%s",
                 args.root, not args.no_backup, args.force, args.dry_run, exclude_dirs)

    if not os.path.exists(args.root):
        logging.error("Указанная директория не найдена: %s", args.root)
        raise SystemExit(1)

    try:
        check_tools()
    except SystemExit as e:
        logging.error("Проверка утилит не пройдена: %s", e)
        raise

    try:
        find_and_process(args.root, enable_backup=not args.no_backup,
                         force=args.force, dry_run=args.dry_run, log_file=args.log,
                         exclude_dirs=exclude_dirs)
    except Exception as e:
        logging.exception("Критическая ошибка: %s", e)

if __name__ == "__main__":
    main()
