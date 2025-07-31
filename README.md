# Prognosys: Sistema de Gerenciamento de Registros Médicos Versionados

## Visão Geral

O **Prognosys** é um sistema de linha de comando (CLI) projetado para gerenciar e versionar registros médicos de pacientes, utilizando a poderosa capacidade de controle de versão do Git. Inspirado na ideia de que cada atualização ou adição de um registro médico é como um "commit" em um repositório, o Prognosys garante um histórico completo, rastreável e auditável da evolução clínica de cada paciente.

Este projeto visa fornecer uma ferramenta robusta e flexível para profissionais de saúde que necessitam de um controle rigoroso sobre os dados dos pacientes, com foco na simplicidade da interface via terminal (TTY) e na segurança da autenticação.

## Objetivo do Projeto

Transformar a ideia de documentos `.med` (um formato simplificado para anotações médicas) em um sistema de "repositório" por paciente, onde cada interação com o registro (nova consulta, atualização de exames, etc.) gera um novo "commit" no histórico do paciente. Isso permite:

*   **Rastreabilidade:** Saber quem fez o quê, quando e por que.
*   **Integridade:** Preservar todas as versões do registro, sem sobrescrever informações.
*   **Controle de Versão:** Acessar facilmente versões anteriores de um registro.

## Funcionalidades Atuais

O Prognosys oferece as seguintes funcionalidades via linha de comando:

*   **Autenticação de Usuários:**
    *   `adicionar-usuario`: Cria novos usuários (médicos) com senhas hashadas.
    *   `entrar`: Permite que um usuário faça login e inicie uma sessão.
    *   `sair`: Encerra a sessão ativa do usuário.
    *   **Controle de Acesso:** A maioria dos comandos que manipulam registros exige que um usuário esteja logado.
*   **Gerenciamento de Pacientes:**
    *   `criar-paciente <NomeDoPaciente> <CPF>`: Cria um novo diretório para o paciente (`NomeDoPaciente_CPF`) e inicializa um repositório Git dedicado para ele. O CPF atua como chave primária para garantir a unicidade.
    *   `listar-pacientes`: Exibe uma lista tabular de todos os pacientes cadastrados no sistema, incluindo seus CPFs.
*   **Gerenciamento de Registros Médicos (`.med`):**
    *   `adicionar-registro <NomeDoPaciente> <CPF> <caminho-arquivo-med>`: Adiciona um novo registro para um paciente específico. O arquivo `.med` de origem é copiado para o repositório do paciente com um timestamp único no nome, e a mudança é comitada no Git.
    *   `listar-historico <NomeDoPaciente> <CPF>`: Exibe o histórico de commits (registros) para um paciente, mostrando o hash do commit, a mensagem e os arquivos afetados.
    *   `ver-registro <NomeDoPaciente> <CPF> [nome-arquivo-med]`: Visualiza o conteúdo de um registro específico de um paciente. Se `nome-arquivo-med` for fornecido, exibe aquele arquivo; caso contrário, instrui sobre como usar e exibe o mais recente em disco.

## Pilha Tecnológica

*   **Linguagem de Programação:** Python
*   **Sistema de Controle de Versão:** Git CLI (comandos executados via `subprocess`)
*   **Ferramentas de Sistema:** PowerShell / CMD (para operações de arquivo e diretório)
*   **Bibliotecas Python:**
    *   `bcrypt`: Para hashing seguro de senhas.
    *   `shutil`: Para operações de cópia de arquivos.
    *   `subprocess`: Para executar comandos externos (Git, `type`).
    *   `os`, `sys`, `datetime`, `json`, `uuid`: Bibliotecas padrão do Python para manipulação de sistema de arquivos, tempo, JSON e IDs únicos.

## Estrutura do Projeto

O Prognosys organiza os dados da seguinte forma:

*   **`C:\MedicalRecords\Patients\`**: Diretório raiz onde cada paciente possui uma subpasta.
    *   **`C:\MedicalRecords\Patients\<NomeDoPaciente>_<CPF>\`**: Cada subpasta é um repositório Git autônomo para um paciente.
        *   **`.git\`**: Diretório de metadados do Git para o paciente.
        *   **`<NomeDoPaciente>_<CPF>_YYYY-MM-DD_HHMMSS.med`**: Múltiplos arquivos `.med`, cada um representando um registro histórico.
        *   **`.gitignore`**: Configurado para ignorar arquivos que não são `.med`.
*   **`C:\Users\<SeuUsuario>\.prognosys\`**: Diretório de configuração do Prognosys (oculto).
    *   **`users.json`**: Armazena os hashes das senhas dos médicos.
    *   **`session.token`**: Armazena o token da sessão ativa do médico (temporário).
*   **`C:\Users\<SeuUsuario>\Prognosys\`**: Diretório do código-fonte do Prognosys.
    *   **`prognosys_cli.py`**: O script Python principal que contém toda a lógica da CLI.
    *   `README.md`: Este arquivo.

## Instalação e Configuração

Siga estes passos para configurar e começar a usar o Prognosys.

1.  **Pré-requisitos:**
    *   **Python 3:** Certifique-se de ter o Python 3 instalado no seu sistema.
    *   **Git CLI:** O Git deve estar instalado e configurado no seu PATH do sistema.
    *   **GitHub CLI (Opcional, mas recomendado):** Para gerenciar o repositório do código-fonte do Prognosys no GitHub.
        *   Instale com `winget install GitHub.cli` no PowerShell ou siga as instruções em [cli.github.com](https://cli.github.com/).
        *   Autentique-se: `gh auth login`
        *   Se precisar de permissão para deletar/recriar repositórios (como fizemos), execute `gh auth refresh -h github.com -s delete_repo`.

2.  **Clonar o Repositório do Prognosys (código-fonte):**
    ```bash
    git clone https://github.com/andremillet/prognosys.git C:\Users\andre\Prognosys
    ```
    (Se você já fez isso, pule esta etapa).

3.  **Configurar o Repositório Remoto (se não estiver configurado):**
    Navegue até o diretório do projeto e configure o remoto se o clone foi superficial ou se você criou o repositório localmente primeiro.
    ```powershell
    Set-Location C:\Users\andre\Prognosys
    git remote add origin https://github.com/andremillet/prognosys.git
    git branch -M main # Garante que a branch principal seja 'main'
    git push -u origin main
    Set-Location C:\Users\andre
    ```
    *(Este passo só é necessário se a configuração inicial do GitHub não foi feita como demonstrado antes, ou se você estiver configurando em uma nova máquina).*

4.  **Instalar Dependências Python:**
    ```bash
    pip install bcrypt
    ```

5.  **Criar o Diretório Raiz dos Pacientes:**
    ```powershell
    mkdir C:\MedicalRecords\Patients
    ```
    *(Este passo só precisa ser feito uma única vez).*

6.  **Adicionar o Primeiro Usuário (Médico):**
    Este será o seu usuário administrador inicial. Substitua `seu_username` e `sua_senha`.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py adicionar-usuario seu_username sua_senha
    ```
    *Exemplo:* `python C:\Users\andre\Prognosys\prognosys_cli.py adicionar-usuario doctor_andre senha123`

## Uso

Todos os comandos são executados via `python C:\Users\andre\Prognosys\prognosys_cli.py <comando> [argumentos]`.

### Autenticação

*   **`entrar <username> <password>`**
    Faz o login do usuário no sistema. Essencial para realizar operações que modificam registros.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py entrar doctor_andre senha123
    ```

*   **`sair`**
    Encerra a sessão ativa do usuário.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py sair
    ```

### Gerenciamento de Pacientes

*   **`criar-paciente <nome-do-paciente> <cpf>`**
    Cria um novo paciente no sistema, inicializando um repositório Git para ele.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py criar-paciente "Maria Silva" "11122233344"
    ```

*   **`listar-pacientes`**
    Exibe uma lista de todos os pacientes cadastrados, incluindo Nome e CPF.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py listar-pacientes
    ```
    *(Requer login prévio).*

### Gerenciamento de Registros Médicos

*   **`adicionar-registro <nome-do-paciente> <cpf> <caminho-arquivo-med>`**
    Adiciona um novo registro (`.med` file) para um paciente específico. O arquivo é copiado para o repositório do paciente com um timestamp no nome e comitado no Git.
    ```bash
    # Exemplo: Se você tiver um arquivo .med em C:	emp\consulta_nova.med
    python C:\Users\andre\Prognosys\prognosys_cli.py adicionar-registro "Maria Silva" "11122233344" "C:	emp\\consulta_nova.med"
    ```
    *(Requer login prévio).*

*   **`listar-historico <nome-do-paciente> <cpf>`**
    Mostra o histórico de todas as alterações (commits) para o registro de um paciente.
    ```bash
    python C:\Users\andre\Prognosys\prognosys_cli.py listar-historico "Maria Silva" "11122233344"
    ```
    *(Requer login prévio).*

*   **`ver-registro <nome-do-paciente> <cpf> [nome-arquivo-med]`**
    Exibe o conteúdo de um arquivo `.med` específico do histórico de um paciente. Se `nome-arquivo-med` não for fornecido, ele exibirá uma mensagem de uso e o conteúdo do arquivo `.med` mais recente em disco para aquele paciente (se existir).
    ```bash
    # Para ver um arquivo específico (nome completo do arquivo com timestamp)
    python C:\Users\andre\Prognosys\prognosys_cli.py ver-registro "Maria Silva" "11122233344" "FRANCISCA COELHO DE BARROS CARDOSO_2025-07-30_224149.med"

    # Para ver o mais recente e obter instruções
    python C:\Users\andre\Prognosys\prognosys_cli.py ver-registro "Maria Silva" "11122233344"
    ```
    *(Requer login prévio).*

## Próximos Passos e Melhorias Potenciais

*   **Refatorar Pacientes Antigos:** Desenvolver um comando para migrar pacientes existentes (sem CPF no nome da pasta) para o novo padrão `Nome_CPF`.
*   **Visualização por ID de Commit:** Aprimorar `ver-registro` para permitir a visualização de qualquer versão de um registro usando o ID do commit (hash) do Git.
*   **Comparação de Registros (`diff`):** Implementar uma funcionalidade para comparar duas versões de um registro médico (entre commits ou arquivos).
*   **Busca por Conteúdo:** Adicionar um comando para buscar termos específicos dentro de todos os registros `.med`.
*   **Remoção de Registros:** Desenvolver um comando seguro para remover registros (com atenção à integridade dos dados médicos).
*   **Sincronização Remota dos Repositórios de Pacientes:** Considerar a possibilidade de sincronizar os repositórios Git de pacientes com um servidor Git remoto (GitHub, GitLab, etc.) para backup e colaboração (requer considerações de segurança e privacidade rigorosas).
*   **Melhorias na Interface (TTY):** Formatação mais avançada de tabelas e saídas para melhor legibilidade.
*   **Empacotamento:** Transformar o `prognosys_cli.py` em um executável ou pacote Python instalável para facilitar o uso (`prognosys <comando>`).

---
