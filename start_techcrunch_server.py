from content_update_server.techcrunch import fetch_and_compare, schedule, run_scheduler
import threading
from flask import Flask

app = Flask('name')

if __name__ == "__main__":
    # Проверяем, является ли поток главным, чтобы не запускать планировщик дважды
    if not threading.current_thread().name == "MainThread":
        exit()

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Запускаем Flask без перезагрузки
    app.run(debug=False, use_reloader=False)