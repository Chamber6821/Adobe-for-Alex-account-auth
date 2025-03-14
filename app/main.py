import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from app.models import UserCredentials
from app.selenium_driver import Selenium
from app.proxy import get_working_proxy
from loguru import logger

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(credentials: UserCredentials):
    try:
        proxy = get_working_proxy()
        bot = Selenium(proxy)
        token = bot.register(credentials.email, credentials.password)
        bot.close()
        if token:
            return {"token": token}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
    except ValueError:
        raise HTTPException(status_code=401, detail="Registration failed")
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login")
async def login(credentials: UserCredentials):
    try:
        proxy = get_working_proxy()
        bot = Selenium(proxy)
        token = bot.login(credentials.email, credentials.password)
        bot.close()
        if token:
            return {"token": token}
        else:
            raise HTTPException(status_code=400, detail="Login failed")
    except ValueError:
        raise HTTPException(status_code=401, detail="Login failed")
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
