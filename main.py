'''
Author: LuminolT luminol.chen@gmail.com
Date: 2023-07-08 09:16:16
LastEditors: LuminolT luminol.chen@gmail.com
LastEditTime: 2023-07-08 10:56:40
FilePath: \GTNH-monitor\backend\main.py
Description: 

Copyright (c) 2023 by LuminolT, All Rights Reserved. 
'''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import datetime


class LogItem(BaseModel):
    """ LogItem class to manage the log data
    """
    id: int
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
        query = "INSERT INTO log (item_name, quantity, timestamp) VALUES (?, ?, ?)"
        cursor.execute(query, data)
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
    """