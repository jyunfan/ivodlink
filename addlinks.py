#!/usr/bin/env python
import sys
import json
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
db = connection.ivod
ivod = db.ivod

items = json.loads(sys.stdin.read())
ivod.insert(items)
