from psycopg2.pool import SimpleConnectionPool
import json

class Valor:

    __connPool__:SimpleConnectionPool

    def __init__(self, pool:SimpleConnectionPool, valor, ref, modelo, comb):
        self.__connPool__ = pool
        self._json = valor
        self._strValor = json.dumps(valor)
        self._ref = ref
        self._modelo = modelo
        self._comb = comb
        self._valor = int(self._json['Valor'].replace('R$ ','').replace('.','').replace(',',''))

    def apply(self) -> bool:
 
        sql = """INSERT INTO valor(autenticacao, ref, modelo, ano, combustivel, valor, data, criado, atualizado)
VALUES(%s,%s,%s,%s,%s,%s,%s,Now(),Now())
ON CONFLICT (autenticacao)
DO UPDATE SET data = excluded.data, valor = excluded.valor, atualizado = Now()
WHERE valor.valor != excluded.valor;""" 

        conn = self.__connPool__.getconn()

        cur = conn.cursor()

        cur.execute(sql, (self._json['Autenticacao'], self._ref,self._modelo,self._json['AnoModelo'],self._comb,self._valor,self._strValor))

        conn.commit()
        
        count = cur.rowcount

        cur.close()

        self.__connPool__.putconn(conn)

        if count > 0:
            return True
        
        return False

    def update(self) -> bool:
        change = False

        
        if self.apply():
            change = True

        return change