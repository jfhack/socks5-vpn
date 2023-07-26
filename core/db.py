#!/usr/bin/env python
import sqlite3

class DBCounter:
  def __init__(self, path):
    self.conn = sqlite3.connect(path, check_same_thread=False)
    self.c = self.conn.cursor()

    self.c.execute('''CREATE TABLE IF NOT EXISTS counter(
                    id INTEGER PRIMARY KEY CHECK (id = 0), 
                    count INTEGER
                  )''')

  def increase(self):
    with self.conn:
      self.c.execute("INSERT OR IGNORE INTO counter VALUES (?, ?)", (0, 0))
      self.c.execute("UPDATE counter SET count = count + 1")
  
  def decrease(self):
    with self.conn:
      self.c.execute("INSERT OR IGNORE INTO counter VALUES (?, ?)", (0, 0))
      self.c.execute("UPDATE counter SET count = max(count - 1, 0)")

  def reset(self):
    with self.conn:
      self.c.execute("INSERT OR IGNORE INTO counter VALUES (?, ?)", (0, 0))
      self.c.execute("UPDATE counter SET count = 0")

  def get_count(self):
    with self.conn:
      self.c.execute("INSERT OR IGNORE INTO counter VALUES (?, ?)", (0, 0))
      count = self.c.execute("SELECT count FROM counter").fetchone()[0]
    return count