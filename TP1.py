import statistics
import gzip
import time
import tracemalloc


class LinkedNode:
    def __init__(self,vtx):
        self.vtx = vtx
        self.next = None

class ArvoreGeradora:
    def __init__(self,vtx,pai,nivel):
        self.vtx = vtx
        self.pai = pai
        self.nivel = nivel

class Graph:
    def __init__(self, arquivo_relativo ,implementacao=1):

        with gzip.open(arquivo_relativo, 'rt') as f:
            lines = f.readlines()
            lines = [line.rstrip() for line in lines]
            num_vtx = int(lines[0])
            lines.pop(0)
            for i in range(len(lines)):
                new_edge = lines[i].split()
                new_edge[0] = int(new_edge[0])
                new_edge[1] = int(new_edge[1])
                lines[i] = new_edge

            self.num_vtx = num_vtx
            self.edges = lines

        self.implementacao = implementacao
        if self.implementacao == 2:
            self.graph_matrix = self.adjacency_matrix()
        if self.implementacao == 1:
            self.graph_list = self.adjacency_list()
        self.graus = self.calcula_graus()
        self.componentes = self.contar_componentes()
        with open('info_grafo.txt', 'w') as f:
            f.write(f'Numero de vertices: {self.num_vtx}// Numero de arestas: {len(self.edges)}// gmin: {self.gmin()}// gmax:{self.gmax()}// N Componentes: {len(self.componentes[0])} // Maior: {max(self.componentes[1])} // Menor: {min(self.componentes[1])}')
        
    def adjacency_matrix(self):
        colunas = self.num_vtx
        linhas = self.num_vtx
        matrix = []
        for i in range(linhas):
            linha = []
            for j in range(colunas):
                linha.append(0)
            matrix.append(linha)
        for edge in self.edges:
            linha = edge[0]
            coluna = edge[1]
            matrix[linha-1][coluna-1] = 1 # arestas começam no índice um
            matrix[coluna-1][linha-1] = 1 # matriz é simétrica
        return matrix

    def adjacency_list(self):
        list = [None] * self.num_vtx
        for i in range(self.num_vtx):
            list[i] = LinkedNode(i+1)
        for edge in self.edges:
            vtx1 = edge[0]
            vtx2 = edge[1]
            
            node = list[vtx1-1]
            while node.next != None:
                node = node.next
            node.next = LinkedNode(vtx2)

            node = list[vtx2-1]
            while node.next != None:
                node = node.next
            node.next = LinkedNode(vtx1)

        return list

    def BFS(self,vtx):
        marcado = [False] * self.num_vtx
        fila = []
        arvore_geradora = []
        pais = [None] * self.num_vtx
        niveis = [None] * self.num_vtx

        fila.append(vtx)
        marcado[vtx-1] = True # como os vértices começam no índice 1, precisamos decrementar a posição em marcado
        contador=0

        pais[vtx-1] = 0
        niveis[vtx-1] = 0

        while fila:
            vtx = fila.pop(0)
            contador +=1
            
            #print (vtx, end = " ")
            arvore_geradora.append(ArvoreGeradora(vtx,pais[vtx-1],niveis[vtx-1]))

            #para todo vizinho de vtx w
            #ordena vizinhos
            #se w não marcado,
            #marca e adiciona na fila
            vizinhos_desmarcados = []
            if self.implementacao == 1:
                node = self.graph_list[vtx-1]
                while node.next != None:
                    node = node.next
                    if marcado[node.vtx - 1] == False:
                        vizinhos_desmarcados.append(node.vtx)
            if self.implementacao == 2:
                node = self.graph_matrix[vtx-1]
                for i in range(self.num_vtx):
                    if node[i] == 1:
                        if marcado[i] == False:
                            vizinhos_desmarcados.append(i+1)

            if len(vizinhos_desmarcados) > 0:
                
                vizinhos_desmarcados = sorted(vizinhos_desmarcados)
                for i in vizinhos_desmarcados:
                    fila.append(i)
                    marcado[i-1] = True
                    pais[i-1] = vtx
                    niveis[i-1] = niveis[vtx-1] + 1  
            
        with open('info_BFS.txt', 'w') as b:
            for k in arvore_geradora:
                b.write(f'Vertice: {k.vtx}, pai: {k.pai}, nivel:{k.nivel} //')
        return arvore_geradora, marcado

    def DFS(self,vtx):
        marcado = [False] * self.num_vtx
        pilha = []
        arvore_geradora = []
        pais = [None] * self.num_vtx
        niveis = [None] * self.num_vtx

        pais[vtx-1] = 0
        niveis[vtx-1] = 0
        pilha.append(vtx)

        while pilha:
            vtx = pilha.pop()
            
            if marcado[vtx-1] == False:
                marcado[vtx-1] = True
                
                #print (vtx, end = " ")
                arvore_geradora.append(ArvoreGeradora(vtx,pais[vtx-1],niveis[vtx-1]))

                vizinhos = []
                if self.implementacao == 1:
                    node = self.graph_list[vtx-1]
                    while node.next != None:
                        node = node.next
                        vizinhos.append(node.vtx)
                if self.implementacao == 2:
                    node = self.graph_matrix[vtx-1]
                    for i in range(self.num_vtx):
                        if node[i] == 1:
                            vizinhos.append(i+1)

                if len(vizinhos) > 0:
                    vizinhos = sorted(vizinhos)
                    #loop de tras p frente add pilha
                    for i in reversed(vizinhos):
                        pilha.append(i)
                        pais[i-1] = vtx
                        niveis[i-1] = niveis[vtx-1] + 1
                 

        with open('info_DFS.txt', 'w') as d:
            for k in arvore_geradora:
                d.write(f'Vertice: {k.vtx}, pai: {k.pai}, nivel:{k.nivel} //')
        return arvore_geradora

    def calcula_distancia(self,vtx1,vtx2):
        BFS_vtx1 = self.BFS(vtx1)
        marcado = BFS_vtx1[1]
        if marcado[vtx2-1] == False:
            print('Nao existe caminho')
            return None
        else: 
          for i in BFS_vtx1[0] : #arvore_geradora
            if i.vtx == vtx2:
                print(f'A distancia e de {i.nivel} vertices')
                return i.nivel

    def contar_componentes(self):
        marcado = [False] * self.num_vtx
        vtx_por_componente = []
        vertices = []
        componentes = 0 
        soma_contadores = 0
        while soma_contadores != self.num_vtx:
            for i in range(len(marcado)):
                if marcado[i] == False:
                    vtx = i+1 #soma pq quando marcamos vtx, marcamos na posição vtx-1
                    break
            BFS_vtx = self.BFS(vtx)
            #iterar dentro do vetor de marcação
            contador = 0
            componente_atual = []
            for i in range(len(BFS_vtx[1])):
                if BFS_vtx[1][i] == True:
                    marcado[i] = True
                    contador += 1
                    soma_contadores += 1
                    componente_atual.append(i+1)
            componentes += 1
            vtx_por_componente.append(contador)
            vertices.append(componente_atual)

        print(f'Temos {componentes} componente(s) neste grafo, maior: {max(vtx_por_componente)}, menor: {min(vtx_por_componente)}')
        with open('info_componentes.txt', 'w') as c:
            for i in range(len(vertices)):
                c.write(f'Componente {i+1} : ')
                for j in vertices[i]:
                    c.write(f'Vertice: {j} //')
        return vertices, vtx_por_componente

    def calcula_diametro(self):
        maximos = [0] * self.num_vtx
        for i in range(1,self.num_vtx + 1):
            BFS_vtx = self.BFS(i)
            maximo_vizinho = BFS_vtx[0].pop() #ultimo elemento do vetor arvore_geradora
            maximo_vizinho = maximo_vizinho.nivel
            maximos[i-1] = maximo_vizinho
        diametro = max(maximos)
        print(f'Diametro: {diametro}')
        return diametro

    def diametro_aproximado(self):
        componentes = self.componentes[0]
        distancia_componente = []
        for i in componentes:
            BFS_primeiro = self.BFS(i[0])[0] #vetor da arvore geradora p primeiro elemento descoberto
            BFS_primeiro = BFS_primeiro.pop()
            BFS_primeiro = BFS_primeiro.nivel #distancia do elemento mais distante
            distancia_componente.append(BFS_primeiro)
        
        return max(distancia_componente)


    def calcula_graus(self):
        if self.implementacao == 2:
            graus = []
            for linha in self.graph_matrix:
                soma = 0
                for i in range(self.num_vtx):
                    soma += linha[i]
                graus.append(soma)
            return graus
        if self.implementacao==1:
            graus = []
            for i in range(self.num_vtx):
                vizinhos = 0
                node = self.graph_list[i]
                while node.next != None:
                    node = node.next
                    vizinhos+=1
                graus.append(vizinhos)
            return graus
    
    def num_edges(self):
        soma_graus = 0
        for grau in self.graus:
            soma_graus += grau
        return int(soma_graus / 2)

    def gmin(self):
        minimo = min(self.graus)
        return minimo

    def gmax(self):
        maximo = max(self.graus)
        return maximo

    def gmed(self):
        soma_graus = 0
        for grau in self.graus:
            soma_graus += grau 
        return soma_graus / self.num_vtx

    def mediana_grau(self):
        return statistics.median(self.graus)


tracemalloc.start()
G4 = Graph('Teoria dos Grafos\grafos_TP1\grafo_4.txt.gz',1)
print(tracemalloc.get_traced_memory())
tracemalloc.stop()

def mil_BFS(G):
    inicio = time.time()
    for i in range(1000):
        if i%100 == 0:
            print('Ainda to aqui')
        i = i % G.num_vtx
        G.BFS(i)   
    fim = time.time()
    tempo_medio = (fim - inicio) / 1000
    print(f'Tempo de exec: {tempo_medio} ')
    return tempo_medio

def mil_DFS(G):
    inicio = time.time()
    for i in range(1000):
        if i%100 == 0:
            print('Ainda to aqui')
        i = i % G.num_vtx
        G.DFS(i)
    fim = time.time()
    tempo_medio = (fim - inicio) / 1000
    print(f'Tempo de exec: {tempo_medio} ')
    return tempo_medio




    
    
            

   
    

