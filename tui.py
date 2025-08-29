#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os
import json
import textwrap
import sys

# --- Conteúdo de conduta_extractor.py ---

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
        # Retorna uma mensagem de erro amigável para a TUI
        return [f"Erro: O arquivo '{filepath}' não foi encontrado."]
    except Exception as e:
        return [f"Ocorreu um erro ao ler o arquivo: {e}"]

    condutas_encontradas = []
    em_secao_conduta = False

    for linha in linhas:
        linha_strip = linha.strip()

        if linha_strip.startswith('[') and linha_strip.endswith(']'):
            if linha_strip.upper() == '[CONDUTA]':
                em_secao_conduta = True
            else:
                em_secao_conduta = False
            continue

        if em_secao_conduta and linha_strip:
            condutas_encontradas.append(linha_strip)

    return condutas_encontradas

# --- Conteúdo de conduta_translator.py ---

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

        if item.startswith('+'):
            partes = item[1:].split()
            if len(partes) >= 2:
                medicacao = partes[0]
                dose = partes[1]
                posologia = ' '.join(partes[2:]) if len(partes) > 2 else ''
                dicionario_item = {
                    'comando': 'ADICIONAR',
                    'medicacao': medicacao,
                    'dose': dose,
                    'posologia': posologia,
                    'descricao': f"Adicionar {medicacao} {dose} à lista de medicamentos"
                }
        elif item.startswith('!ENCAMINHO'):
            partes = item.split(' ', 1)
            if len(partes) == 2:
                servico = partes[1]
                dicionario_item = {
                    'comando': 'ENCAMINHAR',
                    'servico': servico,
                    'descricao': f"Encaminhar o paciente para {servico}"
                }
        elif item.startswith('!ORIENTO'):
            partes = item.split(' ', 1)
            if len(partes) == 2:
                orientacao = partes[1]
                dicionario_item = {
                    'comando': 'ORIENTAR',
                    'orientacao': orientacao,
                    'descricao': f"Orientar o paciente a {orientacao}"
                }
        else:
            dicionario_item = {
                'comando': 'DESCONHECIDO',
                'original': item,
                'descricao': 'Comando não reconhecido.'
            }
        
        if dicionario_item: # Adiciona apenas se um dicionário foi criado
            lista_traduzida.append(dicionario_item)

    return lista_traduzida

# --- Código original de tui.py (modificado) ---

def get_med_files():
    """Escaneia o diretório atual e retorna uma lista de arquivos .med."""
    return sorted([f for f in os.listdir('.') if f.endswith('.med')])

def draw_menu(stdscr, tabs, current_tab_idx):
    """Desenha o menu principal de abas."""
    h, w = stdscr.getmaxyx()
    menu_str = " | ".join(tabs)
    x_start = (w - len(menu_str)) // 2
    stdscr.addstr(1, x_start, menu_str)

    highlight_x = x_start
    for i, tab in enumerate(tabs):
        if i == current_tab_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(1, highlight_x, tab)
            stdscr.attroff(curses.color_pair(1))
        highlight_x += len(tab) + 3

def draw_content(stdscr, current_tab_idx, med_files, current_file_idx, selected_file, extractor_output, translator_output):
    """Desenha o conteúdo principal da tela baseado na aba e seleção."""
    h, w = stdscr.getmaxyx()
    content_win_y, content_win_x = 4, 2
    content_h, content_w = h - 6, w - 4

    for y in range(content_h):
        stdscr.addstr(content_win_y + y, content_win_x, " " * content_w)

    if current_tab_idx == 0:
        stdscr.addstr(content_win_y, content_win_x, "./")
        if not med_files:
            stdscr.addstr(content_win_y + 2, content_win_x, "Nenhum arquivo .med encontrado no diretório.")
            return
        for i, filename in enumerate(med_files):
            if i >= content_h - 1: break
            symbol = "o " if i == current_file_idx else "  "
            line_str = f"{symbol}{filename}"
            if i == current_file_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(content_win_y + 1 + i, content_win_x, line_str)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(content_win_y + 1 + i, content_win_x, line_str)
    else:
        if not selected_file:
            stdscr.addstr(content_win_y, content_win_x, "Nenhum arquivo selecionado. Volte e pressione Enter em um arquivo.")
            return

        if current_tab_idx == 1:
            if not extractor_output:
                stdscr.addstr(content_win_y, content_win_x, "Nenhuma conduta encontrada neste arquivo.")
                return
            for i, line in enumerate(extractor_output):
                if i >= content_h: break
                stdscr.addstr(content_win_y + i, content_win_x, line)
        elif current_tab_idx == 2:
            if not translator_output:
                stdscr.addstr(content_win_y, content_win_x, "Nenhuma conduta para traduzir neste arquivo.")
                return
            pretty_json = json.dumps(translator_output, indent=2, ensure_ascii=False)
            json_lines = pretty_json.split('\n')
            wrapped_lines = []
            for line in json_lines:
                wrapped_lines.extend(textwrap.wrap(line, width=content_w))
            for i, line in enumerate(wrapped_lines):
                if i >= content_h: break
                stdscr.addstr(content_win_y + i, content_win_x, line)

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    tabs = ["SELECIONAR ARQUIVO", "CONDUTA EXTRACTOR", "CONDUTA TRANSLATOR"]
    current_tab_idx = 0
    med_files = get_med_files()
    current_file_idx = 0
    selected_file = None
    extractor_output = []
    translator_output = []
    
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear()

        title = f" CONDUTA EXPLORER - {selected_file if selected_file else 'Nenhum arquivo selecionado'} "
        stdscr.addstr(0, (w - len(title)) // 2, title)

        draw_menu(stdscr, tabs, current_tab_idx)
        
        stdscr.hline(2, 0, '-', w)
        stdscr.hline(h - 2, 0, '-', w)

        draw_content(stdscr, current_tab_idx, med_files, current_file_idx, selected_file, extractor_output, translator_output)
        
        instructions = "Setas para navegar | Enter para selecionar | Q para sair"
        stdscr.addstr(h - 1, (w - len(instructions)) // 2, instructions)

        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_RIGHT:
            current_tab_idx = (current_tab_idx + 1) % len(tabs)
        elif key == curses.KEY_LEFT:
            current_tab_idx = (current_tab_idx - 1 + len(tabs)) % len(tabs)

        if current_tab_idx == 0 and med_files:
            if key == curses.KEY_DOWN:
                current_file_idx = (current_file_idx + 1) % len(med_files)
            elif key == curses.KEY_UP:
                current_file_idx = (current_file_idx - 1 + len(med_files)) % len(med_files)
            elif key == curses.KEY_ENTER or key == 10:
                selected_file = med_files[current_file_idx]
                extractor_output = conduta_extractor(selected_file)
                translator_output = translate_conduta(extractor_output)
                current_tab_idx = 1

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print("Ocorreu um erro ao executar a aplicação:")
        print(e)