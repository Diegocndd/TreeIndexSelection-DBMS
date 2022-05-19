# VOCE DEVE INCLUIR SUAS IMPORTACOES AQUI, CASO NECESSARIO!!!

from estrutura import *

def main():
    # vinho = Tabela("vinho.csv") # cria estrutura necessaria para a tabela
    # uva = Tabela("uva.csv")
    pais = Tabela("pais.csv")
    
    # vinho.carregarDados() # le os dados do csv e add na estrutura da tabela, caso necessario
    # uva.carregarDados()
    pais.carregarDados()
    print('finalizou')
    ## DESCOMENTE A PROXIMA LINHA CASO SEU TRABALHO SEJA SELECAO:
    #op = Operador(vinho, ["ano_colheita", "uva_id"], ["1990", "0"])
    ## significa: SELECT * FROM Vinho WHERE ano_colheita = '1990' AND uva_id = '0'
    ## IMPORTANTE: isso eh so um exemplo, pode ser outra tabela e ter mais ou menos colunas/constantes.
    ## genericamente: Operador(tabela, lista_colunas, lista_constantes): 
    ## significa: SELECT * FROM tabela WHERE col_1 = con_1 AND col_2 = con_2 AND ... AND col_n = con_n

    #op.executar() # Realiza a operacao desejada
    
    #print("#Pags:", op.numPagsGeradas()) # Retorna a quantidade de paginas geradas pela operacao
    #print("#IOss:", op.numIOExecutados()) # Retorna a quantidade de IOs geradas pela operacao
    #print("#Tups:", op.numTuplasGeradas()) # Retorna a quantidade de tuplas geradas pela operacao
    
    #op.salvarTuplasGeradas("selecao_vinho_ano_colheita_1990.csv") # Retorna as tuplas geradas pela operacao e salva em um csv
    
main()