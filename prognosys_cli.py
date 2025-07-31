
import sys
import os
import datetime
import json
import uuid
import shutil
import subprocess

# Configura a saída padrão para UTF-8 para evitar problemas de codificação
sys.stdout.reconfigure(encoding='utf-8')

# --- Funções de Autenticação e Gerenciamento de Sessão ---
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".prognosys", "session.token")
USERS_FILE = os.path.join(os.path.expanduser("~"), ".prognosys", "users.json")

def _verificar_sessao_interna():
    if not os.path.exists(SESSION_FILE):
        return False, None

    session_info = {}
    with open(SESSION_FILE, 'r') as f:
        try:
            session_info = json.load(f)
        except json.JSONDecodeError:
            return False, None # Arquivo corrompido

    if not all(k in session_info and session_info[k] for k in ['username', 'token', 'expiration']):
        return False, None

    expiration_str = session_info['expiration']
    try:
        expiration_time = datetime.datetime.fromisoformat(expiration_str)
    except ValueError:
        return False, None # Formato de data inválido

    if datetime.datetime.now() < expiration_time:
        return True, session_info['username']
    else:
        os.remove(SESSION_FILE) # Remover sessão expirada
        return False, None

def _autenticar_usuario_interna(username, password):
    try:
        import bcrypt
    except ImportError:
        print("Erro: A biblioteca 'bcrypt' não está instalada. Execute 'pip install bcrypt'.")
        return False

    if not os.path.exists(USERS_FILE):
        print("Erro: Nenhum usuário cadastrado. Por favor, adicione um usuário primeiro.")
        return False

    users_data = {}
    with open(USERS_FILE, 'r') as f:
        try:
            users_data = json.load(f)
        except json.JSONDecodeError:
            print("Erro: Arquivo de usuários corrompido.")
            return False

    if username not in users_data:
        print("Erro: Nome de usuário ou senha inválidos.")
        return False

    stored_hash = users_data[username]['password_hash'].encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        session_token = str(uuid.uuid4())
        expiration_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
        
        session_info = {
            'username': username,
            'token': session_token,
            'expiration': expiration_time
        }
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_info, f, indent=4)
        
        print(f"Login bem-sucedido para '{username}'.")
        return True
    else:
        print("Erro: Nome de usuário ou senha inválidos.")
        return False

def _adicionar_usuario_interna(username, password):
    try:
        import bcrypt
    except ImportError:
        print("Erro: A biblioteca 'bcrypt' não está instalada. Execute 'pip install bcrypt'.")
        return False

    users_data = {}
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                users_data = json.load(f)
            except json.JSONDecodeError:
                users_data = {}

    if username in users_data:
        print(f"Erro: O usuário '{username}' já existe.")
        return False

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_data[username] = {'password_hash': hashed_password}

    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)
    
    print(f"Usuário '{username}' adicionado com sucesso.")
    return True

def _sair_interna():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("Sessão encerrada com sucesso.")
    else:
        print("Nenhuma sessão ativa para encerrar.")

# --- Funções de Operação de Registros ---
PATIENTS_ROOT = "C:\\MedicalRecords\\Patients"

# Helper function to get patient directory path
def _get_patient_dir(nome_paciente, cpf):
    patient_folder_name = f"{nome_paciente}_{cpf}"
    return os.path.join(PATIENTS_ROOT, patient_folder_name)

def _adicionar_registro_interna(nome_paciente, cpf, caminho_arquivo_med_origem, medico_logado):
    patient_dir = _get_patient_dir(nome_paciente, cpf)
    
    if not os.path.isdir(patient_dir):
        print(f"Erro: Paciente '{nome_paciente}' com CPF '{cpf}' não encontrado. Por favor, crie o paciente primeiro.")
        return False

    if not os.path.exists(caminho_arquivo_med_origem):
        print(f"Erro: Arquivo .med de origem não encontrado em '{caminho_arquivo_med_origem}'.")
        return False

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    nome_base_arquivo = os.path.splitext(os.path.basename(caminho_arquivo_med_origem))[0]
    novo_nome_arquivo = f"{nome_base_arquivo}_{timestamp}.med"
    caminho_destino_med = os.path.join(patient_dir, novo_nome_arquivo)

    try:
        shutil.copy(caminho_arquivo_med_origem, caminho_destino_med)
        print(f"Arquivo '{novo_nome_arquivo}' copiado para o diretório do paciente.")
    except Exception as e:
        print(f"Erro ao copiar arquivo: {e}")
        return False

    current_dir = os.getcwd()
    try:
        os.chdir(patient_dir)
        
        subprocess.run(["git", "add", novo_nome_arquivo], check=True, capture_output=True, text=True)
        
        commit_message = f"Registro adicionado por {medico_logado}: {novo_nome_arquivo}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
        
        print(f"Registro para '{nome_paciente}' com CPF '{cpf}' adicionado e comitado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro na operação Git: {e.stderr}")
        return False
    except Exception as e:
        print(f"Erro na operação Git: {e}")
        return False
    finally:
        os.chdir(current_dir)

def _listar_historico_interna(nome_paciente, cpf):
    patient_dir = _get_patient_dir(nome_paciente, cpf)
    if not os.path.isdir(patient_dir):
        print(f"Erro: Paciente '{nome_paciente}' com CPF '{cpf}' não encontrado.")
        return False

    current_dir = os.getcwd()
    try:
        os.chdir(patient_dir)
        print(f"Histórico de registros para {nome_paciente} (CPF: {cpf}):")
        result = subprocess.run(["git", "log", "--pretty=format:%h | %s", "--name-status"], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar histórico: {e.stderr}")
        return False
    except Exception as e:
        print(f"Erro ao listar histórico: {e}")
        return False
    finally:
        os.chdir(current_dir)

def _ver_registro_interna(nome_paciente, cpf, nome_arquivo_med=None):
    patient_dir = _get_patient_dir(nome_paciente, cpf)

    if not os.path.isdir(patient_dir):
        print(f"Erro: Paciente '{nome_paciente}' com CPF '{cpf}' não encontrado.")
        return False

    current_dir = os.getcwd()
    try:
        os.chdir(patient_dir)

        if nome_arquivo_med:
            caminho_completo_arquivo = os.path.join(patient_dir, nome_arquivo_med)
            if not os.path.exists(caminho_completo_arquivo):
                print(f"Erro: Arquivo '{nome_arquivo_med}' não encontrado para o paciente '{nome_paciente}' (CPF: {cpf}).")
                print(f"Use 'listar-historico {nome_paciente} {cpf}' para ver os nomes dos arquivos disponíveis.")
                return False
            
            print(f"Visualizando o registro '{nome_arquivo_med}' para {nome_paciente} (CPF: {cpf}):")
            try:
                result = subprocess.run(["type", nome_arquivo_med], check=True, capture_output=True, text=True, shell=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Erro ao exibir o arquivo: {e.stderr}")
            
        else:
            print(f"Para visualizar um registro específico, use: ver-registro <nome-paciente> <cpf> <nome-arquivo-med>")
            print(f"Use 'listar-historico {nome_paciente} {cpf}' para ver os nomes dos arquivos disponíveis.")
            
            med_files = [f for f in os.listdir('.') if f.endswith('.med')]
            if med_files:
                latest_med_file = max(med_files, key=os.path.getctime)
                print("") # Linha em branco separada
                print(f"Exibindo o registro mais recente em disco para '{nome_paciente}' (CPF: {cpf}): {latest_med_file}")
                try:
                    result = subprocess.run(["type", latest_med_file], check=True, capture_output=True, text=True, shell=True)
                    print(result.stdout)
                except subprocess.CalledProcessError as e:
                    print(f"Erro ao exibir o arquivo: {e.stderr}")
            else:
                print("Nenhum arquivo .med encontrado para este paciente.")
            return False

        return True
    except Exception as e:
        print(f"Erro ao visualizar registro: {e}")
        return False
    finally:
        os.chdir(current_dir)

def _criar_paciente_interna(nome_paciente, cpf):
    patient_dir = _get_patient_dir(nome_paciente, cpf)

    if os.path.isdir(patient_dir):
        print(f"Erro: O paciente '{nome_paciente}' com CPF '{cpf}' já existe.")
        return False

    try:
        os.makedirs(patient_dir)
        print(f"Diretório para o paciente '{nome_paciente}' (CPF: {cpf}) criado em '{patient_dir}'.")
        
        current_dir = os.getcwd()
        os.chdir(patient_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)

        # Usando aspas triplas para strings de múltiplas linhas
        gitignore_content = """
*.tmp
*.log
*/
!*.med
"""
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        
        subprocess.run(["git", "add", ".gitignore"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Primeiro commit: Inicializa repositório do paciente e adiciona .gitignore."], check=True, capture_output=True, text=True)

        print(f"Repositório Git para '{nome_paciente}' (CPF: {cpf}) inicializado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro na operação Git: {e.stderr}")
        return False
    except Exception as e:
        print(f"Erro ao criar paciente: {e}")
        return False
    finally:
        os.chdir(current_dir)

def _listar_pacientes_interna():
    print("Listando todos os pacientes cadastrados:")
    found_patients = []
    if not os.path.exists(PATIENTS_ROOT) or not os.path.isdir(PATIENTS_ROOT):
        print("Nenhum diretório de pacientes encontrado.")
        return

    for item in os.listdir(PATIENTS_ROOT):
        item_path = os.path.join(PATIENTS_ROOT, item)
        if os.path.isdir(item_path):
            # Assumimos o formato Nome_CPF
            parts = item.rsplit('_', 1) # Divide no último underscore
            if len(parts) == 2:
                nome = parts[0]
                cpf = parts[1]
                found_patients.append({'Nome': nome, 'CPF': cpf, 'Pasta': item})
            else:
                # Lidar com pastas que não seguem o padrão (ex: pacientes antigos)
                found_patients.append({'Nome': item, 'CPF': 'N/A', 'Pasta': item})
    
    if not found_patients:
        print("Nenhum paciente encontrado.")
        return

    # Ordenar pacientes pelo nome
    found_patients.sort(key=lambda p: p['Nome'].lower())

    # Exibir em formato de tabela simples para TTY
    print("-------------------------------------------------------------------")
    print(f"{'Nome do Paciente':<35} | {'CPF':<15}")
    print("-------------------------------------------------------------------")
    for patient in found_patients:
        print(f"{patient['Nome']:<35} | {patient['CPF']:<15}")
    print("-------------------------------------------------------------------")

def _ver_medicacoes_interna(nome_paciente, cpf, medico_logado):
    patient_dir = _get_patient_dir(nome_paciente, cpf)
    if not os.path.isdir(patient_dir):
        print(f"Erro: Paciente '{nome_paciente}' com CPF '{cpf}' não encontrado.")
        return False

    current_dir = os.getcwd()
    try:
        os.chdir(patient_dir)
        
        med_files = [f for f in os.listdir('.') if f.endswith('.med')]
        if not med_files:
            print(f"Nenhum registro .med encontrado para o paciente '{nome_paciente}' (CPF: {cpf}).")
            return False

        latest_med_file = max(med_files, key=os.path.getctime)
        print(f"Analisando o registro mais recente para {nome_paciente} (CPF: {cpf}): {latest_med_file}")
        
        raw_medicacoes = ""
        in_anamnese_section = False
        
        with open(latest_med_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line == '[ANAMNESE]':
                    in_anamnese_section = True
                    continue
                if in_anamnese_section and line.startswith('[') and line.endswith(']'):
                    break 
                    
                if in_anamnese_section and line.startswith('!MED'):
                    raw_medicacoes = line[len('!MED'):].strip()
                    break # Encontrou e pode parar
        
        print("-------------------------------------------------------------------")
        print(f"Medicações em Uso para {nome_paciente} (CPF: {cpf}) - (Dr(a). {medico_logado}):")
        print("-------------------------------------------------------------------")
        
        if raw_medicacoes:
            # Dividir por ponto e vírgula e limpar cada item
            medicacoes_formatadas = [med.strip() for med in raw_medicacoes.split(';') if med.strip()]
            for i, med in enumerate(medicacoes_formatadas):
                print(f"  {i+1}. {med}")
        else:
            print("Nenhuma medicação em uso (!MED) encontrada na anamnese do registro mais recente.")
        print("-------------------------------------------------------------------")

        return True
    except Exception as e:
        print(f"Erro ao visualizar medicações: {e}")
        return False
    finally:
        os.chdir(current_dir)

# --- Lógica principal da CLI ---

def main():
    if len(sys.argv) < 2:
        print("Uso: python prognosys_cli.py <comando> [argumentos]")
        print("Comandos disponíveis:")
        print("  adicionar-usuario <username> <password>")
        print("  entrar <username> <password>")
        print("  sair")
        print("  adicionar-registro <nome-paciente> <cpf> <caminho-arquivo-med>")
        print("  listar-historico <nome-paciente> <cpf>")
        print("  ver-registro <nome-paciente> <cpf> [nome-arquivo-med]")
        print("  criar-paciente <nome-paciente> <cpf>")
        print("  listar-pacientes")
        print("  ver-medicacoes <nome-paciente> <cpf>") # Novo comando
        return

    comando = sys.argv[1]
    
    # Comandos de autenticação que não exigem login prévio
    if comando == "adicionar-usuario":
        if len(sys.argv) == 4:
            _adicionar_usuario_interna(sys.argv[2], sys.argv[3])
        else:
            print("Uso: adicionar-usuario <username> <password>")
    elif comando == "entrar":
        if len(sys.argv) == 4:
            _autenticar_usuario_interna(sys.argv[2], sys.argv[3])
        else:
            print("Uso: entrar <username> <password>")
    elif comando == "sair":
        _sair_interna()
    # Comandos que exigem autenticação
    elif comando == "listar-pacientes":
        esta_logado, usuario_logado = _verificar_sessao_interna()
        if not esta_logado:
            print("Erro: Nenhuma sessão ativa. Por favor, faça login primeiro com 'prognosys entrar <username> <password>'.")
            return
        print(f"Sessão ativa para o Dr(a). {usuario_logado}.")
        _listar_pacientes_interna()
    elif comando == "ver-medicacoes": 
        if len(sys.argv) == 4:
            esta_logado, usuario_logado = _verificar_sessao_interna()
            if not esta_logado:
                print("Erro: Nenhuma sessão ativa. Por favor, faça login primeiro com 'prognosys entrar <username> <password>'.")
                return
            print(f"Sessão ativa para o Dr(a). {usuario_logado}.")
            _ver_medicacoes_interna(sys.argv[2], sys.argv[3], usuario_logado)
        else:
            print("Uso: ver-medicacoes <nome-paciente> <cpf>")

    else:
        esta_logado, usuario_logado = _verificar_sessao_interna()
        if not esta_logado:
            print("Erro: Nenhuma sessão ativa. Por favor, faça login primeiro com 'prognosys entrar <username> <password>'.")
            return
        
        print(f"Sessão ativa para o Dr(a). {usuario_logado}.")

        if comando == "adicionar-registro":
            if len(sys.argv) == 5:
                _adicionar_registro_interna(sys.argv[2], sys.argv[3], sys.argv[4], usuario_logado)
            else:
                print("Uso: adicionar-registro <nome-paciente> <cpf> <caminho-arquivo-med>")
        elif comando == "listar-historico":
            if len(sys.argv) == 4:
                _listar_historico_interna(sys.argv[2], sys.argv[3])
            else:
                print("Uso: listar-historico <nome-paciente> <cpf>")
        elif comando == "ver-registro":
            if len(sys.argv) >= 4:
                nome_paciente = sys.argv[2]
                cpf = sys.argv[3]
                nome_arquivo_med = sys.argv[4] if len(sys.argv) == 5 else None
                _ver_registro_interna(nome_paciente, cpf, nome_arquivo_med)
            else:
                print("Uso: ver-registro <nome-paciente> <cpf> [nome-arquivo-med]")
        elif comando == "criar-paciente":
            if len(sys.argv) == 4:
                _criar_paciente_interna(sys.argv[2], sys.argv[3])
            else:
                print("Uso: criar-paciente <nome-paciente> <cpf>")
        else:
            print(f"Comando desconhecido: {comando}")

if __name__ == '__main__':
    main()
