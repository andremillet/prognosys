# MedFiles

MedFiles é um processador de arquivos médicos (.med) escrito em Rust. Ele permite gerenciar registros de atendimentos médicos de forma segura e organizada.

## Funcionalidades

- **Configuração de Usuário**: Configure sua conta com nome, CPF, telefone e email. Verificação por token via email.
- **Interface CLI**: Comando simples para interagir com o sistema.
- **Processamento de Arquivos .med**: Estrutura os dados médicos em seções para fácil acesso.

## Instalação

1. Certifique-se de ter o Rust instalado: [rustup.rs](https://rustup.rs/)
2. Clone o repositório e entre no diretório:
   ```bash
   git clone <url-do-repo>
   cd medfiles
   ```
3. Compile o projeto:
   ```bash
   cargo build --release
   ```

## Uso

### Configuração Inicial
Execute o comando de configuração para registrar um novo usuário:
```bash
./target/release/medfiles config
```
Siga as instruções para inserir seus dados e confirmar via email.

### Uso Geral
Execute o programa sem argumentos para acessar o menu principal:
```bash
./target/release/medfiles
```
Será solicitado o que deseja fazer (ver atendimentos, ver prescrições - recursos em desenvolvimento).

### Comandos Disponíveis
- `medfiles config`: Configura ou verifica a conta do usuário.
- `medfiles`: Menu principal (requer usuário configurado).

## Estrutura dos Arquivos .med

Os arquivos .med são divididos em seções marcadas por `[NOME DA SEÇÃO]`, como:
- [ANAMNESE]
- [EXAME FISICO]
- [HIPOTESE DIAGNOSTICA]
- [CONDUTA]

## Desenvolvimento

Para contribuir:
1. Faça um fork do projeto.
2. Crie uma branch para sua feature: `git checkout -b minha-feature`
3. Commit suas mudanças: `git commit -am 'Adiciona nova feature'`
4. Push para a branch: `git push origin minha-feature`
5. Abra um Pull Request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato

Para dúvidas ou sugestões, abra uma issue no repositório.