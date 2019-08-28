import sys
from copy import deepcopy
from math import floor
from random import randrange, choice, seed

import pygame as pg
from pygame.math import Vector3

'''
Para generar
https://github.com/pgorsira/hashiwokakero
'''

''' 
¡¡¡¡Para no duplicar la documentación en los métodos verticales y horizontales, solo se documentará en detalle y los pasos de los horizontales!!!!
'''

# Permite mostrar los puentes antes de construirlos
PREVISUALIZAR = True
# Resuelve el juego solo, Tiene preferencia y no permite jugar
AUTOPLAY = True

# Vector con los puentes de tipo horizontal la posicion indica la cantidad de puentes para ese valor
puente_horizontal = [(-1, 0), (-2, 0)]
# Vector con los puentes de tipo vertical la posicion indica la cantidad de puentes para ese valor
puente_vertical = [(0, -1), (0, -2)]

# Vector con todos los posibles valores de un puente, el primer valor será el de por defecto
puente = [0] + puente_horizontal + puente_vertical

# Número de pixeles que ocupará el texto
TAMA_TEXTO = 30
# Número de pixeles que tendrá cada puente
TAMA_PUENTE = TAMA_TEXTO * 3

# Colores de las superficies
FONDO = (240, 240, 240)  # color del fondo
NODOS = (255, 255, 255)  # color para el centro de un nodo
NUMEROS = (0, 0, 0)  # color para los valores de los nodos y el borde de los nodos
PUENTES = (0, 0, 0)  # color de los puentes
PUENTES_FONDO = Vector3(PUENTES).lerp(Vector3(FONDO), 0.7)  # color especial para puentes por defecto
MARCADO = (255, 0, 0)  # color del borde en los nodos marcados
VISITADO = (255, 128, 0)
COMPLETADO = (0, 128, 0)

ESPACIO = 5  # espacio entre los nodos y el borde exterior


def dibujar_texto(surface, texto, pos, color=(0, 0, 0), fuente='Comic Sans MS'):
    '''
Mostrar texto en pantalla
    :param surface: superficie sobre la que se dibujará
    :param texto: texto que se mostrará
    :param pos: posición del texto
    :param color: color del texto
    :param fuente: fuente precargada en el sistema
    '''
    # text = str(texto)
    # font = pygame.font.Font(font_type, size)
    # text = font.render(text, True, color)
    # screen.blit(text, (x, y))
    # Sobre la superficie indicada se utiliza una fuente con un tamaño, se renderiza ese texto con ese color y se pone en esa posición
    surface.blit(pg.font.SysFont(fuente, TAMA_TEXTO).render(texto, True, color), pos)


def calcular_horizontal(tablero, i, j):
    '''
    Calcular los nodos extremos de un puente horizontal
    :param tablero: matriz con los datos
    :param i: fila del puente
    :param j: columna del puente
    :return: vector con coordenadas de los nodos mas cecanos a los lados de esa posicion
    '''
    extremos = []  # vector con las posiciones de los nodos en los extremos
    if tablero[i][j] in puente:  # si la posicion que se pasa es un puente entonces tendrá extremos
        # empezamos de izquierda a derecha para que los extremos estén ordenados de menor a mayor
        # izquierda
        pos = j
        '''
        nos desplazamos a la izquierda hasta que no podamos más:
            -llegamos al tope
            -llegamos a un nodo o un puente que corta el paso (vertical)
        '''
        while pos != 0 and (tablero[i][pos] == puente[0] or (not AUTOPLAY and tablero[i][pos] in puente_horizontal)):
            pos -= 1

        # si llegamos a un puente tenemos exito
        if tablero[i][pos] not in puente and valorar_nodo(tablero, i, pos) != 0:
            # añadimos la posicion de ese nodo al extremo
            extremos.append([i, pos])

        # repetimos la operación hacia el otro lado
        # derecha
        pos = j
        while pos != len(tablero[0]) - 1 and (
                tablero[i][pos] == puente[0] or (not AUTOPLAY and tablero[i][pos] in puente_horizontal)):
            pos += 1

        if tablero[i][pos] not in puente and valorar_nodo(tablero, i, pos) != 0:
            extremos.append([i, pos])

    return extremos


def calcular_vertical(tablero, i, j):
    '''
    Calcular los nodos extremos de un puente vertical
    :param tablero: matriz con los datos
    :param i: fila del puente
    :param j: columna del puente
    :return: vector con coordenadas de los nodos mas cecanos a los lados de esa posicion
    '''
    extremos = []
    if tablero[i][j] in puente:
        # arriba
        pos = i
        while pos != 0 and (tablero[pos][j] == puente[0] or (not AUTOPLAY and tablero[pos][j] in puente_vertical)):
            pos -= 1

        if tablero[pos][j] not in puente and valorar_nodo(tablero, pos, j) != 0:
            extremos.append([pos, j])

        # abajo
        pos = i
        while pos != len(tablero) - 1 and (
                tablero[pos][j] == puente[0] or (not AUTOPLAY and tablero[pos][j] in puente_vertical)):
            pos += 1

        if tablero[pos][j] not in puente and valorar_nodo(tablero, pos, j) != 0:
            extremos.append([pos, j])

    return extremos


def dibujar_horizontal(pantalla, color, x, y, ancho=1):
    '''
    Dibuja una linea horizontal con longitud fija
    :param pantalla: superficie sobre la que se dibuja
    :param color: color de la linea
    :param x: x de la linea
    :param y: y de la linea
    :param ancho: anchura de la linea 1 por defecto
    '''
    # Se dibuja una linea sobre esa superficie con esas coordenadas y con la longitud de un puente y el ancho especificado
    pg.draw.line(pantalla, color, (x, y), (x + TAMA_PUENTE + TAMA_TEXTO, y), ancho)


def dibujar_vertical(pantalla, color, x, y, ancho=1):
    '''
    Dibuja una linea vertical con longitud fija
    :param pantalla: superficie sobre la que se dibuja
    :param color: color de la linea
    :param x: x de la linea
    :param y: y de la linea
    :param ancho: anchura de la linea 1 por defecto
    '''
    pg.draw.line(pantalla, color, (x, y), (x, y + TAMA_PUENTE + TAMA_TEXTO), ancho)


def dibujar_horizontales(pantalla, tablero, i, j):
    '''
    Dibuja un numero de lineas paralelas horizontales dependiendo del valor en la posicion
    :param pantalla: pantalla sobre la que se dibuja
    :param tablero: matriz con los datos
    :param i: fila en la que comienzan las lineas
    :param j: columna en la que comienzan las lineas
    '''
    # Si no esta en el borde y no hay un puente vertical ni en la actual ni la siguiente
    if j != len(tablero[0]) - 1 and tablero[i][j] not in puente_vertical and tablero[i][j + 1] not in puente_vertical:
        # se intenta calcular el indice para saber cuantos puentes dibujar
        try:
            if tablero[i][j] in puente:
                indice = puente_horizontal.index(tablero[i][j]) + 1
            else:
                indice = puente_horizontal.index(tablero[i][j + 1]) + 1
        except ValueError:
            indice = 1

        # numero de puentes que se dibujan
        nlineas = floor(indice / 2)

        # color de los puentes
        color = PUENTES_FONDO
        ancho = 1

        if tablero[i][j] in puente[1:] or tablero[i][j + 1] in puente[1:]:
            color = PUENTES
            ancho = 3

            # if not (tablero[i][j] in puente or tablero[i][j + 1] in puente):
            #     return

        # separacion de los puentes entre ellos
        separacion = TAMA_TEXTO / 4 + ancho

        # se calculan las coordenadas de los puentes teniendo en cuenta su posición en la matriz
        x = floor(TAMA_TEXTO + (j * TAMA_TEXTO + j * TAMA_PUENTE))
        y = floor(TAMA_TEXTO + (i * TAMA_TEXTO + i * TAMA_PUENTE))

        # se clasifican si el número de puentes es par o impar
        if indice % 2 == 1:
            # impares
            dibujar_horizontal(pantalla, color, x, y, ancho)  # se dibuja la linea central

            # se dibujan lineas paralelas a ella con la separación apropiada
            for pos in range(nlineas):
                dibujar_horizontal(pantalla, color, x, y - (pos + 1) * separacion, ancho)
                dibujar_horizontal(pantalla, color, x, y + (pos + 1) * separacion, ancho)
        else:
            # pares
            # y = floor(TAMA_TEXTO - separacion / 2 + (i * TAMA_TEXTO + i * TAMA_PUENTE)) + separacion / 4 # las lineas salen desplazadas

            # se dibujan lineas paralelas
            for pos in range(nlineas):
                dibujar_horizontal(pantalla, color, x, y - pos * separacion, ancho)
                dibujar_horizontal(pantalla, color, x, y + (pos + 1) * separacion, ancho)

        # se dibujan los puentes a su derecha
        # derecha
        dibujar_horizontales(pantalla, tablero, i, j + 1)


def dibujar_verticales(pantalla, tablero, i, j):
    '''
        Dibuja un numero de lineas paralelas verticales dependiendo del valor en la posicion
        :param pantalla: pantalla sobre la que se dibuja
        :param tablero: matriz con los datos
        :param i: fila en la que comienzan las lineas
        :param j: columna en la que comienzan las lineas
        '''
    if i != len(tablero) - 1 and tablero[i][j] not in puente_horizontal and tablero[i + 1][j] not in puente_horizontal:
        try:
            if tablero[i][j] in puente:
                indice = puente_vertical.index(tablero[i][j]) + 1
            else:
                indice = puente_vertical.index(tablero[i + 1][j]) + 1
        except ValueError:
            indice = 1

        nlineas = floor(indice / 2)

        color = PUENTES_FONDO
        ancho = 1

        if tablero[i][j] in puente[1:] or tablero[i + 1][j] in puente[1:]:
            color = PUENTES
            ancho = 3

        separacion = TAMA_TEXTO / 4 + ancho

        y = floor(TAMA_TEXTO + (i * TAMA_TEXTO + i * TAMA_PUENTE))
        x = floor(TAMA_TEXTO + (j * TAMA_TEXTO + j * TAMA_PUENTE))
        if indice % 2 == 1:
            dibujar_vertical(pantalla, color, x, y, ancho)

            for pos in range(nlineas):
                dibujar_vertical(pantalla, color, x - (pos + 1) * separacion, y, ancho)
                dibujar_vertical(pantalla, color, x + (pos + 1) * separacion, y, ancho)
        else:

            for pos in range(nlineas):
                dibujar_vertical(pantalla, color, x - pos * separacion, y, ancho)
                dibujar_vertical(pantalla, color, x + (pos + 1) * separacion, y, ancho)

        # abajo
        dibujar_verticales(pantalla, tablero, i + 1, j)


def construir_puente(tablero, extremos, valor):
    '''
    Cambia el valor de las posiciones uniendo nodos
    :param tablero: tablero sobre el que se dibuja
    :param extremos: nodos paralelos que se van a unir
    :param valor: valor que se pondra en esa posicion
    '''
    # dependiendo de si el puente es horizontal o no se pone un valor u otro
    if extremos[0][0] == extremos[1][0]:  # si las coordenadas X son la misma es horizontal
        i = extremos[0][0]
        for j in range(extremos[0][1] + 1, extremos[1][1]):  # se recorren los valores por columnas y se asigna el calor
            tablero[i][j] = valor
    else:  # en el caso de vertical
        j = extremos[0][1]
        for i in range(extremos[0][0] + 1, extremos[1][0]):
            tablero[i][j] = valor


def siguiente_puente(tipo_puente, tablero, i, j):
    '''
    Dependiendo del puente en una posicion se calculará el siguiente
    :param tipo_puente: vertical/horizontal
    :param tablero: matriz con los datos
    :param i: fila del puente
    :param j: columna del puente
    :return: valor que tendrá el siguiente puente
    '''
    try:
        # se busca el incide del puente actual en el vector de puentes
        indice = tipo_puente.index(tablero[i][j])  # aquie es donde puede dar el error al no estar
        if indice == len(tipo_puente) - 1:  # si se llega al final
            valor = puente[0]  # se pone el valor basico
        else:  # en otro caso se pone el siguiente puente
            indice += 1
            valor = tipo_puente[indice]

    except ValueError:
        valor = tipo_puente[0]  # si no existe se le da el valor del primer puente

    return valor


def construir(pos_raton, tablero):
    '''
    Dependiendo de la posicion del raton se calcula que puente se aproxima mejor
    :param pos_raton: coordenadas relativas del raton
    :param tablero: matriz donde se sustituiran los datos
    '''
    # se calcula la fila y la columna que tiene el raton
    fila_raton = (pos_raton.y - TAMA_TEXTO - ESPACIO) / (TAMA_TEXTO + TAMA_PUENTE)
    col_raton = (pos_raton.x - TAMA_TEXTO - ESPACIO) / (TAMA_TEXTO + TAMA_PUENTE)

    # se calcula la distancia del raton al indice mas cecano
    dx = fila_raton - round(fila_raton)
    dy = col_raton - round(col_raton)

    # se aproximan esos valores y se ajustan si se necesita
    fila_raton = round(fila_raton)
    col_raton = round(col_raton)

    if abs(dx) < abs(
            dy):  # se clasifica dependiendo de si el raton esta mas cerca de una horizontal que de una vertical
        if tablero[fila_raton][col_raton] not in puente:  # si esta en un nodo se calcula al más cercano
            # se incrementa o decrementa la columna dependiendo del signo del error
            if dy < 0 and col_raton != 0:
                col_raton -= 1
            elif col_raton != len(tablero[0]) - 1:
                col_raton += 1

        # se calculan el numero de nodos que pueden conectar con ese puente
        lados = calcular_horizontal(tablero, fila_raton, col_raton)
        # si el puente esta conectado por dos nodos se crea ese puente
        if len(lados) == 2:
            construir_puente(tablero, lados,
                             siguiente_puente(puente_horizontal, tablero, fila_raton, col_raton))
    else:
        if tablero[fila_raton][col_raton] not in puente:
            if dx < 0 and fila_raton != 0:
                fila_raton -= 1
            elif fila_raton != len(tablero) - 1:
                fila_raton += 1

        lados = calcular_vertical(tablero, fila_raton, col_raton)
        if len(lados) == 2:
            construir_puente(tablero, lados, siguiente_puente(puente_vertical, tablero, fila_raton, col_raton))


def valorar_puente(tablero, i, j):
    '''
    Valor del puente en una posicion (contar las lineas)
    :param tablero: matriz con los datos
    :param i: fila
    :param j: columna
    :return: valor de ese puente
    '''
    valor = 0  # valor por defecto
    if tablero[i][j] in puente:  # si es un puente
        valor = 0 if tablero[i][j] == puente[0] else tablero[i][j][0] + tablero[i][j][
            1]  # si es un puente por defecto tiene valor 0, si no se suman los valores del puente en esa posicion

    return valor


def valorar_nodo(tablero, i, j):
    '''
    Valor del nodo - suma del valor de los puentes con los que conecta
    :param tablero: matriz con los datos
    :param i: fila
    :param j: columna
    :return: valor de ese nodo
    '''
    suma = 0  # valor por inicial del nodo
    if tablero[i][j] not in puente:  # si es un nodo se calcula su suma
        suma = tablero[i][j]  # se le da el valor que tenga

        # arriba
        if i != 0 and (
                tablero[i - 1][j] == puente[0] or tablero[i - 1][j] in puente_vertical):  # si arriba tiene un puente
            suma += valorar_puente(tablero, i - 1, j)  # se suma el valor de ese puente

        # derecha
        if j != len(tablero[0]) - 1 and (tablero[i][j + 1] == puente[0] or tablero[i][j + 1] in puente_horizontal):
            suma += valorar_puente(tablero, i, j + 1)

        # abajo
        if i != len(tablero) - 1 and (tablero[i + 1][j] == puente[0] or tablero[i + 1][j] in puente_vertical):
            suma += valorar_puente(tablero, i + 1, j)

        # izquierda
        if j != 0 and (tablero[i][j - 1] == puente[0] or tablero[i][j - 1] in puente_horizontal):
            suma += valorar_puente(tablero, i, j - 1)

    return suma


def contar_espacios(tablero, i, j):
    '''
    Calcula las direciones sin puentes desde un nodo
    :param tablero: matriz con los datos
    :param i: fila
    :param j: columna
    :return: direcciones disponibles
    '''
    espacios = 0  # por defecto el nodo esta completo

    if tablero[i][j] not in puente:  # si es un nodo
        # arriba
        if i != 0 and tablero[i - 1][j] == puente[0] and len(
                calcular_vertical(tablero, i - 1, j)) == 2:  # buscamos hacia arriba si se puede conectar un puente
            espacios += 1

        # derecha
        if j != len(tablero[0]) - 1 and tablero[i][j + 1] == puente[0] and len(
                calcular_horizontal(tablero, i, j + 1)) == 2:
            espacios += 1

        # abajo
        if i != len(tablero) - 1 and tablero[i + 1][j] == puente[0] and len(calcular_vertical(tablero, i + 1, j)) == 2:
            espacios += 1

        # izquierda
        if j != 0 and tablero[i][j - 1] == puente[0] and len(calcular_horizontal(tablero, i, j - 1)) == 2:
            espacios += 1

    return espacios


def generar(length=7, width=7):
    '''
    Genera un tablero nuevo
    :param length: cantidad de filas
    :param width: cantidad de columnas
    :return: tablero para jugar
    '''
    '''
    Para generar
    https://github.com/pgorsira/hashiwokakero
    '''

    espacio = puente[0]

    vertical1 = puente_vertical[0]
    vertical2 = puente_vertical[1]

    horizontal1 = puente_horizontal[0]
    horizontal2 = puente_horizontal[1]

    reverse_direction = lambda direction: tuple([-1 * x for x in direction])

    generated = False

    attemps = 0

    MAX_NODES = floor((width * length) / 3)

    while not generated:

        num_nodes = MAX_NODES - attemps  # 25

        attemps += 1

        board = [[espacio for x in range(width)] for y in range(length)]  # solution (full board)

        # first node
        x = randrange(0, length)
        y = randrange(0, width)
        board[x][y] = '*'
        nodes = [(x, y)]
        directions = {nodes[-1]: []}

        looped = 0  # todo is this a dirty patch or a necessary fix

        while num_nodes > 1 and looped < 100:  # prepare board
            looped += 1

            home_node = choice(nodes)

            if len(directions[home_node]) == 4:  # all 4 directions used for this node
                continue

            direction_taken = True
            intentos = 0
            max_intentos = width * length
            while direction_taken:  # find an unused direction for this node
                dx = randrange(-1, 2)
                dy = randrange(-1, 2)
                direction = (dx, dy)
                direction_taken = direction in directions[home_node] or (abs(dx) == abs(dy))
                intentos += 1
                if intentos >= max_intentos:
                    # print('intentos ',intentos)
                    break

            if intentos >= max_intentos:
                continue

            x = home_node[0]
            y = home_node[1]

            # determine bridge specs
            double_bridge = randrange(0, 2) > 0.7

            if dx == 0:
                if double_bridge:
                    bridge = horizontal2
                else:
                    bridge = horizontal1

                if dy < 0:
                    dist_avail = y
                else:
                    dist_avail = width - y
            else:
                if double_bridge:
                    bridge = vertical2
                else:
                    bridge = vertical1

                if dx < 0:
                    dist_avail = x
                else:
                    dist_avail = length - x

            try:
                distance = randrange(2, dist_avail)
            except ValueError:  # no room
                continue

            d = 0

            new_node = tuple(a + b for a, b in zip(home_node, direction))
            x = new_node[0]
            y = new_node[1]

            bridges = [(x, y)]

            # check next space and next next space
            try:
                if board[x][y] != espacio or board[x + dx][
                    y + dy] != espacio or x < 0 or x + dx < 0 or y < 0 or y + dy < 0:
                    continue
            except IndexError:
                continue

            directions[home_node].append(direction)

            directions[home_node].append(direction)

            while d < distance and board[x][y] == espacio and 0 <= x < length and 0 <= y < width:
                new_node = tuple(a + b for a, b in zip(new_node, direction))
                x = new_node[0]
                y = new_node[1]
                bridges.append((x, y))
                d += 1

            # todo place node on bridge if possible (instead of instantly retreating)

            # undo last move
            new_node = tuple(a - b for a, b in zip(new_node, direction))
            bridges.remove((x, y))

            # add bridges
            for (x, y) in bridges:
                board[x][y] = bridge

            x = new_node[0]
            y = new_node[1]

            board[x][y] = '*'
            nodes.append(new_node)

            # note that this direction has been taken
            if new_node in direction:
                directions[new_node].append(reverse_direction(direction))
            else:
                directions[new_node] = [reverse_direction(direction)]
            num_nodes -= 1

            looped = 0

        if num_nodes == 1:
            generated = True

    usr_board = [[espacio for x in range(width)] for y in range(length)]  # user's board

    # nodes -> numbers
    for x in range(length):
        for y in range(width):
            if board[x][y] == '*':
                count = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if abs(dx) == abs(dy):
                            continue
                        try:
                            if (board[x + dx][y + dy] == vertical1 and dx != 0) or (
                                    board[x + dx][y + dy] == horizontal1 and dy != 0):
                                count += 1
                            if (board[x + dx][y + dy] == vertical2 and dx != 0) or (
                                    board[x + dx][y + dy] == horizontal2 and dy != 0):
                                count += 2
                        except IndexError:
                            pass

                board[x][y] = count
                usr_board[x][y] = count

    # print('\nPuzzle:')
    # print(usr_board)
    # print('\nSolution:')
    # print(board)

    return usr_board


def opciones(argumentos):
    global AUTOPLAY
    global PREVISUALIZAR

    if '--help' in argumentos:
        print('ayuda')

    if '--autoplay' in argumentos:
        print('autoplay')
        AUTOPLAY = True
    else:
        AUTOPLAY = False

    if '--prever' in argumentos:
        print('previsualizar')
        PREVISUALIZAR = True
    else:
        PREVISUALIZAR = False

    if '--tama' in argumentos:
        inidice = argumentos.index('--tama')
        if len(argumentos) < inidice + 2:
            raise ValueError('Debe indicarse el numero de filas y columnas')
        tama = [int(argumentos[inidice + 1]), int(argumentos[inidice + 2])]
    else:
        tama = [7, 7]

    return tama


def calcular_puentes(tablero, i, j):
    puentes = []

    if tablero[i][j] not in puente:
        suma = valorar_nodo(tablero, i, j)
        # valor = tablero[i][j]

        valor = 0
        # arriba
        if i != 0 and tablero[i - 1][j] in puente:
            lados = calcular_vertical(tablero, i - 1, j)
            if len(lados) == 2:  # si puedo poner un puente
                otro = lados[0]
                libres = contar_espacios(tablero, otro[0], otro[1])
                if libres == 1:
                    pass

        # derecha
        if j != len(tablero[0]) - 1:
            lados = calcular_horizontal(tablero, i, j + 1)
            if len(lados) == 2:
                construir_puente(tablero, lados, puente_horizontal[cantidad])

        # abajo
        if i != len(tablero) - 1:
            lados = calcular_vertical(tablero, i + 1, j)
            if len(lados) == 2:
                construir_puente(tablero, lados, puente_vertical[cantidad])

        # izquierda
        if j != 0:
            lados = calcular_horizontal(tablero, i, j - 1)
            if len(lados) == 2:
                construir_puente(tablero, lados, puente_horizontal[cantidad])

    return puentes


if __name__ == '__main__':

    seed(10)

    argumentos = sys.argv[1:]

    tama = opciones(argumentos)

    # tablero con los datos
    tablero = generar(tama[0], tama[1])

    # se calcula el tamaño de la ventana dependiendo del numero de columnas y filas
    ncol = floor((len(tablero[0]) + 1) * (TAMA_TEXTO) + ((len(tablero[0]) - 1) * TAMA_PUENTE))
    nfila = floor((len(tablero) + 1) * (TAMA_TEXTO) + ((len(tablero) - 1) * TAMA_PUENTE))

    # se inicializa pygame
    pg.init()
    # se crea esa pantalla con el espacio exterior
    pantalla = pg.display.set_mode([ncol + ESPACIO * 2, nfila + ESPACIO * 2])
    # se le pone el titulo a la ventana
    pg.display.set_caption("Hashiwokakero")

    # variable para saber cuando se ha cerrado la pantalla y salir
    running = True
    # relog para mantener los fps
    clock = pg.time.Clock()

    # vector con los nodos sin todos los puentes
    pendientes = []
    completados = []
    visitados = []
    # si no hay jugador se necesita ver donde estar los nodos
    if AUTOPLAY:
        # se recorre toda la matriz para añadir esos nodos al vector
        for fila in range(len(tablero)):
            for col in range(len(tablero[0])):
                if tablero[fila][col] not in puente:
                    pendientes.append([fila, col])

        if len(pendientes) != 0:  # mientras exitan nodos sin puentes
            actual = pendientes.pop(0)  # extraemos el primer valor
    else:  # en caso de tener un jugador no se marca ningun nodo al inicio
        actual = [-1, -1]  # valor fuera del rango

    try:
        while running:  # entramos en bucle mientras no se cierre el programa
            clock.tick(60)  # fps de la ventana

            if AUTOPLAY:  # se calculan datos para intentar resolver
                suma_actual = valorar_nodo(tablero, actual[0], actual[1])  # valor del nodo - valor de todos los puentes
                libres_actual = contar_espacios(tablero, actual[0], actual[1])  # caminos libres sin puente

                if suma_actual != 0:  # si el nodo no está completo
                    if libres_actual == 0:
                        # destruir imperios
                        print('?')
                        continue

                    if libres_actual == 1 or (
                            suma_actual % 2 == 0 and suma_actual / libres_actual == 2):  # si se puede resolver

                        # ponemos alias a las variables por comodidad
                        i = actual[0]
                        j = actual[1]

                        cantidad = floor((suma_actual / libres_actual) - 1)  # cantidad de puentes en cada dirección

                        # arriba
                        if i != 0:
                            lados = calcular_vertical(tablero, i - 1, j)
                            if len(lados) == 2:  # si puedo poner un puente
                                construir_puente(tablero, lados, puente_vertical[cantidad])

                        # derecha
                        if j != len(tablero[0]) - 1:
                            lados = calcular_horizontal(tablero, i, j + 1)
                            if len(lados) == 2:
                                construir_puente(tablero, lados, puente_horizontal[cantidad])

                        # abajo
                        if i != len(tablero) - 1:
                            lados = calcular_vertical(tablero, i + 1, j)
                            if len(lados) == 2:
                                construir_puente(tablero, lados, puente_vertical[cantidad])

                        # izquierda
                        if j != 0:
                            lados = calcular_horizontal(tablero, i, j - 1)
                            if len(lados) == 2:
                                construir_puente(tablero, lados, puente_horizontal[cantidad])

            # se dibuja el fondo
            pantalla.fill(FONDO)

            # se obtienen las coordenadas del raton
            raton = pg.math.Vector2(pg.mouse.get_pos())  # se crea un vector con esas coordenadas

            if not AUTOPLAY and PREVISUALIZAR:
                tablero_anterior = deepcopy(tablero)  # se hace una copia del tablero
                construir(raton, tablero)  # se pone un puente donde esta el raton

            # dibujar
            for fila in range(len(tablero)):
                for col in range(len(tablero[0])):
                    # se calculan las coordenadas para esa fila y columna
                    x = floor(TAMA_TEXTO + (col * TAMA_TEXTO + col * TAMA_PUENTE)) + ESPACIO
                    y = floor(TAMA_TEXTO + (fila * TAMA_TEXTO + fila * TAMA_PUENTE)) + ESPACIO

                    # se dibujan los puentes siempre, si no los nodos estarían desconectados del resto de lineas
                    dibujar_horizontales(pantalla, tablero, fila, col)
                    dibujar_verticales(pantalla, tablero, fila, col)

                    # se dibujan los nodos
                    if tablero[fila][col] not in puente:
                        # se dibuja el circulo central
                        pg.draw.circle(pantalla, NODOS, [x, y], TAMA_TEXTO)

                        # color del borde del nodo
                        color = NUMEROS

                        # cambiamos el color del nodo dependiendo de su estado
                        if (actual[0] == fila and actual[
                            1] == col):  # or raton.distance_to((x, y)) < TAMA_TEXTO:  # el actual
                            color = MARCADO
                        elif [fila, col] in completados:  # no volverán a visitarse
                            color = COMPLETADO
                        elif [fila, col] in visitados:  # se visitarán en la proxima vuelta
                            color = VISITADO

                        # se dibuja el borde del circulo
                        pg.draw.circle(pantalla, color, [x, y], TAMA_TEXTO, 2)

                        # se pone el valor de ese nodo
                        dibujar_texto(pantalla, str(tablero[fila][col]), (x - TAMA_TEXTO / 4, y - TAMA_TEXTO / 1.5),
                                      NUMEROS)

            # actualiza la pantalla para dibujar todos los elementos
            pg.display.flip()

            # indica si los cambios necesitan desacerse o no
            borrar = True

            # se recorren todos los eventos
            for event in pg.event.get():

                if event.type == pg.QUIT:  # si se hace click en cerrar
                    # se indica que el bucle debe finalizar
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_F5:
                        tablero = generar(tama[0], tama[1])

                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # si se pulsa un boton y es el boton izquierdo

                    # se actualiza el estado del nodo solo si debe jugar solo
                    if AUTOPLAY:
                        # si no se han añadido los puentes
                        if suma_actual != 0 and not (
                                suma_actual % 2 == 0 and suma_actual / libres_actual == 2):  # suma_actual != 0 and suma_actual % libres_actual != 0:
                            pendientes.append(actual)  # se añade al final para visitarlo otra vez
                            visitados.append(actual)  # se añade para cambiar el color mientras cambia el actual
                        else:  # tiene los puentes
                            completados.append(actual)  # se añade para cambiar el color del borde
                            if actual in visitados:  # si esta en el vector
                                visitados.remove(actual)  # se elimina al estar completado

                        if len(pendientes) != 0:  # mientras exitan nodos sin puentes
                            actual = pendientes.pop(0)  # extraemos el primer valor
                        else:  # al acabar
                            actual = [-1, -1]  # se asigna fuera del rango para desmarcar el ultimo
                    else:  # si hay un jugador se hacen las acciones normales
                        # no se borra y se dibuja el puente
                        borrar = False
                        if not PREVISUALIZAR:
                            # si no se previsualiza se construye el puente directamente
                            construir(raton, tablero)

            if not AUTOPLAY and PREVISUALIZAR and borrar:  # en caso de borrarse se desacen los cambios
                tablero = tablero_anterior  # se deshacen los cambios haechos

        pg.quit()
    except SystemExit:  # si hay un error o no se cierra el programa
        pg.quit()
