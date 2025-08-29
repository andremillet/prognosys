import argparse
import sys

def extract_conduta(file_path):
    """
    Extracts the [CONDUTA] section from a .med file.

    Args:
        file_path (str): The path to the .med file.

    Returns:
        list: A list of strings from the [CONDUTA] section.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    conduta_section = []
    in_conduta_section = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == '[CONDUTA]':
            in_conduta_section = True
            continue
        
        if in_conduta_section:
            if stripped_line.startswith('['):
                # Stop if we reach another section
                break
            if stripped_line:
                conduta_section.append(stripped_line)

    return conduta_section

def main():
    parser = argparse.ArgumentParser(
        description="Extracts the [CONDUTA] section from a .med file."
    )
    parser.add_argument(
        "file",
        metavar="nome-do-arquivo.med",
        help="The path to the .med file."
    )
    args = parser.parse_args()

    conduta = extract_conduta(args.file)
    
    for item in conduta:
        print(item)

if __name__ == "__main__":
    main()