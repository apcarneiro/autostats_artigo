from psycopg2.pool import SimpleConnectionPool
from model.Modelo import *
import FipeAPI 
from tqdm import tqdm

class Marca:
    __connPool__:SimpleConnectionPool

    def __init__(self, pool:SimpleConnectionPool, id, descricao):
        self.__connPool__ = pool
        self._id = id
        self._descricao = descricao
        

    def apply(self) -> bool:

        sql = """INSERT INTO marca(id, descricao, criado, atualizado)
VALUES(%s,%s,Now(),Now()) 
ON CONFLICT (id) 
DO UPDATE SET descricao = excluded.descricao, atualizado = Now()
WHERE marca.descricao != excluded.descricao;"""

        conn = self.__connPool__.getconn()

        cur = conn.cursor()

        cur.execute(sql, (self._id, self._descricao))

        conn.commit()
        
        count = cur.rowcount

        cur.close()

        self.__connPool__.putconn(conn)

        if count > 0:
            return True
        
        return False
    
    def update(self, ref) -> bool:
        change = False

        if self.apply():
            change = True
        for modelo in tqdm(FipeAPI.GetModelos(ref,self._id), "Modelos"):
            mod = Modelo(self.__connPool__, modelo['Value'], self._id, modelo['Label'])
            if mod.update(ref):
                change = True

        return change    