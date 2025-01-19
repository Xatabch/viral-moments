from content_update_server.techcrunch import app, fetch_and_compare, schedule, run_scheduler
import threading

FETCH_INTERVAL = 3600

@app.route('/')
def index():
    return "Сервер запущен и проверяет новые статьи TechCrunch."

if __name__ == "__main__":
    fetch_and_compare()

    schedule.every(FETCH_INTERVAL).seconds.do(fetch_and_compare)

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    app.run(debug=True)