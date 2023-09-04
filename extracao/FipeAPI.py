import requests
import time

_fipe_url = 'https://veiculos.fipe.org.br/api/veiculos/'


def GetReferencias():
    
    fail = False
    
    try:
        referencias = requests.post(_fipe_url + 'ConsultarTabelaDeReferencia', timeout=5)
        referencias.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print("A connection error or timeout occurred:", e)
        fail = True
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
        fail = True
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        fail = True
    finally:
        if fail:
            time.sleep(2)
            return GetReferencias()

    return referencias.json()

def GetMarcas(referencia):
    req = {}
    req['codigoTabelaReferencia'] = referencia
    req['codigoTipoVeiculo'] = 1
    fail = False

    try:
        marcas = requests.post(_fipe_url + 'ConsultarMarcas', req, timeout=5)
        marcas.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print("A connection error or timeout occurred:", e)
        fail = True
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
        fail = True
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        fail = True
    finally:
        if fail:
            time.sleep(2)
            return GetMarcas(referencia)
        


    return marcas.json()

def GetModelos(referencia, marca):
    req = {}
    req['codigoTabelaReferencia'] = referencia
    req['codigoTipoVeiculo'] = 1
    req['codigoMarca'] = marca
    fail = False

    try:
        modelos = requests.post(_fipe_url + 'ConsultarModelos', req, timeout=5)
        modelos.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print("A connection error or timeout occurred:", e)
        fail = True
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
        fail = True
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        fail = True
    finally:
        if fail:
            time.sleep(2)
            return GetModelos(referencia, marca)

    return modelos.json()['Modelos']

def GetAnosModelo(referencia, marca, modelo):
    req = {}
    req['codigoTabelaReferencia'] = referencia
    req['codigoTipoVeiculo'] = 1
    req['codigoMarca'] = marca
    req['codigoModelo'] = modelo
    fail = False
    
    try:
        anos = requests.post(_fipe_url + 'ConsultarAnoModelo', req, timeout=5)
        anos.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print("A connection error or timeout occurred:", e)
        fail = True
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
        fail = True
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        fail = True
    finally:
        if fail:
            time.sleep(2)
            return GetAnosModelo(referencia, marca, modelo)
        
    return anos.json()



def GetValor(referencia, marca, modelo, ano, comb):
    req = {}
    req['codigoTabelaReferencia'] = referencia
    req['codigoTipoVeiculo'] = 1
    req['codigoMarca'] = marca
    req['codigoModelo'] = modelo
    req['anoModelo'] = ano
    req['codigoTipoCombustivel'] = comb
    req['tipoVeiculo'] = 'carro'
    req['tipoConsulta'] = 'tradicional'
    req['modeloCodigoExterno'] = ''

    fail = False
    
    try:
        time.sleep(1)
        valor = requests.post(_fipe_url + 'ConsultarValorComTodosParametros', req, timeout=5)
        valor.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print("A connection error or timeout occurred:", e)
        fail = True
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
        fail = True
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        fail = True
    finally:
        if fail:
            time.sleep(2)
            return GetValor(referencia, marca, modelo, ano, comb)

    return valor.json()