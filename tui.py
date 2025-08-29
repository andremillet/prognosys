#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import os
import json
import textwrap

# Importa as funções dos outros dois arquivos
from conduta_extractor import conduta_extractor
from conduta_translator import translate_conduta

def get_med_files():
    """Escaneia o diretório atual e retorna uma lista de arquivos .med."""
    return sorted([f for f in os.listdir('.') if f.endswith('.med')])

def draw_menu(stdscr, tabs, current_tab_idx):
    """Desenha o menu principal de abas."""
    h, w = stdscr.getmaxyx()
    menu_str = " | ".join(tabs)
    x_start = (w - len(menu_str)) // 2
    stdscr.addstr(1, x_start, menu_str)

    # Destaca a aba ativa
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
    content_win_y, content_win_x = 4, 2  # Onde a janela de conteúdo começa
    content_h, content_w = h - 6, w - 4   # Altura e largura da janela de conteúdo

    # Limpa a área de conteúdo antes de desenhar
    for y in range(content_h):
        stdscr.addstr(content_win_y + y, content_win_x, " " * content_w)

    # Aba 0: SELECIONAR ARQUIVO
    if current_tab_idx == 0:
        stdscr.addstr(content_win_y, content_win_x, "./")
        if not med_files:
            stdscr.addstr(content_win_y + 2, content_win_x, "Nenhum arquivo .med encontrado no diretório.")
            return
        for i, filename in enumerate(med_files):
            if i >= content_h - 1: break # Limita o número de arquivos exibidos
            
            symbol = "o " if i == current_file_idx else "  "
            line_str = f"{symbol}{filename}"
            
            if i == current_file_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(content_win_y + 1 + i, content_win_x, line_str)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(content_win_y + 1 + i, content_win_x, line_str)

    # Aba 1 e 2: Mostrar resultados
    else:
        if not selected_file:
            stdscr.addstr(content_win_y, content_win_x, "Nenhum arquivo selecionado. Volte e pressione Enter em um arquivo.")
            return

        # Aba 1: CONDUTA EXTRACTOR
        if current_tab_idx == 1:
            if not extractor_output:
                stdscr.addstr(content_win_y, content_win_x, "Nenhuma conduta encontrada neste arquivo.")
                return
            for i, line in enumerate(extractor_output):
                if i >= content_h: break
                stdscr.addstr(content_win_y + i, content_win_x, line)

        # Aba 2: CONDUTA TRANSLATOR
        elif current_tab_idx == 2:
            if not translator_output:
                stdscr.addstr(content_win_y, content_win_x, "Nenhuma conduta para traduzir neste arquivo.")
                return
            # Formata o JSON para exibição bonita
            pretty_json = json.dumps(translator_output, indent=2, ensure_ascii=False)
            json_lines = pretty_json.split('\n')
            
            # Envolve linhas longas que possam quebrar a UI
            wrapped_lines = []
            for line in json_lines:
                wrapped_lines.extend(textwrap.wrap(line, width=content_w))

            for i, line in enumerate(wrapped_lines):
                if i >= content_h: break
                stdscr.addstr(content_win_y + i, content_win_x, line)

def main(stdscr):
    # Configurações iniciais do curses
    curses.curs_set(0) # Esconde o cursor
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # Par de cores para destaque

    # Estado da aplicação
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

        # --- Desenhar UI ---
        # Título
        title = f" CONDUTA EXPLORER - {selected_file if selected_file else 'Nenhum arquivo selecionado'} "
        stdscr.addstr(0, (w - len(title)) // 2, title)

        # Abas
        draw_menu(stdscr, tabs, current_tab_idx)
        
        # Linha divisória
        stdscr.hline(2, 0, '-', w)
        stdscr.hline(h - 2, 0, '-', w)

        # Conteúdo principal
        draw_content(stdscr, current_tab_idx, med_files, current_file_idx, selected_file, extractor_output, translator_output)
        
        # Rodapé com instruções
        instructions = "Setas para navegar | Enter para selecionar | Q para sair"
        stdscr.addstr(h - 1, (w - len(instructions)) // 2, instructions)

        stdscr.refresh()

        # --- Capturar Input ---
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        # Navegação entre abas
        elif key == curses.KEY_RIGHT:
            current_tab_idx = (current_tab_idx + 1) % len(tabs)
        elif key == curses.KEY_LEFT:
            current_tab_idx = (current_tab_idx - 1 + len(tabs)) % len(tabs)

        # Navegação na lista de arquivos (apenas na primeira aba)
        if current_tab_idx == 0 and med_files:
            if key == curses.KEY_DOWN:
                current_file_idx = (current_file_idx + 1) % len(med_files)
            elif key == curses.KEY_UP:
                current_file_idx = (current_file_idx - 1 + len(med_files)) % len(med_files)
            elif key == curses.KEY_ENTER or key == 10:
                selected_file = med_files[current_file_idx]
                # Processa os dados do arquivo selecionado
                extractor_output = conduta_extractor(selected_file)
                translator_output = translate_conduta(extractor_output)
                # Muda para a próxima aba para conveniência
                current_tab_idx = 1


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        # Se ocorrer um erro, imprime para que o usuário possa ver
        print("Ocorreu um erro ao executar a aplicação:")
        print(e)
