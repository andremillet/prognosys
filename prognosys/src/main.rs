use std::env;
use std::fs;
use std::io::{self, BufRead};

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("Uso: prognosys <comando> [opções]");
        return;
    }

    let command = &args[1];

    match command.as_str() {
        "novo" => {
            if args.len() < 3 {
                println!("Uso: prognosys novo <opção>");
                return;
            }
            let option = &args[2];
            match option.as_str() {
                "paciente" => criar_paciente(),
                "atendimento" => println!("ok"),
                _ => println!("Opção inválida: {}", option),
            }
        }
        _ => println!("Comando inválido: {}", command),
    }
}

fn criar_paciente() {
    let stdin = io::stdin();
    let mut name = String::new();
    let mut cpf = String::new();

    println!("Nome completo:");
    stdin.read_line(&mut name).unwrap();
    name = name.trim().to_string();

    println!("CPF (11 dígitos):");
    stdin.read_line(&mut cpf).unwrap();
    cpf = cpf.trim().to_string();

    // Validação básica do CPF
    if cpf.len() != 11 || !cpf.chars().all(|c| c.is_numeric()) {
        println!("CPF inválido. Deve ter 11 dígitos numéricos.");
        return;
    }

    println!("Nome: {}, CPF: {}. Confirmar? (s/n)", name, cpf);
    let mut confirm = String::new();
    stdin.read_line(&mut confirm).unwrap();
    confirm = confirm.trim().to_lowercase();

    if confirm == "s" || confirm == "sim" {
        let dir_path = format!("pacientes/{}", cpf);
        if fs::metadata(&dir_path).is_ok() {
            println!("Paciente com CPF {} já existe.", cpf);
            return;
        }

        if let Err(e) = fs::create_dir_all(&dir_path) {
            println!("Erro ao criar diretório: {}", e);
            return;
        }

        let info_path = format!("{}/info.txt", dir_path);
        let info_content = format!("Nome: {}\nCPF: {}", name, cpf);
        if let Err(e) = fs::write(&info_path, info_content) {
            println!("Erro ao salvar informações: {}", e);
            return;
        }

        println!("Paciente criado com sucesso!");
    } else {
        println!("Operação cancelada.");
    }
}
