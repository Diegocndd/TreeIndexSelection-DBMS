import os
import shutil
from utils import *
from pathlib import Path

class Tupla:
    def __init__(self):
        self.cols = []

class Esquema:
    def __init__(self, col_indice):
        self.colunas = []
        self.qtd_cols = 0
        self.col_indice = col_indice

class Pagina:
    def __init__(self):
        self.tuplas = []
        self.qtd_tuplas_ocp = 0


class Tabela:
    def __init__(self, nome_tab):
        self.nome_tab = nome_tab[:-4]
        self.nome_arq = nome_tab
        self.paginas = []
        self.qtd_pags = 0
        self.esquema = Esquema(self.obterChave())

    def carregarDados(self):
        dir_name = "tabelas/"+self.nome_tab
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            

        Path(dir_name+"/paginas").mkdir(parents=True, exist_ok=True)
        Path(dir_name+"/dados").mkdir(parents=True, exist_ok=True)
        Path(dir_name+"/folhas").mkdir(parents=True, exist_ok=True)
        Path(dir_name+"/indices").mkdir(parents=True, exist_ok=True)
        f = open(dir_name+"/pag_count.txt", "w")
        f.write("0")
        f.close()

        # Leitura CSV
        f = open(self.nome_arq, "r")
        registros = f.read().split('\n')
        registros[:] = [x for x in registros if x]

        colunas = registros[0].split(',')
        self.esquema.colunas = colunas
        self.esquema.qtd_cols = len(colunas)
        registros.pop(0) # remover header

        dataList = []

        for reg in registros:
            data = {}
            reg_split = reg.split(',')
            for i, col in enumerate(colunas):
                data[col] = reg_split[i]
            dataList.append(data)

        totalToInsert = len(dataList)

        f.close()

        cur_page = currentPage(self.nome_tab)

        cur_pageList = parsePage(self.nome_tab, cur_page)
        
        if cur_pageList is None:
            cur_page += 1
            f = open(dir_name+"/paginas/"+str(cur_page)+".txt", "w")

            f.close()
            updatePageCount(self.nome_tab, cur_page)

        cur_pageList = parsePage(self.nome_tab,cur_page)
        rest = 12 - len(cur_pageList)

        divs = []
        if rest == 0:
            cur_page += 1
        else:
            divs.append(dataList[:rest])
            dataList = dataList[rest:]
            totalToInsert = len(dataList)
        
        qntd = totalToInsert // 12
        for i in range(qntd):
            divs.append(dataList[i*12:(i+1)*12])
        
        r = totalToInsert % 12
        if r != 0:
            divs.append(dataList[-r:])

        for d in divs:
            pageContent = ""
            newPage(self.nome_tab, cur_page)
            cur_pageList = parsePage(self.nome_tab,cur_page)
            
            for element in cur_pageList:
                
                for i, col in enumerate(colunas):
                    pageContent += col + ": " + element[col]
                    if i != self.esquema.qtd_cols-1:
                        pageContent += ","
                pageContent += "\n"

            for element in d:
                for i, col in enumerate(colunas):
                    pageContent += col + ": " + element[col]
                    if i != self.esquema.qtd_cols-1:
                        pageContent += ","
                pageContent += "\n"
            
            f = open(dir_name+"/paginas/" + str(cur_page) + ".txt", "a")

            f.write(pageContent)

            f.close()

            cur_page += 1

    def obterChave(self):
        if self.nome_tab == "vinho":
            return "ano_producao"
        elif self.nome_tab == "uva":
            return "ano_colheita"
        return "pais_id"

class Operador:
    def __init__(self, tabela, colunas, constantes):
        self.tabela = tabela
        self.colunas = colunas
        self.constantes = constantes

    def executar(self):
        pass

    def salvarTuplasGeradas(self):
        pass