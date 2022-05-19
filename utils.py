import os

def getRangeOfKey(key, data):
    """
    Esse algoritmo é executado em cada página e decide qual caminho de ponteiros deve seguir
    """
    keyRange = None
    searchKey = key
    qty = len(data)

    for x in range(0, qty):
        if x == 0 and str(searchKey) < str(data[x]['key']):
            keyRange = (0, 'left')
            break
        elif x == qty - 1 and str(searchKey) >= str(data[x]['key']):
            keyRange = (x, 'right')
            break
        else:
            if str(searchKey) >= str(data[x]['key']) and str(searchKey) < str(data[x + 1]['key']):
                keyRange = (x, 'right')
                break
    
    return keyRange


def parsePage(tabela, page_num):

    if page_num == 0:
        return None
    f = open("tabelas/"+tabela+"/paginas/" + str(page_num) + ".txt", "r")
    elements = f.read().split('\n')
    elements[:] = [x for x in elements if x]

    dataList = []
    for element in elements:
        data = {}
        colunas = element.split(",")
        for col in colunas:
            div_col = col.split(":")
            data[div_col[0].strip()] = div_col[1].strip()
        dataList.append(data)
    
    f.close()

    return dataList

def currentPage(tabela):
    f = open("tabelas/"+tabela+"/pag_count.txt", "r")
    cur_page = int(f.readline().strip())

    f.close()

    return cur_page

def updatePageCount(tabela, cur_page):
    f = open("tabelas/"+tabela+"/pag_count.txt", "w")
    
    f.write(str(cur_page))

    f.close()

def newPage(tabela, cur_page):
    if not os.path.exists("tabelas/"+tabela+"/paginas/" + str(cur_page) + ".txt"):
        f = open("tabelas/"+tabela+"/paginas/" + str(cur_page) + ".txt", "w")

        f.close()

        updatePageCount(tabela, cur_page)
