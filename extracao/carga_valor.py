import sys 
import psycopg2
import psycopg2.pool
import Util
from tqdm import tqdm



def atualizaValoresMarca(pool:psycopg2.pool.SimpleConnectionPool, codMarca):
    try:
        modelos = Util.getModelosMarca(pool, codMarca)
    except Exception as e:
        print("erro ao capturar modelos: ", e)
        return
    
    for modelo in tqdm(modelos, "Atualizando marca[{}] ".format(codMarca)):
        atualizaValoresFipe(pool,modelo)


def atualizaValoresFipe(pool:psycopg2.pool.SimpleConnectionPool, codFipe):
    modelo = Util.modelByFipeCod(connPool, codFipe)

    if modelo != None:
        modelo.updateValues()
    else:
        print("nenhum modelo encontrado com o codigo Fipe ", codFipe)



args = sys.argv[1:]

if len(args) < 1:
    print("erro de sintaxe.\n")
    print("entre com o código fipe do modelo do veículo\n")
    sys.exit(1)


codigo = args[0]

params = Util.GetDbConfig()

connPool = psycopg2.pool.SimpleConnectionPool(1,20,**params)#conexao com o banco

atualizaValoresMarca(connPool,codigo)

