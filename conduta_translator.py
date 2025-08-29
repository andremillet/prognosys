#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def translate_conduta(lista_de_condutas):
    """
    Recebe uma lista de strings (condutas) e a transforma em uma
    lista de dicionários estruturados.

    Args:
        lista_de_condutas (list): A lista de strings gerada pelo conduta-extractor.

    Returns:
        list: Uma lista de dicionários, onde cada um representa uma conduta traduzida.
    """
    lista_traduzida = []

    for item in lista_de_condutas:
        dicionario_item = {}

        # Regra 1: Adicionar Medicamento (começa com '+')
        if item.startswith('+'):
            # Remove o '+' e divide a string em partes
            partes = item[1:].split()
            
            # Garante que há partes suficientes para evitar erros
            if len(partes) >= 2:
                medicacao = partes[0]
                dose = partes[1]
                # Pega todo o resto como posologia, caso haja mais de uma palavra
                posologia = ' '.join(partes[2:]) if len(partes) > 2 else ''

                dicionario_item = {
                    'comando': 'ADICIONAR',
                    'medicacao': medicacao,
                    'dose': dose,
                    'posologia': posologia,
                    'descricao': f"Adicionar {medicacao} {dose} à lista de medicamentos"
                }

        # Regra 2: Encaminhar Paciente (começa com '!ENCAMINHO')
        elif item.startswith('!ENCAMINHO'):
            # Divide a string apenas uma vez para separar o comando do serviço
            partes = item[1:].split(' ', 1)
            
            if len(partes) == 2:
                servico = partes[1]
                dicionario_item = {
                    'comando': 'ENCAMINHAR',
                    'servico': servico,
                    'descricao': f"Encaminhar o paciente para {servico}"
                }

        # Regra 3: Orientar Paciente (começa com '!ORIENTO')
        elif item.startswith('!ORIENTO'):
            # Divide a string apenas uma vez para separar o comando da orientação
            partes = item[1:].split(' ', 1)
            
            if len(partes) == 2:
                orientacao = partes[1]
                dicionario_item = {
                    'comando': 'ORIENTAR',
                    'orientacao': orientacao,
                    'descricao': f"Orientar o paciente a {orientacao}"
                }
        
        # Se nenhuma regra corresponder, cria um item genérico
        else:
            dicionario_item = {
                'comando': 'DESCONHECIDO',
                'original': item,
                'descricao': 'Comando não reconhecido.'
            }
            
        lista_traduzida.append(dicionario_item)

    return lista_traduzida

# --- Bloco de Exemplo de Uso ---
if __name__ == "__main__":
    # Esta é a lista que viria do 'conduta-extractor.py'
    lista_exemplo_input = [
        '+AMITRIPTILINA 25MG NOITE',
        '+LOSARTANA 50MG MANHA E NOITE', # Exemplo com posologia maior
        '!ENCAMINHO PSICOLOGIA',
        '!ORIENTO ATIVIDADE FISICA REGULAR',
        '-SUTURA 3 PONTOS' # Exemplo de um comando não reconhecido
    ]

    print("--- Lista de Entrada ---")
    print(lista_exemplo_input)
    print("\n" + "="*30 + "\n")

    # Chama a função para traduzir a lista
    lista_traduzida_output = translate_conduta(lista_exemplo_input)

    print("--- Lista de Saída (Traduzida) ---")
    # Usa json.dumps para imprimir a lista de dicionários de forma legível
    print(json.dumps(lista_traduzida_output, indent=2, ensure_ascii=False))
