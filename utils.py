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
