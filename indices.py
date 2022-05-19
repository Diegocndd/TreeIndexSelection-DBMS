"""
As funções de parse leem o conteúdo das páginas e retornam dicionários com as informações
para serem tratadas pelo programa.
"""
from ntpath import join
from random import random, randint
import math
import os
from utils import getRangeOfKey, parsePage
from editIndex import editIndex
from editLeaf import editLeaf
import sys
import traceback

ORDER = 4
ERROR_ROOT = 'root node does not exist'

path_to_tree = ''
atributo_chave = ''
arquivo_base = ''

def generateId(type):
    f = open(path_to_tree + "current_ids.txt", "r")
    elements = f.read().split('\n')
    elements[:] = [x for x in elements if x]

    f.close()
    
    new_id = 0
    
    if type == "internal_node":
        new_id = int(elements[0].split(":")[1].strip()) + 1
        elements[0] = "internal_node: " + str(new_id)
    elif type == "leaf_node":
        new_id = int(elements[1].split(":")[1].strip()) + 1
        elements[1] = "leaf_node: " + str(new_id)
    else: 
        new_id = int(elements[2].split(":")[1].strip()) + 1
        elements[2] = "page_id: " + str(new_id)

    f = open(path_to_tree + "current_ids.txt", "w")
    
    f.write("\n".join(elements))

    f.close()
    return str(new_id)

def parseLeaf(titleNode):
    f = open(path_to_tree + "paginas/folhas/" + titleNode + ".txt", "r")
    elements = f.read().split('\n')
    elements[:] = [x for x in elements if x]

    dataList = []
    count = 0
    data = {}
    for element in elements:
        
        typeData = element.split(':')[0]
        valueData = element.split(':')[1].strip()
        if typeData != 'page_id':
            data[typeData] = valueData
        else:
            data[typeData] = valueData
            dataList.append(data)
            data = {}
            count += 1
        if typeData == 'next':
            dataList.append({'next': valueData})
        if typeData == 'parent':
            dataList.append({'parent': valueData})
        if typeData == 'back':
            dataList.append({'back': valueData})
    
    f.close()

    return dataList

def parseData(titlePage):
    f = open(path_to_tree + "paginas/dados/" + titlePage + ".txt", "r")
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

def parseRecords(titlePage, tabela, condicoes):
    
    pagList = parseData(titlePage)

    pagList = sorted(pagList, key = lambda i: (i['pagina_id'], i['slot_id']))

    total = '' #temporario
    buffer = ''

    nTuplas = 0
    
    if pagList:
        pag_ant = int(pagList[0]['pagina_id'])
        pag_n = 0

        col_condicoes = list(condicoes.keys())
        val_condicoes = list(condicoes.values())

        os.makedirs(path_to_tree +  "parciais")
        cur_pagina = parsePage(tabela, pag_ant)

        for pag in pagList:
            
            if int(pag['pagina_id']) != pag_ant:
                pag_ant = int(pag['pagina_id'])
                cur_pagina = parsePage(tabela, pag_ant)
                if buffer != '':
                    f = open(path_to_tree +  "parciais/resultado_" + str(pag_n) + ".txt", "a")
                    f.write(buffer)
                    buffer = ''
                    f.close()
                pag_n += 1
            
            valid = True

            for i, col_c in enumerate(col_condicoes):
                
                if cur_pagina[int(pag['slot_id'])][col_c] != val_condicoes[i]:
                    valid = False
                    break

            if valid:
                total += ','.join(str(x) for x in cur_pagina[int(pag['slot_id'])].values()) + "\n"
                buffer += ','.join(str(x) for x in cur_pagina[int(pag['slot_id'])].values()) + "\n"
                nTuplas += 1
            
        f = open(path_to_tree +  "parciais/resultado_" + str(pag_n) + ".txt", "a")
        f.write(buffer)
        buffer = ''
        f.close()

    
    return total, nTuplas

def joinData(page_ids):
    # mesclar registros de paginas de dados do resultado de busca 
    registers = []

    for id in page_ids:
        registers.extend(parseData("page_"+str(id)))

    return registers, len(registers)

def joinData2(page_id, tabela, condicoes):

    registers, nT = parseRecords("page_"+str(page_id), tabela, condicoes)

    return registers, nT

def parseIndex(titleNode):
    global path_to_tree

    f = None
    try:
        f = open(path_to_tree + "paginas/indices/" + titleNode + ".txt", "r")
    except:
        return ERROR_ROOT
    #print(path_to_tree + "paginas/indices/" + titleNode + ".txt")
    elements = f.read().split('\n')
    elements[:] = [x for x in elements if x]

    dataList = []
    count = 0
    data = {}
    for element in elements:
        typeData = element.split(':')[0]
        valueData = element.split(':')[1].strip()
        if typeData != 'right':
            data[typeData] = valueData
        else:
            data[typeData] = valueData
            dataList.append(data)
            data = {}
            count += 1
    
    f.close()

    return dataList

def createIndex(data, titleNode='null', leftNode='null'):
    # data é um array de dicionários

    # se não for nó raiz, gerar um id para o nó interno
    if titleNode == 'null':
        titleNode = "node_" + generateId("internal_node")
    elif titleNode != "node_root":
        if len(titleNode) <= 5:
            titleNode = "node_" + titleNode

    f = open(path_to_tree + "paginas/indices/" + titleNode + ".txt", "w")
    newContent = ''

    for element in data:
        key = element['key']
        left = element['left'] if leftNode == 'null' else leftNode
        right = element['right']

        newContent += "key: {}\nleft: {} \nright: {}\n\n".format(str(key), left, right)
    
    f.write(newContent)
    f.close()

def createLeaf(data, leafName='null', parent='null', next='null', back='null', moving=False):
    # data é um array de dicionários

    # gerar id para a nova folha e salvar arquivo
    new_leaf_id = generateId("leaf_node") if leafName == 'null' else leafName
    f = open(path_to_tree + "paginas/folhas/leaf_" + new_leaf_id + ".txt", "w")

    leafContent = ""
    if moving:
        # caso esteja apenas reposicionando uma chave ja existente
        for element in data:
            leafContent += "key: {}\npage_id: {}\n\n".format(str(element["key"]), element["page_id"])
    else:
        # caso a chave ainda nao exista na estrutura
        new_page_id = generateId("page_id") 

        leafContent = "key: {}\npage_id: {}\n\n".format(str(data[0]["key"]), new_page_id)

    next = "leaf_"+next if next != 'null' else next
    if parent != "node_root" and parent != 'null':
        if len(parent) <= 5:
            parent = "node_"+parent
    back = "leaf_"+back if back != 'null' else back
    leafContent += "next: " + str(next) + "\n"
    leafContent += "parent: " + str(parent) + "\n"
    leafContent += "back: " + str(back)

    f.write(leafContent)
    f.close()

    if not moving:
        # salvar registros na pagina de registros
        f = open(path_to_tree + "paginas/dados/page_" + new_page_id + ".txt", "w")
        pageContent = ""

        for element in data:
            attrs = list(element.keys())

            for attr in attrs:
                if attr != 'key':
                    pageContent += attr + ": " + str(element[attr]) + ","
            pageContent = pageContent[:-1]
            pageContent += '\n'

        f.write(pageContent)
        f.close()
        

def ORDERDataNode(data):
    return sorted(data, key=lambda d: d['key']) 

def checkLeafMinimum(key, childNode, parentNode):
    currentContent = parseIndex(parentNode)
    
    for element in currentContent:
        if element["right"] == childNode:
            if element["key"] != key:
                editIndex(parentNode, element["key"], newKey=key, path_to_tree=path_to_tree)
            break

def shiftIndexLeft(titleNode):
    currentNode = parseIndex(titleNode)
    try:
        pos, parent, nodeParent = deepInfoIndex(titleNode)

        editIndex(nodeParent, parent["key"], newKey=currentNode[0]["key"], path_to_tree=path_to_tree)

        f = open(path_to_tree + "paginas/indices/"+titleNode+".txt", "r")
        operations = f.read().split('\n')
        operations[:] = [x for x in operations if x]

        new_content = ""

        f.close()

        f = open(path_to_tree + "paginas/indices/"+titleNode+".txt", "w")

        for i, el in enumerate(operations):
            if i > 2:
                new_content += el + "\n"

        f.write(new_content)
        f.close()
    except:
        print('ERRO AO REALIZAR SHIFT DE ELEMENTOS')


def belowMinimum(titleNode):
    currentNode = parseLeaf(titleNode)
    backNodeName = currentNode[-1]["back"]
    nextNodeName = currentNode[-3]["next"]

    if backNodeName != 'null':
        backNode = parseLeaf(backNodeName)

        n_elem_back = len(backNode[:-3])

        # tenta emprestar da esquerda
        if n_elem_back - 1 >= math.floor(ORDER / 2):
            max_val = -1
            page_id = None

            for el in backNode[:-3]:
                if el["key"] > max_val:
                    max_val = int(el["key"])
                    page_id = el["page_id"]

            removeInLeaf(backNodeName, str(max_val), check=False)

            addInLeaf(titleNode, {'key':str(max_val), 'page_id':page_id}, pageId=page_id )
            checkLeafMinimum(str(max_val), titleNode, currentNode[-2]["parent"])
        else:
            # mesclar com a esquerda

            for el in currentNode[:-3]:
                removeInLeaf(titleNode, el["key"], check=False)

                addInLeaf(backNodeName, {'key': el["key"], 'page_id':el["page_id"]}, pageId=el["page_id"] )
            
            shiftIndexLeft(currentNode[-2]["parent"])


            deleteFileLeaf(titleNode)
    elif nextNodeName != 'null':

        nextNode = parseLeaf(nextNodeName)

        n_elem_back = len(nextNode[:-3])

        # emprestar da direita
        if n_elem_back - 1 >= math.floor(ORDER / 2):
            min_val = 999999
            page_id = None

            for el in nextNode[:-3]:
                if int(el["key"]) < min_val:
                    min_val = int(el["key"])
                    page_id = el["page_id"]

            removeInLeaf(nextNodeName, str(min_val), check=False)

            addInLeaf(titleNode, {'key':str(min_val), 'page_id':page_id}, pageId=page_id )
            checkLeafMinimum(str(min_val), titleNode, currentNode[-2]["parent"])
        else:
            # mesclar com a direita

            for el in currentNode[:-3]:
                removeInLeaf(titleNode, el["key"], check=False)

                addInLeaf(nextNodeName, {'key': el["key"], 'page_id':el["page_id"]}, pageId=el["page_id"] )
            
            shiftIndexLeft(currentNode[-2]["parent"])


            deleteFileLeaf(titleNode)


def removeInLeaf(titleNode, key, check=True):
    currentContent = parseLeaf(titleNode)
    arrayToSort = currentContent[:-3]
    pointersData = currentContent[-3:]
    
    f = open(path_to_tree + "paginas/folhas/" + titleNode + ".txt", "w+", encoding="utf-8")

    leafContent = ""
    original_len = len(arrayToSort)

    new_n_elem = 0
    new_minimum = -1
    
    for element in ORDERDataNode(arrayToSort):
        if element["key"] != key:

            new_n_elem += 1

            if new_minimum == -1:
                new_minimum = element["key"]
            leafContent += "key: {}\npage_id: {}\n\n".format(element["key"], element["page_id"])
    
    leafContent += "next: " + pointersData[0]["next"] + "\n" #next
    leafContent += "parent: " + pointersData[1]["parent"] + "\n" #parent
    leafContent += "back: " + pointersData[2]["back"] #back

    f.write(leafContent)
    f.close()

    if check:
        if original_len != new_n_elem:
            if new_n_elem  < math.floor(ORDER / 2):
                belowMinimum(titleNode)
            else:
                checkLeafMinimum(str(new_minimum), titleNode, pointersData[1]["parent"])

def addInLeaf(titleNode, data, pageId=None):
    # data é um array de dicionários

    currentContent = parseLeaf(titleNode)
    arrayToSort = currentContent[:-3]
    pointersData = currentContent[-3:]

    exists = False
    page_id = ""
    
    if not pageId:
        for element in arrayToSort:
            
            if element["key"] == data[0]["key"]:
                # verificou que já existe a chave na folha, salvar page_id correspondente
                exists = True
                page_id = element["page_id"]
                break

    if exists:
        # chave já existe na folha

        registrosPag = parseData("page_" + page_id)
        
        # adicionar registro na pagina de registros existente
        f = open(path_to_tree + "paginas/dados/page_" + page_id + ".txt", "w")
        pageContent = ""

        for element in registrosPag:
            attrs = list(element.keys())

            for attr in attrs:
                if attr != 'key':
                    pageContent += attr + ": " + str(element[attr]) + ","
            pageContent = pageContent[:-1]
            pageContent += '\n'

        for element in data:
            attrs = list(element.keys())

            for attr in attrs:
                if attr != 'key':
                    pageContent += attr + ": " + str(element[attr]) + ","
            pageContent = pageContent[:-1]
            pageContent += '\n'

        f.write(pageContent)
        f.close()

    else:
        #chave ainda não está presente na folha
        f = open(path_to_tree + "paginas/folhas/" + titleNode + ".txt", "w+", encoding="utf-8")

        # criar nova pagina de registro
        page_id = generateId("page_id") if not pageId else pageId

        leafContent = ""

        data = [data] if pageId else data

        for element in data:
            arrayToSort.append({"key":element["key"], "page_id": str(page_id)})
        
        for element in ORDERDataNode(arrayToSort):
            leafContent += "key: {}\npage_id: {}\n\n".format(element["key"], element["page_id"])
        
        leafContent += "next: " + pointersData[0]["next"] + "\n" #next
        leafContent += "parent: " + pointersData[1]["parent"] + "\n" #parent
        leafContent += "back: " + pointersData[2]["back"] #back

        f.write(leafContent)
        f.close()

        if not pageId:
            # adicionar registro na pagina de registros criada
            f = open(path_to_tree + "paginas/dados/page_" + page_id + ".txt", "w+")
            pageContent = ""

            for element in data:
                attrs = list(element.keys())

                for attr in attrs:
                    if attr != 'key':
                        pageContent += attr + ": " + str(element[attr]) + ","
                pageContent = pageContent[:-1]
                pageContent += '\n'

            # for element in data:
            #     key = element['key']
            #     id_element = element['id']
            #     tipo = element['tipo']
            #     rotulo = element['rotulo']
            #     ano_colheita = element['ano_colheita']

            #     pageContent += "id: {},rotulo: {},ano_colheita: {},tipo: {}\n".format(str(id_element), rotulo, str(ano_colheita), tipo)
            
            f.write(pageContent)
            f.close() 

def addInIndex(titleNode, data):
    f = open(path_to_tree + "paginas/indices/" + titleNode + ".txt", "r")
    oldContent = f.readlines()
    oldContent = ''.join(oldContent)

    arrayToSort = parseIndex(titleNode)
    for element in data:
        arrayToSort.append(element)

    f.close()

    f = open(path_to_tree + "paginas/indices/" + titleNode + ".txt", "w+", encoding="utf-8")
    newContent = ''

    for element in ORDERDataNode(arrayToSort):
        key = element['key']
        left = element['left']
        right = element['right']

        newContent += "key: {}\nleft: {} \nright: {}\n\n".format(str(key), left, right)
    
    f.write(newContent)
    f.close()   

def deleteFileLeaf(titleNode):
    os.remove(path_to_tree + "paginas/folhas/" + titleNode + ".txt")

def deleteFileNode(titleNode):
    os.remove(path_to_tree + "paginas/indices/" + titleNode + ".txt")

def splitLeaf(titleNode):
    leafContent = parseLeaf(titleNode)

    # se o pai for null, não existe root. então, deve ser criado
    if leafContent[-2]['parent'] == 'null':
        dataLeaf = leafContent[:-3]
        mid = math.floor(len(dataLeaf) / 2)

        leftContent = dataLeaf[:mid]
        rightContent = dataLeaf[mid:]

        rootKey = rightContent[0]['key']
        rootIndexName = 'node_root'

        leftLeafName = generateId("leaf_node")
        rightLeafName = generateId("leaf_node")

        # cria o root e faz o split na folha
        createLeaf(leftContent, leafName=leftLeafName, parent=rootIndexName, next=rightLeafName, back='null', moving=True)
        createLeaf(rightContent, leafName=rightLeafName, parent=rootIndexName, back=leftLeafName, moving=True)
        createIndex([{
            'key': rootKey,
            'left': "leaf_"+leftLeafName,
            'right': "leaf_"+rightLeafName,
        }], titleNode=rootIndexName)
        
        deleteFileLeaf(titleNode)
    else:
        # se já existir root, fazer o split do nó e subir mais uma key para o root

        dataLeaf = leafContent[:-3]
        mid = math.floor(len(dataLeaf) / 2)

        leftContent = dataLeaf[:mid]
        rightContent = dataLeaf[mid:]

        parentName = leafContent[-2]['parent']
        nextName = leafContent[-3]['next']

        leftLeafName = generateId("leaf_node")
        rightLeafName = generateId("leaf_node")

        parsedParent = parseIndex(parentName)
        keyParent = None
        
        if (parsedParent != ERROR_ROOT):
            
            for index in parsedParent:
                if (index['left'] == titleNode or index['right'] == titleNode):
                    keyParent = index['key']

            backName = leafContent[-1]['back']

            if (backName == 'null'): # nesse caso, a folha está à esquerda
                newRightName = leafContent[-3]['next']
                if newRightName != 'null' and len(newRightName)>5:
                    newRightName = newRightName[5:]

                backName_crop = backName
                if backName != 'null' and len(backName)>5:
                    backName_crop = backName[5:]
                
                createLeaf(leftContent, leafName=leftLeafName, parent=parentName, next=rightLeafName, back=backName_crop, moving=True)
                createLeaf(rightContent, leafName=rightLeafName, parent=parentName, next=newRightName, back=leftLeafName, moving=True)

                leftLeafName = "leaf_"+leftLeafName if leftLeafName != 'null' else leftLeafName
                rightLeafName = "leaf_"+rightLeafName if rightLeafName != 'null' else rightLeafName

                editIndex(parentName, key=keyParent, newLeft='null', path_to_tree=path_to_tree)
                
                addInIndex(parentName, [{
                    'key': rightContent[0]['key'],
                    'left': leftLeafName,
                    'right': rightLeafName,
                }])
                
                editLeaf(nextName, newBack=rightLeafName, path_to_tree=path_to_tree)

                deleteFileLeaf(titleNode)
            else:

                newRightName = leafContent[-3]['next']
                if newRightName != 'null' and len(newRightName)>5:
                    newRightName = newRightName[5:]

                backName_crop = backName
                if backName != 'null' and len(backName)>5:
                    backName_crop = backName[5:]

                createLeaf(leftContent, leafName=leftLeafName, parent=parentName, next=rightLeafName, back=backName_crop, moving=True)
                createLeaf(rightContent, leafName=rightLeafName, parent=parentName, next=newRightName, back=leftLeafName, moving=True)

                leftLeafName = "leaf_"+leftLeafName if leftLeafName != 'null' else leftLeafName
                rightLeafName = "leaf_"+rightLeafName if rightLeafName != 'null' else rightLeafName
                
                editIndex(parentName, key=keyParent, newRight=leftLeafName, path_to_tree=path_to_tree)

                addInIndex(parentName, [{
                    'key': rightContent[0]['key'],
                    'left': 'null',
                    'right': rightLeafName,
                }])
                
                try:
                    editLeaf(backName, newNext=leftLeafName, path_to_tree=path_to_tree)
                except:
                    #print('ERRO AO EDITAR FOLHA')
                    #traceback.print_exc()
                    return
                deleteFileLeaf(titleNode)


            if (len(parsedParent) == ORDER - 1):
                splitIndex(parentName)


def insertData(data):
    try:
        root = parseIndex('node_root')

        if root == ERROR_ROOT:
            # verifica se já existe algum nó-folha sendo construído
            contentLeaf = os.listdir(path=path_to_tree + 'paginas/folhas')
            if len(contentLeaf) == 0:
                # se não existir, cria a primeira folha
                createLeaf([data])
            else:
                # se existir, adiciona na folha já existente
                titleFile = contentLeaf[0].split('.')[0]
                addInLeaf(titleFile, [data])
                leafContent = parseLeaf(titleFile)
            
                # -3 porque desconsideramos as linhas do parent, do next e do back
                if (len(leafContent) - 3 == ORDER): # se a folha estiver cheia, fazer o split e criar o root
                    
                    splitLeaf(titleFile)
        else:
            # se o root existe, vamos percorrer a árvore para descobrir onde colocar o novo dado
            actualNode = parseIndex('node_root')
            referenceNode, position = getRangeOfKey(data['key'], actualNode)

            page = actualNode[referenceNode][position]
            
            while(page.split('_')[0] != 'leaf'):
                actualNode = parseIndex(page)
                try:
                    referenceNode, position = getRangeOfKey(data['key'], actualNode)

                    page = actualNode[referenceNode][position]
                except:
                    return

            addInLeaf(page, [data])
            leafContent = parseLeaf(page)
            
            if (len(leafContent) - 3 == ORDER):
                splitLeaf(page)
    except:
        #print('ERRO AO INSERIR DADO')
        traceback.print_exc()
        return


def removeData(key):
    registers = []

    contentLeaf = os.listdir(path=path_to_tree + 'paginas/indices')

    if len(contentLeaf) == 0:
        contentLeaf = os.listdir(path=path_to_tree + 'paginas/folhas')
        startNode = contentLeaf[0][:-4]

        registers, NumTuplas, IOs = searchInLeaf(startNode, key, "=") 

        deleteDataPage(startNode, key)

        removeInLeaf(startNode, str(key))

    else:

        actualNode = parseIndex('node_root')
        referenceNode, position = getRangeOfKey(key, actualNode)

        page = actualNode[referenceNode][position]
        
        
        while(page.split('_')[0] != 'leaf'):     
            actualNode = parseIndex(page)
            referenceNode, position = getRangeOfKey(key, actualNode)

            page = actualNode[referenceNode][position]
        
        registers, numTuplas, IOs = searchInLeaf(page, key, "=")

        deleteDataPage(page, key)

        removeInLeaf(page, str(key))
    
    return len(registers)

def leafPosition(leafName):
    leafData = parseLeaf(leafName)

    if leafData[-1]['back'] == 'null':
        return 'left'
    elif leafData[-3]['next'] == 'null':
        return 'right'

def isLeaf(nodeName):
    if (nodeName.split('_')[0] == 'leaf'):
        return True
    else:
        return False

# retorna tripla [left|right, parent, parent node]
def deepInfoIndex(nodeTitle='', firstNode='node_root'):
    actualNode = parseIndex(firstNode)

    if (actualNode == ERROR_ROOT):
        return None

    for index in actualNode:
        if (index['left'] == nodeTitle):
            return ['left', index, firstNode]
        if (index['right'] == nodeTitle):
            return ['right', index, firstNode]

    for index in actualNode:
        if index['left'] != 'null':
            return deepInfoIndex(nodeTitle, firstNode=index['left'])
        if index['right'] != 'null':
            return deepInfoIndex(nodeTitle, firstNode=index['right'])

def splitIndex(nodeTitle):
    contentIndices = os.listdir(path=path_to_tree + 'paginas/indices')
    
    if len(contentIndices) == 1: # então só existe o nó root
        nodeContent = parseIndex(nodeTitle)

        dataNode = nodeContent
        mid = math.floor(len(dataNode) / 2)

        leftContent = dataNode[:mid]
        rightContent = dataNode[mid:]

        leftName = 'node_' + generateId("internal_node")
        rightName = 'node_' + generateId("internal_node")

        for index in leftContent:
            if (index['left'] != 'null'):
                editLeaf(index['left'], newParent=leftName, path_to_tree=path_to_tree)
            if (index['right'] != 'null'):
                editLeaf(index['right'], newParent=leftName, path_to_tree=path_to_tree)

        for index in rightContent:
            if (index['left'] != 'null'):
                editLeaf(index['left'], newParent=rightName, path_to_tree=path_to_tree)
            if (index['right'] != 'null'):
                editLeaf(index['right'], newParent=rightName, path_to_tree=path_to_tree) 

        deleteFileNode('node_root')
        createIndex([{
            'key': rightContent[0]['key'],
            'left': leftName,
            'right': rightName,
        }], titleNode='node_root')

        oldRight = rightContent[0]['right']
        rightContent = rightContent[1:len(rightContent)]
        rightContent[0]['left'] = oldRight

        createIndex(leftContent, titleNode=leftName)
        createIndex(rightContent, titleNode=rightName)

    elif nodeTitle == 'node_root':
        nodeContent = parseIndex(nodeTitle)

        dataNode = nodeContent
        mid = math.floor(len(dataNode) / 2)

        leftContent = dataNode[:mid]
        rightContent = dataNode[mid:]

        leftName = 'node_' + generateId("internal_node")
        rightName = 'node_' + generateId("internal_node")

        createIndex(leftContent, titleNode=leftName)
        createIndex(rightContent, titleNode=rightName)

        deleteFileNode('node_root')
        createIndex([{
            'key': rightContent[0]['key'],
            'left': leftName,
            'right': rightName,
        }], titleNode='node_root')   
    else:

        if (parseIndex(nodeTitle) != ERROR_ROOT and deepInfoIndex(nodeTitle) != None):

            pos, parent, nodeParent = deepInfoIndex(nodeTitle)
            nodeContent = parseIndex(nodeTitle)

            dataNode = nodeContent
            mid = math.floor(len(dataNode) / 2)

            leftContent = dataNode[:mid]
            rightContent = dataNode[mid:]

            leftName = 'node_' + generateId("internal_node")
            rightName = 'node_' + generateId("internal_node")

            if nodeContent[0]['left'].split('_')[0] == 'leaf':
                for index in leftContent:
                    if (index['left'] != 'null'):
                        editLeaf(index['left'], newParent=leftName, path_to_tree=path_to_tree)
                    if (index['right'] != 'null'):
                        editLeaf(index['right'], newParent=leftName, path_to_tree=path_to_tree)

                for index in rightContent:
                    if (index['left'] != 'null'):
                        editLeaf(index['left'], newParent=rightName, path_to_tree=path_to_tree)
                    if (index['right'] != 'null'):
                        editLeaf(index['right'], newParent=rightName, path_to_tree=path_to_tree)

            createIndex(rightContent[1:], titleNode=rightName, leftNode=rightContent[0]["right"])
            createIndex(leftContent, titleNode=leftName)
            
            if pos == 'right':
                addInIndex(nodeParent, [{
                    'key': rightContent[0]['key'],
                    'right': rightName,
                    'left': 'null',
                }])
                editIndex(nodeParent, parent['key'], newRight=leftName, path_to_tree=path_to_tree)
                        
            if pos == 'left':
                addInIndex(nodeParent, [{
                    'key': rightContent[0]['key'],
                    'right': rightName,
                    'left': leftName,
                }])

                editIndex(nodeParent, parent['key'], newLeft='null', path_to_tree=path_to_tree)
                
            if (len(parseIndex(nodeParent)) == ORDER - 1):
                splitIndex(nodeParent)

            deleteFileNode(nodeTitle)

def generateOutput(opType, opKey, value):
    # gerar saida de acordo com o tipo da operacao
    
    if opType == "INC":
        return "INC:"+str(opKey)+"/"+str(value)+"\n"
    elif opType == "REM":
        return "REM:"+str(opKey)+"/"+str(value)+"\n"
    elif opType == "BUS=":
        return "BUS=:"+str(opKey)+"/"+str(value)+"\n"
    elif opType == "BUS>":
        return "BUS>:"+str(opKey)+"/"+",".join(value)+"\n"
    elif opType == "BUS<":
        return "BUS<:"+str(opKey)+"/"+",".join(value)+"\n"
    return "Erro\n"

def deleteDataPage(page, opKey):
    # procurar page_id da chave
    leafContent = parseLeaf(page)
    page_id = None
    for elem in leafContent[:-3]:
        if elem["key"] == str(opKey):
            page_id = elem["page_id"]
            break
    
    if page_id:
        fileName = "paginas/dados/page_" + str(page_id) + ".txt"
        if os.path.exists(fileName):
            os.remove(fileName)


def searchInLeaf(page, opKey, mode, tabela=None, condicoes=None):
    # leitura sequencial nos nós folhas
    page_ids = []
    if mode == '=':
        
        # busca por igualdade
        leafContent = parseLeaf(page)
        
        for elem in leafContent[:-3]:

            if elem["key"] == str(opKey):
                
                page_ids.append(elem["page_id"])
                break
    elif mode == '>':
        # busca por maior que
        leafContent = parseLeaf(page)

        for elem in leafContent[:-3]:
            if str(elem["key"]) > str(opKey):
                page_ids.append(elem["page_id"])

        next = leafContent[-3]['next']    
        while next != 'null':
            leafContent = parseLeaf(next)
            for elem in leafContent[:-3]:
                page_ids.append(elem["page_id"])
            next = leafContent[-3]['next']
    elif mode == '<':
        # busca por menor que
        leafContent = parseLeaf(page)

        for elem in leafContent[:-3]:
            if str(elem["key"]) < str(opKey):
                page_ids.append(elem["page_id"])

        back = leafContent[-1]['back']    
        while back != 'null':
            leafContent = parseLeaf(back)
            for elem in leafContent[:-3]:
                page_ids.append(elem["page_id"])
            back = leafContent[-1]['back']
    
    if page_ids:
        if mode != '=' or tabela is None:
            res, nT = joinData(page_ids)
            return res, nT, 0
        else:
            res, nT = joinData2(page_ids[0], tabela, condicoes)
            return res, nT, 0
    return page_ids, 0, 0

def search(tabela, indice, opKey, mode, condicoes):
    global path_to_tree
    registers = []

    path_to_tree = "tabelas/" + tabela + "/" + indice + "/"

    contentLeaf = os.listdir(path=path_to_tree + '/paginas/indices')

    if len(contentLeaf) == 0:
        contentLeaf = os.listdir(path=path_to_tree + '/paginas/folhas')
        startNode = contentLeaf[0][:-4]

        registers, numTuplas, IOs = searchInLeaf(startNode, opKey, mode, tabela=tabela, condicoes=condicoes) # retorna as tuplas encontradas 

    else:
        actualNode = parseIndex('node_root')
        
        if actualNode != ERROR_ROOT:
            
            referenceNode, position = getRangeOfKey(opKey, actualNode)

            page = actualNode[referenceNode][position]

            while(page.split('_')[0] != 'leaf'):
                actualNode = parseIndex(page)
                try:
                    referenceNode, position = getRangeOfKey(opKey, actualNode)

                    page = actualNode[referenceNode][position]
                except:
                    return

            registers, numTuplas, IOs = searchInLeaf(page, opKey, mode, tabela=tabela, condicoes=condicoes) # retorna as tuplas encontradas 
        
    return registers, math.ceil(numTuplas / 12) , IOs, numTuplas

def createBaseFiles(path):
    newPath = path + 'paginas/'
    os.makedirs(newPath)
    os.makedirs(newPath + 'dados')
    os.makedirs(newPath + 'folhas')
    os.makedirs(newPath + 'indices')
    f = open(path + "current_ids.txt", "w")
    f.write("internal_node: 0\nleaf_node: 0\npage_id: 0")
    f.close()

def createTree(arquivo, atributo, dataToAdd=[], table='', attribute=''):
    global atributo_chave
    global arquivo_base
    global path_to_tree

    path_to_tree = 'tabelas/' + table + '/' + attribute + '/' 

    if os.path.exists(path_to_tree + 'paginas/') == False:
        createBaseFiles(path_to_tree)

    atributo_chave = atributo
    arquivo_base = arquivo
    count = 0
    for data in dataToAdd:
        if count < 100:
            insertData(data)
            # time.sleep(0.2)
        else:
            break
        count += 1

    # print(search('1984', '='))

if len(sys.argv) > 1:
    if sys.argv[1] == "-reset":
        table = sys.argv[2].split('=')[1]
        attr = sys.argv[3].split('=')[1]
        path_to_tree = 'tabelas/' + table + '/' + attr + '/' 
        # apagar toda a estrutura de indexacao e os registros
        for mydir in [path_to_tree + "paginas/dados/", path_to_tree + "paginas/folhas/", path_to_tree + "paginas/indices/"]:
            filelist = [ f for f in os.listdir(mydir) if f.endswith(".txt") ]
            for f in filelist:
                os.remove(os.path.join(mydir, f))

        # resetar arquivo de current_ids
        f = open(path_to_tree + "current_ids.txt", "w")
        reset_current_ids = "internal_node: 0\nleaf_node: 0\npage_id: 0"
        f.write(reset_current_ids)
        print("Tudo resetado")
        f.close()
        sys.exit()
else:
    # createTree('pais.csv', 'nome', dataToAdd=data, table='pais', attribute='nome')
    pass