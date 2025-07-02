from src.app_celery.main import app
import time
import random

@app.task(bind=True)
def parse_api(self, url, params):
    # имитация работы
    time.sleep(random.randint(1, 3))
    return {"url": url, "status": "done", "params": params}
