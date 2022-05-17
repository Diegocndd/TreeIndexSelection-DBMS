"""
As funções de parse leem o conteúdo das páginas e retornam dicionários com as informações
para serem tratadas pelo programa.
"""

from ntpath import join
from random import random, randint
import math
import os
from utils import getRangeOfKey
from editIndex import editIndex
from editLeaf import editLeaf
import sys

ORDER = 4
ERROR_ROOT = 'root node does not exist'
ATRIBUTO = 'ano_colheita'

def generateId(type):
    f = open("current_ids.txt", "r")
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

    f = open("current_ids.txt", "w")
    
    f.write("\n".join(elements))

    f.close()
    return str(new_id)

def parseLeaf(titleNode):
    f = open("paginas/folhas/" + titleNode + ".txt", "r")
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
    f = open("paginas/dados/" + titlePage + ".txt", "r")
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

def joinData(page_ids):
    # mesclar registros de paginas de dados do resultado de busca 
    registers = []

    for id in page_ids:
        registers.extend(parseData("page_"+str(id)))

    return registers

def parseIndex(titleNode):
    f = None
    try:
        f = open("paginas/indices/" + titleNode + ".txt", "r")
    except:
        return ERROR_ROOT

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

    f = open("paginas/indices/" + titleNode + ".txt", "w")
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
    f = open("paginas/folhas/leaf_" + new_leaf_id + ".txt", "w")

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
        f = open("paginas/dados/page_" + new_page_id + ".txt", "w")
        pageContent = ""
        
        for element in data:
            key = element['key']
            id_element = element['id']
            tipo = element['tipo']
            rotulo = element['rotulo']
            ano_colheita = element['ano_colheita']

            pageContent += "id: {},rotulo: {},ano_colheita: {},tipo: {}\n".format(str(id_element), rotulo, str(ano_colheita), tipo)
        
        f.write(pageContent)
        f.close()
        

def ORDERDataNode(data):
    return sorted(data, key=lambda d: d['key']) 

def checkLeafMinimum(key, childNode, parentNode):
    currentContent = parseIndex(parentNode)
    
    for element in currentContent:
        if element["right"] == childNode:
            if element["key"] != key:
                editIndex(parentNode, element["key"], newKey=key)
            break

def shiftIndexLeft(titleNode):

    currentNode = parseIndex(titleNode)

    pos, parent, nodeParent = deepInfoIndex(titleNode)

    editIndex(nodeParent, parent["key"], newKey=currentNode[0]["key"])

    f = open("paginas/indices/"+titleNode+".txt", "r")
    operations = f.read().split('\n')
    operations[:] = [x for x in operations if x]

    new_content = ""

    f.close()

    f = open("paginas/indices/"+titleNode+".txt", "w")

    for i, el in enumerate(operations):
        if i > 2:
            new_content += el + "\n"

    f.write(new_content)
    f.close()


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
    
    f = open("paginas/folhas/" + titleNode + ".txt", "w+", encoding="utf-8")

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
        f = open("paginas/dados/page_" + page_id + ".txt", "w")
        pageContent = ""

        for element in registrosPag:
            pageContent += "id: {},rotulo: {},ano_colheita: {},tipo: {}\n".format(element["id"], element["rotulo"], element["ano_colheita"], element["tipo"])

        for element in data:
            key = element['key']
            id_element = element['id']
            tipo = element['tipo']
            rotulo = element['rotulo']
            ano_colheita = element['ano_colheita']
            pageContent += "id: {},rotulo: {},ano_colheita: {},tipo: {}\n".format(str(id_element), rotulo, str(ano_colheita), tipo)

        f.write(pageContent)
        f.close()

    else:
        #chave ainda não está presente na folha
        f = open("paginas/folhas/" + titleNode + ".txt", "w+", encoding="utf-8")

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
            f = open("paginas/dados/page_" + page_id + ".txt", "w+")
            pageContent = ""

            for element in data:
                key = element['key']
                id_element = element['id']
                tipo = element['tipo']
                rotulo = element['rotulo']
                ano_colheita = element['ano_colheita']

                pageContent += "id: {},rotulo: {},ano_colheita: {},tipo: {}\n".format(str(id_element), rotulo, str(ano_colheita), tipo)
            
            f.write(pageContent)
            f.close() 

def addInIndex(titleNode, data):
    f = open("paginas/indices/" + titleNode + ".txt", "r")
    oldContent = f.readlines()
    oldContent = ''.join(oldContent)

    arrayToSort = parseIndex(titleNode)
    for element in data:
        arrayToSort.append(element)

    f.close()

    f = open("paginas/indices/" + titleNode + ".txt", "w+", encoding="utf-8")
    newContent = ''

    for element in ORDERDataNode(arrayToSort):
        key = element['key']
        left = element['left']
        right = element['right']

        newContent += "key: {}\nleft: {} \nright: {}\n\n".format(str(key), left, right)
    
    f.write(newContent)
    f.close()   

def deleteFileLeaf(titleNode):
    os.remove("paginas/folhas/" + titleNode + ".txt")

def deleteFileNode(titleNode):
    os.remove("paginas/indices/" + titleNode + ".txt")

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

                editIndex(parentName, key=keyParent, newLeft='null')
                
                addInIndex(parentName, [{
                    'key': rightContent[0]['key'],
                    'left': leftLeafName,
                    'right': rightLeafName,
                }])
                
                editLeaf(nextName, newBack=rightLeafName)

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
                
                editIndex(parentName, key=keyParent, newRight=leftLeafName)

                addInIndex(parentName, [{
                    'key': rightContent[0]['key'],
                    'left': 'null',
                    'right': rightLeafName,
                }])
                
                editLeaf(backName, newNext=leftLeafName)

                deleteFileLeaf(titleNode)


            if (len(parsedParent) == ORDER - 1):
                splitIndex(parentName)


def insertData(data):
    root = parseIndex('node_root')

    if root == ERROR_ROOT:
        # verifica se já existe algum nó-folha sendo construído
        contentLeaf = os.listdir(path='./paginas/folhas')
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
            referenceNode, position = getRangeOfKey(data['key'], actualNode)

            page = actualNode[referenceNode][position]
            

        addInLeaf(page, [data])
        leafContent = parseLeaf(page)
        
        if (len(leafContent) - 3 == ORDER):
            splitLeaf(page)


def removeData(key):
    registers = []

    contentLeaf = os.listdir(path='./paginas/indices')

    if len(contentLeaf) == 0:
        contentLeaf = os.listdir(path='./paginas/folhas')
        startNode = contentLeaf[0][:-4]

        registers = searchInLeaf(startNode, key, "=") 

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
        
        registers = searchInLeaf(page, key, "=")

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
    contentIndices = os.listdir(path='./paginas/indices')
    
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
                editLeaf(index['left'], newParent=leftName)
            if (index['right'] != 'null'):
                editLeaf(index['right'], newParent=leftName)

        for index in rightContent:
            if (index['left'] != 'null'):
                editLeaf(index['left'], newParent=rightName)
            if (index['right'] != 'null'):
                editLeaf(index['right'], newParent=rightName) 

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
                        editLeaf(index['left'], newParent=leftName)
                    if (index['right'] != 'null'):
                        editLeaf(index['right'], newParent=leftName)

                for index in rightContent:
                    if (index['left'] != 'null'):
                        editLeaf(index['left'], newParent=rightName)
                    if (index['right'] != 'null'):
                        editLeaf(index['right'], newParent=rightName)

            createIndex(rightContent[1:], titleNode=rightName, leftNode=rightContent[0]["right"])
            createIndex(leftContent, titleNode=leftName)
            
            if pos == 'right':
                addInIndex(nodeParent, [{
                    'key': rightContent[0]['key'],
                    'right': rightName,
                    'left': 'null',
                }])
                editIndex(nodeParent, parent['key'], newRight=leftName)
                        
            if pos == 'left':
                addInIndex(nodeParent, [{
                    'key': rightContent[0]['key'],
                    'right': rightName,
                    'left': leftName,
                }])

                editIndex(nodeParent, parent['key'], newLeft='null')
                
            if (len(parseIndex(nodeParent)) == ORDER - 1):
                splitIndex(nodeParent)

            deleteFileNode(nodeTitle)


def readInput():
    # ler operacoes do arquivo de entrada e retornando uma lista de dicionarios para cada operacao
    f = open("in.txt", "r")
    operations = f.read().split('\n')
    operations[:] = [x for x in operations if x]

    # lendo primeira linha, aka informacao da quantidade filhos dos nos
    prim_l = operations.pop(0)
    if prim_l[:4] != "FLH/":
        print("Primeira linha deve ser a qntd de filhos!")
        return "",[]

    ops = []

    

    for op in operations:
        o = {}
        if op[:4] == "INC:":
            o["tipo"] = "INC"
            o["valor_c"] = int(op[4:])
        elif op[:4] == "REM:":
            o["tipo"] = "REM"
            o["valor_c"] = int(op[4:])
        elif op[:5] == "BUS=:":
            o["tipo"] = "BUS="
            o["valor_c"] = int(op[5:])
        elif op[:5] == "BUS>:":
            o["tipo"] = "BUS>"
            o["valor_c"] = int(op[5:])
        elif op[:5] == "BUS<:":
            o["tipo"] = "BUS<"
            o["valor_c"] = int(op[5:])
        else:
            print("Ignorando operacao invalida")
        ops.append(o)
    f.close()

    return prim_l, ops

def fetchCSV(ano_colheita):
    # buscar registros com ano_colheita especificado no vinhos.csv e retornar como dicionarios
    f = open("vinhos.csv", "r")
    registros = f.read().split('\n')
    registros[:] = [x for x in registros if x]

    registros.pop(0) # remover header

    dataList = []

    for reg in registros:
        print(reg)
        data = {}
        reg_split = reg.split(',')
        ano_c = int(reg_split[2])
        if ano_c == ano_colheita:
            data["id"] = reg_split[0]
            data["rotulo"] = reg_split[1]
            data["key"] = reg_split[2]
            data["tipo"] = reg_split[3]
            dataList.append(data)

    return dataList

def writeOutput(out):
    # escrever saida em out.txt
    f = open("out.txt", "w")

    f.write(out)
    f.close()

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


def searchInLeaf(page, opKey, mode):
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
        return joinData(page_ids)
    return page_ids

def search(opKey, mode):
    registers = []

    contentLeaf = os.listdir(path='./paginas/indices')

    if len(contentLeaf) == 0:
        contentLeaf = os.listdir(path='./paginas/folhas')
        startNode = contentLeaf[0][:-4]

        registers = searchInLeaf(startNode, opKey, mode) # retorna as tuplas encontradas 

    else:
        actualNode = parseIndex('node_root')

        if actualNode != ERROR_ROOT:

            referenceNode, position = getRangeOfKey(str(opKey), actualNode)

            page = actualNode[referenceNode][position]

            while(page.split('_')[0] != 'leaf'):
                actualNode = parseIndex(page)
                print(actualNode)
                referenceNode, position = getRangeOfKey(str(opKey), actualNode)
                page = actualNode[referenceNode][position]

            registers = searchInLeaf(page, opKey, mode) # retorna as tuplas encontradas 
        
    return registers

if len(sys.argv) > 1:
    if sys.argv[1] == "-reset":
        # apagar toda a estrutura de indexacao e os registros
        for mydir in ["paginas/dados/", "paginas/folhas/", "paginas/indices/"]:
            filelist = [ f for f in os.listdir(mydir) if f.endswith(".txt") ]
            for f in filelist:
                os.remove(os.path.join(mydir, f))

        # resetar arquivo de current_ids
        f = open("current_ids.txt", "w")
        reset_current_ids = "internal_node: 0\nleaf_node: 0\npage_id: 0"
        f.write(reset_current_ids)
        print("Tudo resetado")
        f.close()
        sys.exit()

modo_teste = True
if modo_teste:
    # testar comandos sem o arquivo de entrada
    # insertData({"key": "a", "tipo": "lalal", "rotulo": "opopopo", "id": "19", "ano_colheita": "1984"})
    # insertData({"key": 'b', "tipo": "rose", "rotulo": "bla_bla", "id": '9', "ano_colheita": "2021"})
    # insertData({"key": 'c', "tipo": "cabernet", "rotulo": "xxxxxx", "id": '155', "ano_colheita": "1904"})
    # insertData({"key": "d", "tipo": "ssss", "rotulo": "bla_bla", "id": "30", "ano_colheita": "1866"})
    # insertData({"key": "kakaka", "tipo": "ssss", "rotulo": "bla_bla", "id": "30", "ano_colheita": "2003"})
    # insertData({"key": "uuu", "tipo": "hhhhh", "rotulo": "xyxyxyxy", "id": "344", "ano_colheita": "2003"})
    # insertData({"key": "ui", "tipo": "lalal", "rotulo": "opopopo", "id": "19", "ano_colheita": "2003"})
    # insertData({"key": "OP", "tipo": "lalal", "rotulo": "opopopo", "id": "20", "ano_colheita": "2003"})
    # insertData({"key": "eeee", "tipo": "lalal", "rotulo": "opopopo", "id": "21", "ano_colheita": "2003"})
    # insertData({"key": "leleo", "tipo": "lalal", "rotulo": "opopopo", "id": "22", "ano_colheita": "2003"})
    # print(search('d', '='))
    # removeData('eeee')
    #insertData({"key": "9", "tipo": "hhhhh", "rotulo": "xyxyxyxy", "id": "344"})
    #insertData({"key": "10", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "11", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "12", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "13", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "14", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "20", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "21", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "22", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "15", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "16", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #removeData(22)
    #removeData(21)
    
    #insertData({"key": "16", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "17", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #removeData(17)
    #removeData(15)
    #removeData(23)
    #insertData({"key": "18", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "19", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "20", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "21", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "22", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "23", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "24", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "25", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    #insertData({"key": "26", "tipo": "lalal", "rotulo": "opopopo", "id": "19"})
    
    #print(search(5000, '='))
    #print(search(1889, '<'))
    #print(search(1800, '<'))
    pass
else:
    # ler e executar operacoes do arquivo de entrada

    header, ops = readInput()

    if ops:
        output = header + "\n"
        
        for op in ops:
            if op["tipo"] == "INC":
                # buscar registros e inserir na indexacao
                regs = fetchCSV(int(op["valor_c"]))
                for reg in regs:
                    insertData(reg)

                # gerar saida da operacao de inclusao
                output += generateOutput(op["tipo"], op["valor_c"], len(regs))
            elif op["tipo"] == "REM":
                # realizar remocao por chave
                registers = removeData(int(op["valor_c"]))

                # gerar saida da operacao de busca por igualdade
                output += generateOutput(op["tipo"], op["valor_c"], registers)
            elif op["tipo"] == "BUS=":
                # realizar busca por igualdade
                registers = search(int(op["valor_c"]), '=')

                # gerar saida da operacao de busca por igualdade
                output += generateOutput(op["tipo"], op["valor_c"], len(registers))
            elif op["tipo"] == "BUS>":
                # realizar busca por maior que
                registers = search(int(op["valor_c"]), '>')
                chaves = []

                for reg in registers:
                    if reg["ano_colheita"] not in chaves:
                        chaves.append(reg["ano_colheita"])

                # gerar saida da operacao de busca por maior que
                output += generateOutput(op["tipo"], op["valor_c"], chaves)
            elif op["tipo"] == "BUS<":
                # realizar busca por menor que
                registers = search(int(op["valor_c"]), '<')
                chaves = []

                for reg in registers:
                    if reg["ano_colheita"] not in chaves:
                        chaves.append(reg["ano_colheita"])

                # gerar saida da operacao de busca por menor que
                output += generateOutput(op["tipo"], op["valor_c"], chaves)

        writeOutput(output)