# 与sqlite3数据库交互
import sqlite3
import json

conn = sqlite3.connect('data/data.db')

def get_last_room(qq: str) -> str:
  "获取此用户上次查询的数据"
  stmt = "SELECT room FROM users WHERE qq=?"
  c = conn.cursor()
  c.execute(stmt, (qq,))
  result = c.fetchone()
  if result is not None:
    result = result[0]
  return result

def set_last_room(qq: str, query: str):
  "设置查询数据，注意要设置有效的查询"
  stmt = [
    "INSERT OR IGNORE INTO users (qq, room) VALUES (?, ?)",
    "UPDATE users SET room = ? WHERE qq = ?"]
  c = conn.cursor()
  c.execute(stmt[0], (qq, query))
  c.execute(stmt[1], (query, qq))
  conn.commit()

def get_time_table(qq: str) -> dict:
  stmt = "SELECT timetable FROM users WHERE qq=?"
  c = conn.cursor()
  c.execute(stmt, (qq,))
  result = c.fetchone()
  if result:
    result = result[0]
  if result is not None:
    result = json.loads(result)
  return result

def set_time_table(qq: str, table: dict):
  stmt = [
    "INSERT OR REPLACE INTO users (qq, timetable) VALUES (?, ?)",
    "UPDATE users SET timetable = ? WHERE qq = ?"
  ]
  c = conn.cursor()
  c.execute(stmt[0], (qq, json.dumps(table)))
  c.execute(stmt[0], (json.dumps(table), qq))
  conn.commit()
