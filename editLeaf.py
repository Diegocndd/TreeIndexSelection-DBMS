def editLeaf(titleNode, newNext=None, newParent=None, newBack=None):
    f = open("paginas/folhas/" + titleNode + ".txt", "r")
    elements = f.read().split('\n')
    elements[:] = [x for x in elements if x]

    newContent = ''

    if newNext != None:
        for el in elements:
            if el.split(':')[0] == 'key' or el.split(':')[0] == 'next':
                newContent += '\n'
            if el.split(':')[0] == 'next':
                newContent += 'next: ' + str(newNext) + '\n'
            else:
                newContent += el + '\n'

    if newParent != None:
        for el in elements:
            if el.split(':')[0] == 'key' or el.split(':')[0] == 'next':
                newContent += '\n'
            if el.split(':')[0] == 'parent':
                newContent += 'parent: ' + str(newParent) + '\n'
            else:
                newContent += el + '\n'

    if newBack != None:
        for el in elements:
            if el.split(':')[0] == 'key' or el.split(':')[0] == 'next':
                newContent += '\n'
            if el.split(':')[0] == 'back':
                newContent += 'back: ' + str(newBack) + '\n'
            else:
                newContent += el + '\n'

    f.close()
    f = open("paginas/folhas/" + titleNode + ".txt", "w")
    f.write(newContent)
    f.close()
