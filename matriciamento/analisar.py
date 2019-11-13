import pandas as pd
import xlsxwriter as excel_writer
from gerar_arquivo import sindromes_diagnosticos
from time import time

start_time = time()

with open("arquivo_fonte.csv", "r") as arquivo:
	dados = pd.read_csv(arquivo)

# Transformar sindrome_diagnostico em uma estrutura de contabilização
##### O QUE É UMA LISTA? MOSTRAR EXEMPLO RÁPIDO
todas_estruturas_analise = []
# Percorre cada síndrome de cada diagnóstico
for pair in sindromes_diagnosticos:
	for diagnostico in pair["DIAGNOSTICOS"]:
		novo = {
			"SINDROME": pair["SINDROME"],
			"DIAGNOSTICO": diagnostico,
			"QTDE DIAGNOSTICO": 0,
			"UBS": 0,
			"AME": 0,
			"AME/EXAMES": 0
		}
		
		todas_estruturas_analise.append(novo)

# Guardo tudo numa "planilha" (DataFrame)
data_analise = pd.DataFrame(todas_estruturas_analise)

# Para cada uma das linhas da planilha, analise cada diagnóstico de cada síndrome e
# contabilize os casos encaminhados para a UBS, o AME e AME/EXAMES
for identificador, linha in data_analise.iterrows():
	diagnostico_da_linha = linha["DIAGNOSTICO"]

	match = dados[dados["Diagnóstico Prévio"].str.contains(diagnostico_da_linha)]

	data_analise.at[identificador, "QTDE DIAGNOSTICO"] = match.shape[0]
	data_analise.at[identificador, "UBS"] = match[match["Conduta"] == "UBS"].shape[0]
	data_analise.at[identificador, "AME"] = match[match["Conduta"] == "AME"].shape[0]
	data_analise.at[identificador, "AME/EXAMES"] = match[match["Conduta"] == "AME/EXAMES"].shape[0]

end_time_analise = time() - start_time

# Escrevendo os dados da análise
planilha = excel_writer.Workbook("Analise.xlsx")

for sindrome in data_analise["SINDROME"].unique().tolist():
	data_sindrome = data_analise[data_analise["SINDROME"] == sindrome]
	total_sindrome = data_sindrome["QTDE DIAGNOSTICO"].sum()

	sheet = planilha.add_worksheet(sindrome)
	sheet.merge_range("A1:E1", sindrome)

	total_ubs = data_sindrome["UBS"].sum()
	sheet.write("B2", "UBS")
	sheet.write("B3", total_ubs)
	sheet.write("B4", float(total_ubs)/float(total_sindrome))

	total_ame = data_sindrome["AME"].sum()
	sheet.write("C2", "AME")
	sheet.write("C3", total_ame)
	sheet.write("C4", float(total_ame)/float(total_sindrome))

	total_exames = data_sindrome["AME/EXAMES"].sum()
	sheet.write("D2", "AME/EXAMES")
	sheet.write("D3", total_exames)
	sheet.write("D4", float(total_exames)/float(total_sindrome))

	sheet.write("E2", "Total")
	sheet.write("E3", total_sindrome)
	sheet.write("E4", "1")

	linha_ref = 5
	for diagnostico in data_sindrome["DIAGNOSTICO"].unique().tolist():
		data_diagnostico = data_sindrome[data_sindrome["DIAGNOSTICO"] == diagnostico]

		sheet.write("A" + str(linha_ref), diagnostico)
		sheet.write("B" + str(linha_ref), data_diagnostico["UBS"])
		sheet.write("C" + str(linha_ref), data_diagnostico["AME"])
		sheet.write("D" + str(linha_ref), data_diagnostico["AME/EXAMES"])

		total_diagnostico = data_diagnostico["UBS"] + data_diagnostico["AME"] + data_diagnostico["AME/EXAMES"]

		sheet.write("E" + str(linha_ref), total_diagnostico)
		sheet.write("F" + str(linha_ref), float(total_diagnostico)/float(total_sindrome))

		linha_ref += 1

planilha.close()

end_time_planilha = time() - start_time

print("Tempo de análise: {} segundos".format(end_time_analise))
print("Tempo de escrita de planilha: {} segundos".format(end_time_planilha))