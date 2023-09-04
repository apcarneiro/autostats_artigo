import psycopg2
import psycopg2.pool
import FipeAPI
from model.Referencia import *
from model.Modelo import *
from model.Valor import *
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
        referencias.append(ref)
    except Exception as e:
        print(('Erro ao atualizar referencia {}-{}:{}-{}').format(referencia['Codigo'],referencia['Mes'],type(e),e) )
        error = True
        break

if error == False:
    for referencia in tqdm(referencias, "Atualizando Marcas"):
        marcas = []

        if error == False:
            for marca in tqdm(FipeAPI.GetMarcas(referencia.getId()), "Marcas de {}".format(referencia.getMesReferencia())):
                m = Marca(connPool,marca['Value'],marca['Label'])
                try:
                    m.apply()
                    marcas.append(m)
                except Exception as e:
                    print(('Erro ao atualizar marca {}-{}:{} - {}').format(marca['Value'],marca['Label'],type(e),e) )
                    error = True
                    break
            
            if error == False:
                for marca in tqdm(marcas):
                    modFipeCod = []

                    if error == False:
                        for modelo in tqdm(FipeAPI.GetModelos(referencia.getId(),marca._id), "Modelos de {} - {}".format(marca._id,marca._descricao)):
                            mod = Modelo(connPool, modelo['Value'], marca._id, modelo['Label'])
                            try:
                                mod.apply()
                                if not mod.hasFipeCode():
                                    modFipeCod.append(mod)
                            except Exception as e:
                                print(('Erro ao atualizar modelo {}-{}:').format(modelo['Value'],modelo['Label'],e) )
                                error = True
                                break

                    if error == False and len(modFipeCod) > 0:
                        for mod in tqdm(modFipeCod, "Atualizando codigos Fipe"):
                            for ano in FipeAPI.GetAnosModelo(referencia.getId(),mod._marca,mod._id):
                                data = ano['Value'].split("-")

                                valor = FipeAPI.GetValor(referencia.getId(),mod._marca,mod._id,data[0],data[1])
                                
                                #Os valores serão atualizados por outro módulo.
                                mod.updateFipeCod(valor['CodigoFipe'])

                                break         
if connPool is not None:
    connPool.closeall()
    print('Database connection closed.')

