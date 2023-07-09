'''
Author: LuminolT luminol.chen@gmail.com
Date: 2023-07-08 09:16:16
LastEditors: LuminolT luminol.chen@gmail.com
LastEditTime: 2023-07-09 13:44:32
FilePath: \backend\main.py
Description: 

Copyright (c) 2023 by LuminolT, All Rights Reserved. 
'''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime
import json


class LogItem(BaseModel):
    """ LogItem class to manage the log data
    """
    id: int = None # id is auto-incremented
    item_name: str
    quantity: int
    time: datetime.datetime
            
class Buffer:
    """ Buffer class to save the POST data
    """
    def __init__(self):
        self._buffer = None
    
    def update(self, new_buf):
        self._buffer = new_buf
    
    def save(self):
        with open("buffer.json", "w") as f:
            json.dump(self._buffer, f)
            
    def read(self):
        with open("buffer.json", "r") as f:
            self._buffer = json.load(f)
            
    @property
    def buffer(self):
        return self._buffer

#################### Main ####################s

# db = Database()
app = FastAPI()
buffer = Buffer()

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
    
    
#################### Functions ####################

def get_latest_data():
    """ Get the latest log data from database

    Returns:
        list: The latest log data
    """
    
    return buffer.buffer

def add_log(log_data: str):
    """ Add log data to database

    Args:
        log_data (str): the original text
        
    Returns:
        dict: the response
    """
    data = log_data_clean(log_data)
    
    buffer.update(data)
    
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