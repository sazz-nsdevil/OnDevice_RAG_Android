from pathlib import Path
import sqlite3
def init_schema(con:sqlite3.Connection,sql_dir:str)->None:
    sql_dir=str(sql_dir)
    p=Path(sql_dir)
    con.executescript((p/"001_init.sql").read_text(encoding="utf-8"))
    con.executescript((p/"002_indexes.sql").read_text(encoding="utf-8"))
