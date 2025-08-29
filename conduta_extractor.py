#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def conduta_extractor(filepath):
    """
    Abre um arquivo .med, encontra a seção [CONDUTA] e extrai
    seu conteúdo em uma lista de strings.

    Args:
        filepath (str): O caminho para o arquivo .med.

    Returns:
        list: Uma lista de strings contendo cada linha da conduta,
              ou uma lista vazia se a seção não for encontrada.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{filepath}' não foi encontrado.")
        sys.exit(1) # Encerra o programa com um código de erro
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        sys.exit(1)

    condutas_encontradas = []
    em_secao_conduta = False

    for linha in linhas:
        # Remove espaços em branco e quebras de linha do início e do fim
        linha_strip = linha.strip()

        # Se encontrarmos o início de uma nova seção...
        if linha_strip.startswith('[') and linha_strip.endswith(']'):
            if linha_strip.upper() == '[CONDUTA]':
                # Ativa o modo de captura
                em_secao_conduta = True
            else:
                # Desativa o modo de captura se encontrarmos outra seção
                em_secao_conduta = False
            # Pula para a próxima linha (não queremos incluir o '[CONDUTA]')
            continue

        # Se estivermos na seção correta e a linha não estiver vazia...
        if em_secao_conduta and linha_strip:
            condutas_encontradas.append(linha_strip)

    return condutas_encontradas

if __name__ == "__main__":
    # Verifica se o nome do arquivo foi passado como argumento
    if len(sys.argv) < 2:
        print("Uso: python conduta-extractor.py <nome-do-arquivo.med>")
        sys.exit(1) # Encerra o programa com um código de erro

    # O primeiro argumento (índice 1) é o nome do arquivo
    nome_do_arquivo = sys.argv[1]

    # Chama a função e armazena o resultado
    lista_de_condutas = conduta_extractor(nome_do_arquivo)

    # Imprime o resultado final
    print(lista_de_condutas)
    
