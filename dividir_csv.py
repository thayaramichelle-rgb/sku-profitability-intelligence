
from pathlib import Path
import csv

origem = Path("data/historico_skus.csv")
pasta = origem.parent
limite_bytes = 10 * 1024 * 1024  # aproximadamente 10 MB por parte

if not origem.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {origem.resolve()}")

parte = 1
linhas_parte = 0
total_linhas = 0
arquivo_saida = None
escritor = None

try:
    with origem.open("r", encoding="utf-8-sig", newline="") as entrada:
        leitor = csv.reader(entrada)
        cabecalho = next(leitor)

        for linha in leitor:
            if escritor is None or (
                arquivo_saida.tell() >= limite_bytes and linhas_parte > 0
            ):
                if arquivo_saida is not None:
                    arquivo_saida.close()

                destino = pasta / f"historico_skus_{parte}.csv"
                arquivo_saida = destino.open(
                    "w", encoding="utf-8", newline=""
                )
                escritor = csv.writer(arquivo_saida)
                escritor.writerow(cabecalho)

                print(f"Criando {destino.name}...")
                parte += 1
                linhas_parte = 0

            escritor.writerow(linha)
            linhas_parte += 1
            total_linhas += 1

finally:
    if arquivo_saida is not None and not arquivo_saida.closed:
        arquivo_saida.close()

print(f"\nConcluído! Total de registros: {total_linhas}")
print(f"Total de partes criadas: {parte - 1}")
