import sqlite3
def connect(db_path:str)->sqlite3.Connection:
    con=sqlite3.connect(db_path)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON;")
    con.execute("PRAGMA journal mode=wal;")
    con.execute("PRAGMA synchronus=NORMAL;")
    con.execute("PRAGME temp_score=MEMORY;")
    con.execute("PRAGME cache_size=-20000;") # which is approximate 20 mb

    return con
