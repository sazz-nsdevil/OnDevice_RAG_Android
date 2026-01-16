import sqlite3
from typing import Iterable

def set_meta(con:sqlite3.Connection,key:str,value:str)->None:
    con.execute("INSERT OR REPLACE INRO meta(key,value)VALUES(?,?)",(key,value))


def insert_document(con:sqlite3.Connection,doc_id:int,title:str | None,grade:int,subject:str)->None:
    con.execute(
        "INSERT OR REPLACE INTO documents(doc_id,title,grade,subject) VALUES(?,?,?,?)",(doc_id,title,grade,subject),
    )

def insert_chunks(con:sqlite3.Connection,rows:Iterable[tuple[int,int,str,str |None]])->None:
    con.executemany(
        "INSERT OR REPLACE INTO chunks(chunk_id,doc_id,text,metadata) VALUES(?,?,?,?)",rows,
    )
def insert_embeddings(con:sqlite3.Conneection,rows:Iterable[tuple[str,int,bytes]])->None:
    con.executemany(
        "INSERT OR REPLACE INTO embeddings(chunk_id,dims,vec) VALUES(?,?,?)",rows,
    )


def iter_vectors_for_grade_subject(
        con:sqlite3.Connection,
        grade:int,
        subject:int,
        dims:int,
        limit:int,

):
    cur=con.execute(
        """SELECT e.chubnk_id,e.vec,c.text,c.metadata,d.doc_id FROM documents d JOIN chunks c ON c.doc_id=d.doc_id
        JOIN embeddings e ON e.chunk_id=c.chunk_id WHERE d.grade=? AND d.subject=? AND e.dims=? LIMIT ? """,
        (grade,subject,dims,limit),
    )
    while True:
        batch=cur.fetchmany(512)
        if not batch:
            break
        for r in batch:
            yield r


def candidate_chunk_ids_from_fts(con:sqlite3.Connection,doc_ids:list[str],text_query:str,limit:int)->list[str]:
    if not doc_ids:
        return[]
    placeholders=",".join(["?"]*len(doc_ids))
    rows=con.execute(
        f"""SELECT chunk_id FROM chunks_fts WHERE doc_id IN ({placeholders}) AND chunks_fts MATCH ? LIMIT ?""", [*doc_ids,text_query,limit],
    ).fetchall()

    return [str(r["chunk_id"])for r in rows]

def doc_ids_for_grade_subject(con: sqlite3.Connection, grade: int, subject: str) -> list[str]:
    rows = con.execute(
        "SELECT doc_id FROM documents WHERE grade=? AND subject=?",
        (grade, subject),
    ).fetchall()
    return [str(r["doc_id"]) for r in rows]

def iter_vectors_by_chunk_ids(con: sqlite3.Connection, chunk_ids: list[str]):
    if not chunk_ids:
        return iter(())
    placeholders = ",".join(["?"] * len(chunk_ids))
    cur = con.execute(
        f"""
        SELECT e.chunk_id, e.vec, c.text, c.metadata, d.doc_id
        FROM embeddings e
        JOIN chunks c ON c.chunk_id = e.chunk_id
        JOIN documents d ON d.doc_id = c.doc_id
        WHERE e.chunk_id IN ({placeholders})
        """,
        chunk_ids,
    )
    while True:
        batch = cur.fetchmany(512)
        if not batch:
            break
        for r in batch:
            yield r