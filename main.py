'''
Author: LuminolT luminol.chen@gmail.com
Date: 2023-07-08 09:16:16
LastEditors: LuminolT luminol.chen@gmail.com
LastEditTime: 2023-07-09 12:10:20
FilePath: \GTNH-monitor\backend\main.py
Description: 

Copyright (c) 2023 by LuminolT, All Rights Reserved. 
'''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime
import json


class LogItem(BaseModel):
    """ LogItem class to manage the log data
    """
    id: int = None # id is auto-incremented
    item_name: str
    quantity: int
    time: datetime.datetime

class Database:
    """ Database class to manage the connection to the database
    """
    def __init__(self):
        self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect("gtnh.sqlite")
        return self._connection

    def close_connection(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None            

#################### Main ####################s

db = Database()
app = FastAPI()

#################### API ####################

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items")
async def read_item():
    return get_latest_data()

@app.post("/add_log")
async def add_log(log_data: str):
    try:
        response = add_log(log_data)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process the request")
        
@app.on_event("startup")
def startup_event():
    db.get_connection()

@app.on_event("shutdown")
def shutdown_event():
    db.close_connection()
    
    
#################### Functions ####################

def get_latest_data():
    """ Get the latest log data from database

    Returns:
        list: The latest log data
    """
    connection = db.get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM log ORDER BY timestamp DESC"
    cursor.execute(query)
    latest_data = cursor.fetchall()
    
    # to json
    latest_data = [LogItem(id=item[0], item_name=item[1], quantity=item[2], time=item[3]) for item in latest_data]
    
    return latest_data

def add_log(log_data: str):
    """ Add log data to database

    Args:
        log_data (str): the original text
        
    Returns:
        dict: the response
    """
    connection = db.get_connection()
    cursor = connection.cursor()
    
    data = log_data_clean(log_data)
    
    try:
        for item in data:
            query = "INSERT INTO log (item_name, quantity, timestamp) VALUES (?, ?, ?)"
            cursor.execute(query, (item.item_name, item.quantity, item.time))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Failed to add the log data")
    
    return {"message": "Successfully added the log data"}


def log_data_clean(log_data: str) -> List[LogItem]:
    """ Clean the log data

    Args:
        log_data (str): the original text

    Returns:
        str: the cleaned text
        
    Examples:
        >>> log_data_clean("data=Crushed Rare Earth (I) Ore~54~false;
        ····压印基板原料~0~true;
        ····drop of 熔融黑钢~0~true;")
        
        [LogItem(id=None, item_name='Crushed Rare Earth (I) Ore', quantity=54, 
        time=datetime.datetime(2023, 7, 9, 11, 21, 25, 983932)), 
        LogItem(id=None, item_name='压印基板原料', quantity=0, 
        time=datetime.datetime(2023, 7, 9, 11, 21, 25, 983932)), 
        LogItem(id=None, item_name='drop of 熔融黑钢', quantity=0, 
        time=datetime.datetime(2023, 7, 9, 11, 21, 25, 983932))]
    """
    time = datetime.datetime.now()
    # log_data = "data=Crushed Rare Earth (I) Ore~54~false;压印基板原料~0~true;drop of 熔融黑钢~0~true;"
    log_data = log_data[5::].split(";")
    log_data = [item.split("~") for item in log_data]
    res_data = []
    for item in log_data:
        if len(item) != 3:  # check if the data is valid
            continue
        tmp_item = LogItem(item_name=item[0], quantity=int(item[1]), time=time)
        res_data.append(tmp_item)
    return res_data