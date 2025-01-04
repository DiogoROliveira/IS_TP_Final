import csv
import random
import argparse
def select_random_lines(input_file, output_file, num_lines):
    """
    Seleciona um número específico de linhas aleatórias de um arquivo CSV.
    
    Parâmetros:
    input_file (str): Caminho do arquivo CSV de entrada
    output_file (str): Caminho do arquivo CSV de saída
    num_lines (int): Número de linhas a serem selecionadas
    """
    # Lê todas as linhas do arquivo CSV
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        # Salva o cabeçalho
        header = next(reader, None)
        
        # Lê todas as linhas restantes
        rows = list(reader)
    
    # Verifica se há linhas suficientes
    if num_lines > len(rows):
        print(f"Aviso: Número de linhas solicitadas ({num_lines}) "
              f"maior que o total de linhas ({len(rows)}). "
              f"Serão selecionadas todas as linhas.")
        num_lines = len(rows)
    
    # Seleciona linhas aleatórias
    selected_rows = random.sample(rows, num_lines)
    
    # Escreve as linhas selecionadas em um novo arquivo CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escreve o cabeçalho
        if header:
            writer.writerow(header)
        
        # Escreve as linhas selecionadas
        writer.writerows(selected_rows)
    
    print(f"Arquivo {output_file} criado com {num_lines} linhas aleatórias.")
def main():
    # Configuração de argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Seleciona linhas aleatórias de um arquivo CSV')
    parser.add_argument('input', help='Arquivo CSV de entrada')
    parser.add_argument('output', help='Arquivo CSV de saída')
    parser.add_argument('num_lines', type=int, help='Número de linhas a selecionar')
    
    args = parser.parse_args()
    
    # Chama a função principal
    select_random_lines(args.input, args.output, args.num_lines)
if __name__ == '__main__':
    main()