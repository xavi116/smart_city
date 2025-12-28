# backend/main.py
from fastapi import FastAPI
from db import test_conn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smart City API is running"}

@app.get("/db-test")
def db_test():
    res = test_conn()
    if res == 1:
        return {"db_status": "Connected"}
    else:
        return {"db_status": "Failed"}
