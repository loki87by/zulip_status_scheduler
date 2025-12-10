#!/usr/bin/env python3
"""
Скрипт для автоматической смены статуса в Zulip
Работает: Пн-Пт с 10:00 до 17:59 по МСК.
Меняет статус каждый час на случайный из списка
"""

import datetime
import random
import logging
import sys
import time
import os
from typing import Dict
from zoneinfo import ZoneInfo
from zulip import Client

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/zulip_status.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG = {
    "email": os.getenv("ZULIP_EMAIL"),
    "api_key": os.getenv("ZULIP_API_KEY"),
    "site": os.getenv("ZULIP_SITE"),
    "timezone": os.getenv("TIMEZONE")
}

FIRST_STATUSES = [
    {"text": "Инициализирую день", "emoji": "sunrise"},
    {"text": "Компилирую кофе в код", "emoji": "coffee"},
    {"text": "01001000 01100101 01101100 01101100 01101111", "emoji": "robot_face"},
    {"text": "sudo make coffee_and_sandwich", "emoji": "hamburger"},
    {"text": "Синхронизируюсь с реальностью", "emoji": "arrows_counterclockwise"},
    {"text": "Разрешаю конфликты сна и реальности", "emoji": "recycle"},
    {"text": "try { beAwesome(); } catch(Exception e) { coffee++; }", "emoji": "zap"},

]

STATUSES = [
    {"text": "Стримлю нейроны в облако", "emoji": "brain"},
    {"text": "Пингую сервера Вселенной", "emoji": "satellite"},
    {"text": "В декомпиляции сознания", "emoji": "crystal_ball"},
    {"text": "Ищу сакральный смысл в консоли", "emoji": "desktop_computer"},
    {"text": "Дебажу гравитацию", "emoji": "satellite"},
    {"text": "Охочусь на баги", "emoji": "bug"},
    {"text": "Чиню пространственно-временной континуум", "emoji": "alarm_clock"},
    {"text": "Делаю бэкап реальности", "emoji": "floppy_disk"},
    {"text": "Думаю... или завис", "emoji": "thinking_face"},
    {"text": "404: Status not found", "emoji": "question"},
    {"text": "In git we trust", "emoji": "octopus"},
    {"text": "Запускаю сборку Вселенной", "emoji": "gear"},
    {"text": "Декодирую смысл бытия", "emoji": "locked_with_key"},
    {"text": "В поисках потерянного бита", "emoji": "mag_right"},
]

class ZulipStatusScheduler:
    def __init__(self, config: Dict):
        """Инициализация клиента Zulip"""
        self.config = config
        self.timezone = ZoneInfo(config["timezone"])

        try:
            self.client = Client(
                email=config["email"],
                api_key=config["api_key"],
                site=config["site"]
            )
            logger.info("✅ Zulip клиент инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Zulip клиента: {e}")
            raise

    def get_random_status(self) -> Dict:
        """Возвращает случайный статус из списка"""
        if self.is_working_started():
            return random.choice(FIRST_STATUSES)
        return random.choice(STATUSES)

    def is_working_hours(self) -> bool:
        """
        Проверяет, рабочее ли сейчас время:
        - Пн-Пт
        - с 10:00 до 17:59 по МСК
        """
        now = datetime.datetime.now(self.timezone)

        day_of_week = now.weekday()

        if day_of_week >= 5:
            logger.info(f"Выходной день: {now.strftime('%A')}")
            return False

        current_hour = now.hour

        if int(os.getenv("START_WORK_TIME")) <= current_hour < int(os.getenv("END_WORK_TIME")):
            logger.info(f"Рабочие часы: {current_hour}:00")
            return True

        logger.info(f"Вне рабочего времени: {current_hour}:00")
        return False

    def is_working_started(self) -> bool:
        """
        Проверяет начало рабочего дня
        """
        now = datetime.datetime.now(self.timezone)

        current_hour = now.hour

        if int(os.getenv("START_WORK_TIME")) == current_hour:
            return True

        return False

    def update_status(self) -> bool:
        """Обновляет статус в Zulip"""
        try:
            if not self.is_working_hours():
                logger.info("⏸️ Сейчас не рабочее время, статус не меняем")
                return False

            status = self.get_random_status()
            result = self.client.call_endpoint(
                url="users/me/status",
                method="POST",
                request={
                    "status_text": status["text"],
                    "emoji_name": status["emoji"],
                    "away": False
                }
            )

            if result.get("result") == "success":
                logger.info(f"✅ Статус обновлен: {status['text']} ({status['emoji']})")
                return True
            else:
                logger.error(f"❌ Ошибка API: {result}")
                return False

        except Exception as e:
            logger.error(f"❌ Исключение при обновлении статуса: {e}")
            return False

    def run_once(self):
        """Одно выполнение обновления статуса"""
        return self.update_status()

    def run_scheduled(self, interval_minutes=60):
        """
        Запуск в режиме планировщика
        interval_minutes: интервал проверки в минутах
        """
        logger.info(f"🚀 Запуск планировщика статусов (интервал: {interval_minutes} мин)")

        while True:
            try:
                self.update_status()

                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("👋 Остановка по запросу пользователя")
                break
            except Exception as e:
                logger.error(f"⚠️ Ошибка в основном цикле: {e}")
                time.sleep(60)  # Ждем минуту при ошибке


def main():
    """Основная функция"""
    # Проверка переменных окружения
    required_vars = ["ZULIP_EMAIL", "ZULIP_API_KEY", "ZULIP_SITE",
                     "TIMEZONE", "START_WORK_TIME", "END_WORK_TIME"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        logger.info("Установите их командой:")
        for var in missing_vars:
            default_value = ""
            if var == "TIMEZONE":
                default_value = "Europe/Moscow"
            elif var == "START_WORK_TIME":
                default_value = "10"
            elif var == "END_WORK_TIME":
                default_value = "18"

            logger.info(f"  export {var}='{default_value}'")
        sys.exit(1)

    try:
        scheduler = ZulipStatusScheduler(CONFIG)
    except Exception as e:
        logger.error(f"❌ Не удалось создать планировщик: {e}")
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            scheduler.run_once()
        elif sys.argv[1] == "daemon":
            scheduler.run_scheduled(interval_minutes=60)
        else:
            print("Использование:")
            print("  python zulip_status_scheduler.py once   - однократное обновление")
            print("  python zulip_status_scheduler.py daemon - запуск как демон")
    else:
        scheduler.run_once()


if __name__ == "__main__":
    main()

