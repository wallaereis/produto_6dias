import pandas as pd
import streamlit as st
import numpy as np


st.set_page_config(
    page_title="Controle",
    page_icon="🛒", # Use um emoji ou caminho de arquivo de imagem
    layout="wide"
)

df = pd.read_excel(r"Streamlit/Produto Abaixo de 6 dias.xlsx")

df["DATA"] = df["DATA"].dt.strftime("%d/%m/%Y")

# Páginas do sidebar
pagina = st.sidebar.radio("Ir para", ["Produtos", "Ajuste de Parâmetro"])

if pagina == "Produtos":
    #Título
    st.title("Produtos abaixo de 6 dias")

    # Filtro de Seleção

    st.sidebar.title("Filtros")

    lojas = st.sidebar.multiselect("Selecione a Loja",df["LOJA"].sort_values().unique(), default=df["LOJA"].sort_values().unique(),placeholder="Escolha opções")

    datas = st.sidebar.multiselect("Selecione a Data", df["DATA"].sort_values().unique(), default=[],placeholder="Escolha opções")


    #Aplicando Filtros

    filtro = df[(df["LOJA"].isin(lojas)) & (df["DATA"].isin(datas))]



    produtos_por_loja = filtro.groupby("LOJA")["SEQPRODUTO"].count().reset_index()

    #Contagem da loja
    itens = len(filtro)

    st.bar_chart(produtos_por_loja, x = "LOJA", y="SEQPRODUTO")


    # Dataframe
    st.dataframe(filtro,use_container_width=True)
    st.metric("Total de Produtos", itens)

#####################################################################################################

#Ajuste de pârametro

elif pagina == "Ajuste de Parâmetro":
    arquivo = st.file_uploader("Envie o Arquivo Excel", type=["xlsx"])

    if arquivo is not None:
        abs = pd.read_excel(arquivo, sheet_name=0)
        abs1 = pd.read_excel(arquivo, sheet_name=1)
        abs2 = pd.read_excel(arquivo, sheet_name=2)

        # --- Ajustes iniciais ---
        abs['CURVA ATUAL'] = abs['CURVA ATUAL'].replace(0, 'C')

        def dias_cobertura(x):
            x['DIAS COBERT MÍNIMO'] = x['CURVA ATUAL'].apply(lambda curva: 7 if curva == 'A' else (12 if curva == 'B' else 15))
            x['DIAS COBERT MÁXIMO'] = x['CURVA ATUAL'].apply(lambda curva: 10 if curva == 'A' else (15 if curva == 'B' else 20))
            return x

        # Merge com abs1
        abs = abs.merge(abs1, on='SEQPRODUTO', how='left')
        abs = abs[abs['SETOR'] == 'MERCEARIA']

        abs = abs.sort_values(by=['LOJA', 'DESCRICAO PRODUTO', 'FRENTE'], ascending=[True, True, False])
        abs = abs.drop_duplicates(subset=['LOJA', 'DESCRICAO PRODUTO'], keep='first')

        abs = abs[['LOJA', 'SEQPRODUTO','UNID', 'FRENTE', 'TOTAL UND','CURVA ATUAL', 'QTD ESTQ MÍNIMO','QTD ESTQ MÁXIMO']]

        abs['QTD ESTQ MÁXIMO'] = abs['UNID']
        abs['QTD ESTQ MÍNIMO'] = abs['TOTAL UND']
        abs['DIAS COBERT MÍNIMO'] = np.nan
        abs['DIAS COBERT MÁXIMO'] = np.nan

        # Merge com abs2
        abs = abs.merge(abs2, left_on=['LOJA','SEQPRODUTO'], right_on=['Empresa','Cód. Produto'], how='left')
        abs = abs.drop_duplicates(subset=['LOJA', 'SEQPRODUTO'], keep='first')

        # Aplica regra de cobertura
        abs = dias_cobertura(abs)

        # Filtro final
        abs = abs[['LOJA', 'SEQPRODUTO','QTD ESTQ MÍNIMO', 'QTD ESTQ MÁXIMO','DIAS COBERT MÍNIMO','DIAS COBERT MÁXIMO']]
        abs = abs[~abs['SEQPRODUTO'].isin([41102,1257,3938,31013,52])]

        # Renomear colunas
        abs.columns = ['LOJA', 'SEQPRODUTO', 'QTD ESTQ MINIMO', 'QTD ESTQ MAXIMO','DIAS COBERT MINIMO', 'DIAS COBERT MAXIMO']

        # Mostrar resultado
        st.success("Arquivo processado com sucesso!")
        st.dataframe(abs, use_container_width=True)

        # Botão para download
        csv = abs.to_csv(index=False, sep=";").encode("utf-8")
        st.download_button(
            label="⬇️ Baixar Ajuste de Parâmetro",
            data=csv,
            file_name="Ajuste_de_Parametro.csv",
            mime="text/csv"
        )













