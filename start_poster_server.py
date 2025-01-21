from content_update_server.base import run_scheduler
import threading
from flask import Flask
from configs.video.techcrunch import config as techcrunch_config

app = Flask('auto_poster')

if __name__ == "__main__":
    # Проверяем, является ли поток главным, чтобы не запускать планировщик дважды
    if not threading.current_thread().name == "MainThread":
        exit()

    def techcrunch_scheduler():
        run_scheduler(techcrunch_config)

    # Запускаем планировщики в отдельных потоках
    techcrunch_scheduler_thread = threading.Thread(target=techcrunch_scheduler, daemon=True)
    techcrunch_scheduler_thread.start()

    # Запускаем Flask без перезагрузки
    app.run(debug=False, use_reloader=False, port=8001)