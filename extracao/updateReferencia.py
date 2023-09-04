import psycopg2
import psycopg2.pool
import FipeAPI
from model.Referencia import *
import Util
from tqdm import tqdm



params = Util.GetDbConfig()

connPool = psycopg2.pool.SimpleConnectionPool(1,20,**params)#conexao com o banco

referencias = []

error = False

for referencia in tqdm(FipeAPI.GetReferencias(),"Atualizando Referências"):
    ref = Referencia(connPool,referencia['Codigo'],referencia['Mes'])
    try: 
        ref.apply()
    except Exception as e:
        print(('Erro ao atualizar referencia {}-{}:{}-{}').format(referencia['Codigo'],referencia['Mes'],type(e),e) )
        break

