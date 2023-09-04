from psycopg2.pool import SimpleConnectionPool
import numpy as np
from model.Valor import *
import FipeAPI 
import Util
from tqdm import tqdm


class Modelo:
    __connPool__:SimpleConnectionPool

    def __init__(self, pool:SimpleConnectionPool,id, marca, descricao, fipeCode):
        self.__connPool__ = pool
        self._id = id
        self._descricao = descricao
        self._marca = marca
        self._codFipe = fipeCode    

    def apply(self) -> bool:
 
        sql = """INSERT INTO modelo(id, marca, descricao, criado, atualizado)
VALUES(%s,%s,%s,Now(),Now()) 
ON CONFLICT (id) 
DO UPDATE SET descricao = excluded.descricao, marca = excluded.marca, atualizado = Now()
WHERE modelo.descricao != excluded.descricao
OR modelo.marca != excluded.marca;"""

        conn = self.__connPool__.getconn()

        cur = conn.cursor()

        cur.execute(sql, (self._id, self._marca, self._descricao))

        conn.commit()
        
        count = cur.rowcount

        cur.close()

        self.__connPool__.putconn(conn)

        if count > 0:
            return True
        
        return False

    def hasFipeCode(self) -> bool:

        sql = """SELECT codigo_fipe
        FROM modelo
        WHERE id = %s"""

        conn = self.__connPool__.getconn()

        cur = conn.cursor()
        cur.execute(sql, [self._id])
        records = cur.fetchall()

        cur.close()

        self.__connPool__.putconn(conn)

        for row in records:
            if row[0] != None:
                self._codFipe = row[0]
                return True
        
        return False
    
    def update(self, ref) -> bool:
        change = False
        
        if self.apply():
            change = True

        #Se o modelo já existe e tem código FIPE, não faz nada
        if self.hasFipeCode():
            return False
        
        updateCod = False

        for ano in FipeAPI.GetAnosModelo(ref,self._marca,self._id):

            data = ano['Value'].split("-")

            #Busca um valor até achar e atualiza o código Fipe do modelo
            #Os valores serão atualizados por outro módulo.
            if not updateCod:
                valor = FipeAPI.GetValor(ref,self._marca,self._id,data[0],data[1])
                
                if valor == None:
                    updateCod = False
                else:
                    self.updateFipeCod(valor['CodigoFipe'])
                    return True

        return change    
    
    def updateFipeCod(self, codFipe):
        sql = """UPDATE modelo 
        SET codigo_fipe = %s, atualizado = Now() 
        WHERE id = %s;"""

        conn = self.__connPool__.getconn()

        cur = conn.cursor()

        cur.execute(sql, (codFipe, self._id))

        conn.commit()
        
        count = cur.rowcount

        cur.close()

        self.__connPool__.putconn(conn)

        if count > 0:
            return True
        
        return False
    
    def updateValues(self) -> bool:
        if self._codFipe == None:
            return False
        
        print("Atualizando os valores para ", self._descricao)
        ref = Util.getLastReference(self.__connPool__)

        anos = []

        for ano in FipeAPI.GetAnosModelo(ref,self._marca,self._id):
            data = ano['Value'].split("-")
            anos.append(data[0])
        
        firstYear = int(anos[-1])
        print("Ano da primeira versão ", firstYear)

        #limita a 10 anos de dados
        if firstYear < 2014:
            print("Limitado à 2013")
            firstYear = 2014

        #pega o cod de referencia de janeiro do primeiro ano do veiculo menos 1
        olderRef = Util.getReference(self.__connPool__,1,firstYear - 1)

        print("- referencia mais antiga: {} - {}".format(olderRef,(firstYear - 1)))

        #busca a primeira referencia onde esse modelo está presente
        i = 0
        while(olderRef <= ref):
            ret = FipeAPI.GetAnosModelo(olderRef,self._marca,self._id)
            if 'erro' in ret:
                print("--- nao achou... procura ", olderRef+1)
            else: #quando achar, pega os valores de cada ano da referencia
                for ano in tqdm(ret,"Atualiza Valores ref[{}]".format(olderRef)):
                    data = ano['Value'].split("-")
                    valor = FipeAPI.GetValor(olderRef,self._marca,self._id,data[0],data[1])
                    if 'erro' in valor:
                        print('erro ao pegar valor: ', valor['erro'])
                    else:
                        val = Valor(self.__connPool__,valor,olderRef,self._id,data[1])
                        val.update()
            
            olderRef += 1
