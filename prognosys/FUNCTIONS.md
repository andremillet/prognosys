# Prognosys Functions and Keywords Documentation

## Functions

### `identifica_secoes(caminho: &str) -> Result<HashMap<String, String>, io::Error>`
- **Purpose**: Parses a file and identifies sections enclosed in square brackets.
- **Parameters**:
  - `caminho`: Path to the file to parse.
- **Returns**: A HashMap where keys are section names (uppercase alphabetic) and values are the content of each section.
- **Behavior**: Sections are identified by lines starting and ending with `[` and `]`. Content between sections is cleaned by removing text within brackets.

### `conduta_handler(arquivo: &str) -> Result<Vec<String>, io::Error>`
- **Purpose**: Processes the "CONDUTA" section of a file and formats medication-related commands.
- **Parameters**:
  - `arquivo`: Path to the file containing the CONDUTA section.
- **Returns**: A vector of formatted strings representing processed conduta lines.
- **Behavior**: Parses lines ending with `;` and transforms prefixes into readable commands.

### `criar_paciente()`
- **Purpose**: Creates a new patient by prompting for name and CPF, then creates a directory for the patient.
- **Parameters**: None.
- **Behavior**: Asks for user input, validates CPF, confirms creation, creates `pacientes/{cpf}/` directory and saves `info.txt`.

## Keywords and Prefixes

### CLI Commands
- `novo`: Command to create new entities.
  - `paciente`: Create a new patient (prompts for name and CPF, creates patient directory).
  - `atendimento`: Create a new appointment.

### Medication Commands
- `+`: Prefix for "ADICIONAR" (Add)
- `++`: Prefix for "INCREMENTAR DOSE DE" (Increase dose of)
- `--`: Prefix for "DECREMENTAR DOSE DE" (Decrease dose of)
- `-`: Prefix for "INTERROMPER" (Interrupt/Stop)
- `!ENCAMINHO`: Prefix for "ENCAMINHAMENTO PARA" (Referral to)

### Section Identifiers
- `[SECTION_NAME]`: Marks the start of a section where SECTION_NAME is uppercase alphabetic.

## Usage Examples

### Using `identifica_secoes`
```rust
let sections = identifica_secoes("patient.med")?;
for (name, content) in sections {
    println!("Section: {}", name);
    println!("Content: {}", content);
}
```

### Using `conduta_handler`
```rust
let condutas = conduta_handler("patient.med")?;
for conduta in condutas {
    println!("{}", conduta);
}
```

## File Format
- Files are expected to have sections in the format `[SECTION_NAME]` followed by content.
- The CONDUTA section contains lines ending with `;` that represent medical instructions.