import pandas as pd
import os
from bs4 import BeautifulSoup as bs
import requests
import unicodedata


def get_page(pagini, pagfim, bairro):
    url = "http://www.buscacep.correios.com.br/sistemas/buscacep/resultadoBuscaLogBairro.cfm"
    data = {"UF": "RJ", "Localidade": "Rio de Janeiro", "Bairro": bairro, "qtdrow": 50,
            "pagini": pagini, "pagfim": pagfim}
    html = bs(requests.post(url, data).text).find_all('tr')[1:]
    return html


def get_total(bairro):
    url = "http://www.buscacep.correios.com.br/sistemas/buscacep/resultadoBuscaLogBairro.cfm"
    data = {"UF": "RJ", "Localidade": "Rio de Janeiro", "Bairro": bairro, "qtdrow": 50,
            "pagini": 1, "pagfim": 50}
    html = bs(requests.post(url, data).text)
    html = html.get_text()
    x = html.find('1 a 50 de ')+10
    y = x+6
    return int(html[x:y])


def get_ceps(bairro):
    pagini = 1
    pagfim = 50
    void_lst = []
    total = get_total(bairro)
    while pagini < total:
        html = get_page(pagini, pagfim, bairro)
        for row in html:
            try:
                logradouro, bairro, localidade, cep = (
                    col.text.strip() for col in row.find_all('td'))
            except:
                continue
            void_lst.append({'logradouro': logradouro, 'bairro': bairro,
                             'localidade': localidade, 'cep': cep})
        pagini += 50
        pagfim += 50
    return pd.DataFrame(void_lst)


def save_csv(df, path, bairro):
    df.to_csv(f'{path}/{bairro}.csv')


def bulk_csv(path):
    df = pd.DataFrame()
    for file in os.listdir(path):
        file_path = path + '/' + file
        bairro = pd.read_csv(file_path)
        df = pd.concat([df, bairro])
    df = df.reset_index()
    df.drop(['index', 'Unnamed: 0'], axis=1, inplace=True)
    df['cep'] = df['cep'].apply(lambda r: r.replace('-', ''))
    df.to_csv('all_ceps.csv')



