from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from api.v1.router import api_router
from services.data_lake import update_duck_db
load_dotenv()

app = FastAPI(
    title="precos-pmc-api"
)

update_duck_db()

@app.on_event('startup')
def init_data():
    scheduler = BackgroundScheduler()

    cron = {
        'hour': '17', 
        'minute': '0',
    }

    scheduler.add_job(update_duck_db, 'cron', **cron)
    scheduler.start()

app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the precos-pmc-api!"}

