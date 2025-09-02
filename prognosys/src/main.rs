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
        "listar" => {
            if args.len() < 3 {
                println!("Uso: prognosys listar <opção>");
                return;
            }
            let option = &args[2];
            match option.as_str() {
                "pacientes" => listar_pacientes(),
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

fn listar_pacientes() {
    let pacientes_dir = "pacientes";
    if let Ok(entries) = fs::read_dir(pacientes_dir) {
        println!("{:<30} {:<15} {:<12}", "Nome", "CPF", "Último Atendimento");
        println!("{}", "-".repeat(60));
        for entry in entries {
            if let Ok(entry) = entry {
                if let Ok(metadata) = entry.metadata() {
                    if metadata.is_dir() {
                        let cpf = entry.file_name().to_string_lossy().to_string();
                        let info_path = format!("{}/{}/info.txt", pacientes_dir, cpf);
                        if let Ok(content) = fs::read_to_string(&info_path) {
                            let mut name = String::new();
                            for line in content.lines() {
                                if line.starts_with("Nome: ") {
                                    name = line.strip_prefix("Nome: ").unwrap_or("").to_string();
                                }
                            }
                            let last_date = get_last_med_date(&format!("{}/{}", pacientes_dir, cpf));
                            println!("{:<30} {:<15} {:<12}", name, cpf, last_date);
                        }
                    }
                }
            }
        }
    } else {
        println!("Diretório pacientes não encontrado.");
    }
}

fn get_last_med_date(dir_path: &str) -> String {
    if let Ok(entries) = fs::read_dir(dir_path) {
        let mut latest_time = std::time::SystemTime::UNIX_EPOCH;
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if let Some(ext) = path.extension() {
                    if ext == "med" {
                        if let Ok(metadata) = entry.metadata() {
                            if let Ok(modified) = metadata.modified() {
                                if modified > latest_time {
                                    latest_time = modified;
                                }
                            }
                        }
                    }
                }
            }
        }
        if latest_time != std::time::SystemTime::UNIX_EPOCH {
            if let Ok(duration) = latest_time.duration_since(std::time::UNIX_EPOCH) {
                let secs = duration.as_secs();
                let days = secs / 86400;
                let year = 1970 + days / 365;
                let day_of_year = days % 365;
                let month = (day_of_year * 12 / 365) + 1;
                let day = day_of_year - ((month - 1) * 365 / 12);
                format!("{:04}-{:02}-{:02}", year, month, day)
            } else {
                "".to_string()
            }
        } else {
            "".to_string()
        }
    } else {
        "".to_string()
    }
}
