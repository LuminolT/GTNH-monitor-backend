'''
Author: LuminolT luminol.chen@gmail.com
Date: 2023-07-08 09:01:57
LastEditors: LuminolT luminol.chen@gmail.com
LastEditTime: 2023-07-08 09:05:25
FilePath: \GTNH-monitor-backend\main.py
Description: 

Copyright (c) 2023 by LuminolT, All Rights Reserved. 
'''
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}