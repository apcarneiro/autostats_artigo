from psycopg2.pool import SimpleConnectionPool
import Util

class Referencia:
    __connPool__:SimpleConnectionPool

    def __init__(self, pool:SimpleConnectionPool, id, mesReferencia):
        self.__connPool__ = pool
        self._id = id
        self._mesReferencia = mesReferencia.strip(' ')
        aux = self._mesReferencia.split('/')
        print("aux ", aux)
        self._year = int(aux[1])
        self._month = [i for i in Util.meses if Util.meses[i]==aux[0]][0]

    def getId(self):
        return self._id    
    def getMesReferencia(self):
        return self._mesReferencia   

    def apply(self) -> bool:

        sql = """INSERT INTO referencia(id, descricao, criado, atualizado, mes, ano)
VALUES(%s,%s,Now(),Now(),%s,%s) 
ON CONFLICT (id) 
DO UPDATE SET descricao = excluded.descricao, mes = excluded.mes, ano = excluded.ano, atualizado = Now()
WHERE referencia.descricao != excluded.descricao 
OR referencia.ano != excluded.ano 
OR referencia.mes != excluded.mes;"""

        conn = self.__connPool__.getconn()

        cur = conn.cursor()

        cur.execute(sql, (self._id, self._mesReferencia,self._month,self._year))

        count = cur.rowcount
        conn.commit()

        cur.close()

        self.__connPool__.putconn(conn)

        if count > 0:
            return True
        
        return False

    #def update(self) -> bool:
    #    change = False

    #    print("updating reference {} [{}]...".format(self._mesReferencia, self._id))
    #    if self.apply():
    #        print("...reference updated")
    #        change = True

    #    for marca in tqdm(FipeAPI.GetMarcas(self._id), "Marcas"):
    #        m = Marca(self.__connPool__,marca['Value'],marca['Label'])
    #        if m.update(self._id):
    #            change = True

    #    return change  