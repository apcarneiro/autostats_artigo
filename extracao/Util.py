from configparser import ConfigParser
from psycopg2.pool import SimpleConnectionPool
from model.Modelo import Modelo

meses = {
    1:'janeiro',
    2:'fevereiro',
    3:'março',
    4:'abril',
    5:'maio',
    6:'junho',
    7:'julho',
    8:'agosto',
    9:'setembro',
    10:'outubro',
    11:'novembro',
    12:'dezembro'
}

def GetDbConfig(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def modelByFipeCod(pool:SimpleConnectionPool, fipeCode):
    sql = """SELECT id,marca,descricao
    FROM modelo
    WHERE codigo_fipe = %s"""

    conn = pool.getconn()

    cur = conn.cursor()
    cur.execute(sql, [fipeCode])
    records = cur.fetchall()
    cur.close()
    pool.putconn(conn)

    for row in records:
        if row[0] == None:
            return None
        
        return Modelo(pool,row[0],row[1],row[2],fipeCode)

    return None  

def getLastReference(pool:SimpleConnectionPool):

    sql = """SELECT max(id) FROM referencia"""

    conn = pool.getconn()

    cur = conn.cursor()
    cur.execute(sql)
    records = cur.fetchall()
    cur.close()
    pool.putconn(conn)

    for row in records:
        if row[0] == None:
            raise Exception("not found last reference ") 
        
        return row[0]
    
    raise Exception("error on get last reference") 

def getReference(pool:SimpleConnectionPool, month:int, year:int):
    sql = """SELECT max(id) FROM referencia WHERE to_tsvector(descricao) @@ to_tsquery(%s)"""

    conn = pool.getconn()

    ref = "{}/{}".format(meses[month],year)

    cur = conn.cursor()
    cur.execute(sql, [ref])
    records = cur.fetchall()
    cur.close()
    pool.putconn(conn)

    for row in records:
        if row[0] == None:
            raise Exception("not found to {}".format(ref)) 
        
        return row[0]
    
    raise Exception("error on get reference to {}".format(ref)) 


def getModelosMarca(pool:SimpleConnectionPool, codMarca, offset:int) ->[]:
    sql = """select codigo_fipe 
    from modelo 
    where marca = %s 
    and codigo_fipe is not null"""
    if offset > 0:
        sql += " offset {}".format(offset)

    conn = pool.getconn()

    cur = conn.cursor()
    cur.execute(sql, [codMarca])
    records = cur.fetchall()
    cur.close()
    pool.putconn(conn)

    ret = []

    for row in records:
        if row[0] == None:
            raise Exception("not found to {}".format(codMarca))
        else:
            ret.append(row[0])
    
    return ret