import os
import shutil
from utils import *
from pathlib import Path
from indices import createTree, search

class Tupla:
    def __init__(self):
        self.cols = []

class Esquema:
    def __init__(self, col_indice=''):
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
        self.esquema = Esquema()

    def carregarDados(self):
        dir_name = "tabelas/"+self.nome_tab
        print(dir_name)
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

        Path(dir_name+"/paginas").mkdir(parents=True, exist_ok=True)

        f = open(dir_name+"/pag_count.txt", "w")
        f.write("0")
        f.close()

        print("Carregando estrutura...")

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

        newDivs = []

        for d in divs:
            pageContent = ""
            newPage(self.nome_tab, cur_page)
            cur_pageList = parsePage(self.nome_tab,cur_page)

            pagList = []
            
            l = 0
            for element in cur_pageList:
                elDic = {}
                for col in colunas:
                    elDic[col] = element[col]
                elDic['pagina_id'] = cur_page
                elDic['slot_id'] = l
                pagList.append(elDic)

                for i, col in enumerate(colunas):
                    pageContent += col + ": " + element[col]
                    if i != self.esquema.qtd_cols-1:
                        pageContent += ","
                pageContent += "\n"
                l += 1

            for element in d:
                elDic = {}
                for col in colunas:
                    elDic[col] = element[col]
                elDic['pagina_id'] = cur_page
                elDic['slot_id'] = l
                pagList.append(elDic)
                
                for i, col in enumerate(colunas):
                    pageContent += col + ": " + element[col]
                    if i != self.esquema.qtd_cols-1:
                        pageContent += ","
                pageContent += "\n"
                l += 1
            
            newDivs.extend(pagList)

            f = open(dir_name+"/paginas/" + str(cur_page) + ".txt", "a")

            f.write(pageContent)

            f.close()

            cur_page += 1

        print('Criando indices...')

        for col in colunas:
            dataArr = []
            for reg in newDivs:
                data = {x: reg[x] for x in reg if x == 'pagina_id' or x == 'slot_id'}
                data['key'] = reg[col]
                dataArr.append(data)

            newAttrPath = dir_name + '/' + col
            if os.path.exists(newAttrPath) == False:
                Path(newAttrPath).mkdir(parents=True, exist_ok=True)

            createTree(self.nome_arq, col, attribute=col, table=self.nome_tab, dataToAdd=dataArr)

class Operador:
    def __init__(self, tabela, colunas, constantes):
        self.tabela = tabela
        self.colunas = colunas
        self.constantes = constantes
        self.pagsGeradas = 0
        self.IOExecutados = 0
        self.tuplasGeradas = 0
        self.tabela.esquema.col_indice = colunas[0]

    def executar(self):
        col_indice = self.colunas[0]
        val_indice = self.constantes[0]

        col_condicoes = self.colunas[1:]
        val_condicoes = self.constantes[1:]
        condicoes = {}
        for i, col in enumerate(col_condicoes):
            condicoes[col] = val_condicoes[i]

        res, pagsGeradas, IOs, tuplasGeradas = search(self.tabela.nome_tab, col_indice, val_indice, '=', condicoes)
        self.pagsGeradas = pagsGeradas
        self.IOExecutados = IOs
        self.tuplasGeradas = tuplasGeradas
        print(res)

    def salvarTuplasGeradas(self, nome_arq):
        dir_name = 'tabelas/' + self.tabela.nome_tab + '/' + self.tabela.esquema.col_indice + '/parciais/'
        parciais = os.listdir(path=dir_name)

        completo = ''

        for p in parciais:
            f = open(dir_name + p, 'r')

            completo += ''.join(f.readlines())

            f.close()

        f = open(nome_arq, "w")
        f.write(completo)
        f.close()

    def numPagsGeradas(self):
        return self.pagsGeradas

    def numIOExecutados(self):
        return self.IOExecutados

    def numTuplasGeradas(self):
        return self.tuplasGeradas