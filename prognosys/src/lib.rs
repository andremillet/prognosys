use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufRead};

const GREEN: &str = "\x1b[32m";
const BLUE: &str = "\x1b[34m";
const YELLOW: &str = "\x1b[33m";
const RED: &str = "\x1b[31m";
const RESET: &str = "\x1b[0m";

fn clean_line(line: &str) -> String {
    let mut result = String::new();
    let mut in_bracket = false;
    for c in line.chars() {
        if c == '[' {
            in_bracket = true;
        } else if c == ']' {
            in_bracket = false;
        } else if !in_bracket {
            result.push(c);
        }
    }
    result
}

pub fn identifica_secoes(caminho: &str) -> Result<HashMap<String, String>, io::Error> {
    let file = File::open(caminho)?;
    let reader = io::BufReader::new(file);
    let mut sections: HashMap<String, String> = HashMap::new();
    let mut current_section: Option<String> = None;
    let mut current_content = String::new();
    for line in reader.lines() {
        let line = line?;
        let linha_limpa = line.trim();
        if linha_limpa.starts_with('[') && linha_limpa.ends_with(']') {
            let nome_da_secao = &linha_limpa[1..linha_limpa.len() - 1];
            if !nome_da_secao.is_empty() && nome_da_secao.chars().filter(|c| c.is_alphabetic()).all(|c| c.is_uppercase()) {
                if let Some(prev_section) = current_section.take() {
                    sections.insert(prev_section, current_content.trim().to_string());
                }
                current_section = Some(nome_da_secao.to_string());
                current_content.clear();
            } else {
                if current_section.is_some() {
                    current_content.push_str(&clean_line(&line));
                    current_content.push('\n');
                }
            }
        } else {
            if current_section.is_some() {
                current_content.push_str(&clean_line(&line));
                current_content.push('\n');
            }
        }
    }
    if let Some(last_section) = current_section {
        sections.insert(last_section, current_content.trim().to_string());
    }
    Ok(sections)
}

fn imprimir_barra_progresso(progresso: usize, total: usize) {
    let largura = 40;
    let preenchido = (progresso * largura) / total;
    let mut barra = String::from("|");
    for _ in 0..preenchido {
        barra.push('=');
    }
    for _ in preenchido..largura {
        barra.push('-');
    }
    barra.push('|');
    println!("{}", barra);
}

pub fn conduta_handler(arquivo: &str) -> Result<Vec<String>, io::Error> {
    let sections = identifica_secoes(arquivo)?;
    let conduta_content = sections.get("CONDUTA").ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "Seção CONDUTA não encontrada"))?;
    let linhas: Vec<&str> = conduta_content.lines().collect();
    let mut output = Vec::new();
    for (i, linha) in linhas.iter().enumerate() {
        if linha.trim().ends_with(';') {
            let mut linha_modificada = linha.trim().to_string();
            if linha_modificada.starts_with('+') {
                linha_modificada = linha_modificada.replacen('+', "ADICIONAR ", 1);
            } else if linha_modificada.starts_with("++") {
                linha_modificada = linha_modificada.replacen("++", "INCREMENTAR DOSE DE ", 1);
            } else if linha_modificada.starts_with("--") {
                linha_modificada = linha_modificada.replacen("--", "DECREMENTAR DOSE DE ", 1);
            } else if linha_modificada.starts_with("-") {
                linha_modificada = linha_modificada.replacen("-", "INTERROMPER ", 1);
            } else if linha_modificada.starts_with("!ENCAMINHO") {
                linha_modificada = linha_modificada.replacen("!ENCAMINHO", "ENCAMINHAMENTO PARA ", 1);
            }
            let formatted_line = if linha_modificada.starts_with("ADICIONAR ") {
                format!("{}. ADICIONAR {}", i + 1, linha_modificada.strip_prefix("ADICIONAR ").unwrap())
            } else if linha_modificada.starts_with("INCREMENTAR DOSE DE ") {
                format!("{}. INCREMENTAR DOSE DE {}", i + 1, linha_modificada.strip_prefix("INCREMENTAR DOSE DE ").unwrap())
            } else if linha_modificada.starts_with("INTERROMPER ") {
                format!("{}. INTERROMPER {}", i + 1, linha_modificada.strip_prefix("INTERROMPER ").unwrap())
            } else if linha_modificada.starts_with("DECREMENTAR DOSE DE ") {
                format!("{}. DECREMENTAR DOSE DE {}", i + 1, linha_modificada.strip_prefix("DECREMENTAR DOSE DE ").unwrap())
            } else if linha_modificada.starts_with("ENCAMINHAMENTO PARA ") {
                format!("{}. ENCAMINHAMENTO PARA {}", i + 1, linha_modificada.strip_prefix("ENCAMINHAMENTO PARA ").unwrap())
            } else {
                format!("{}. {}", i + 1, linha_modificada)
            };
            output.push(formatted_line);
        }
    }
    Ok(output)
}