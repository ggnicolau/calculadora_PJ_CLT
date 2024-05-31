# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os

directories = ["figs", "report"]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")

# Funções auxiliares e cálculos permanecem os mesmos

# Funções para cálculos
def calcular_decimo_terceiro_ferias(salario_bruto_anual):
    salario_mensal = salario_bruto_anual / 12
    decimo_terceiro = salario_mensal
    ferias = salario_mensal + (salario_mensal / 3)
    return decimo_terceiro + ferias

def calcular_salario_liquido_anual(salario_bruto_anual):
    # Faixas de imposto de renda anual
    faixa1 = 1903.98 * 12
    faixa2 = 2826.65 * 12
    faixa3 = 3751.05 * 12
    faixa4 = 4664.68 * 12
    aliquota_faixa2 = 0.075
    aliquota_faixa3 = 0.15
    aliquota_faixa4 = 0.225
    aliquota_faixa5 = 0.275
    deducao_faixa2 = 142.80 * 12
    deducao_faixa3 = 354.80 * 12
    deducao_faixa4 = 636.13 * 12
    deducao_faixa5 = 869.36 * 12

    # Cálculo do imposto de renda anual
    if salario_bruto_anual <= faixa1:
        imposto_de_renda_anual = 0
    elif salario_bruto_anual <= faixa2:
        imposto_de_renda_anual = (salario_bruto_anual - faixa1) * aliquota_faixa2 - deducao_faixa2
    elif salario_bruto_anual <= faixa3:
        imposto_de_renda_anual = (salario_bruto_anual - faixa2) * aliquota_faixa3 - deducao_faixa3
    elif salario_bruto_anual <= faixa4:
        imposto_de_renda_anual = (salario_bruto_anual - faixa3) * aliquota_faixa4 - deducao_faixa4
    else:
        imposto_de_renda_anual = (salario_bruto_anual - faixa4) * aliquota_faixa5 - deducao_faixa5

    # Cálculo do INSS anual considerando o teto e as alíquotas progressivas
    teto_mensal = 7507.49
    salario_mensal = salario_bruto_anual / 12
    if salario_mensal > teto_mensal:
        inss_anual = teto_mensal * 0.11 * 12
    else:
        inss_anual = salario_mensal * 0.11 * 12

    # Calcular salário líquido anual
    salario_liquido_anual = salario_bruto_anual - imposto_de_renda_anual - inss_anual

    return salario_liquido_anual

def calcular_custos_clt(salario_bruto_anual, alimentacao_saude):
    inss_patronal = 0.20 * salario_bruto_anual
    fgts = 0.08 * salario_bruto_anual
    sat = 0.02 * salario_bruto_anual
    salario_educacao = 0.025 * salario_bruto_anual
    decimo_terceiro_ferias = calcular_decimo_terceiro_ferias(salario_bruto_anual)
    return salario_bruto_anual + inss_patronal + fgts + sat + salario_educacao + decimo_terceiro_ferias + alimentacao_saude

def calcular_receita_liquida_mei(salario_bruto_anual, mei_impostos_fixos_anuais):
    return salario_bruto_anual - mei_impostos_fixos_anuais

def calcular_receita_liquida_pj(salario_bruto_anual, taxa_simples_nacional, pj_inss_minimo_mensal, pj_preco_contador_mensal, pj_taxa_prefeitura_mensal, pj_custos_iniciais):
    custos_mensais_anualizado = (pj_preco_contador_mensal * 12) + (pj_taxa_prefeitura_mensal * 12) + (pj_inss_minimo_mensal * 12)
    impostos = taxa_simples_nacional * salario_bruto_anual
    total_custos_anuais = pj_custos_iniciais + impostos + custos_mensais_anualizado
    return salario_bruto_anual - total_custos_anuais

def calcular_receita_liquida_clt(salario_bruto_anual, alimentacao_saude):
    salario_liquido_anual = calcular_salario_liquido_anual(salario_bruto_anual)
    beneficios_anuais = calcular_decimo_terceiro_ferias(salario_bruto_anual)
    fgts = 0.08 * salario_bruto_anual  # Incluindo FGTS na receita líquida, se quiser desconsiderar FGTS como líquido comente essa linha e tire do return
    return salario_liquido_anual + beneficios_anuais + alimentacao_saude + fgts

def calcular_valor_hora(receita_liquida_anual, horas_anuais):
    return receita_liquida_anual / horas_anuais

def calcular_economia(custo_clt, custo_outro):
    economia = custo_clt - custo_outro
    percentual_economia = (economia / custo_clt) * 100
    return economia, percentual_economia

# Funções para gráficos
def plot_empresa_custos(salario_bruto_anual, custo_clt_40h):
    plt.style.use('Solarize_Light2')
    labels = ['MEI', 'PJ', 'CLT']
    custos = [salario_bruto_anual, salario_bruto_anual, custo_clt_40h]

    fig, ax = plt.subplots()
    ax.bar(labels, custos, color=['#268bd2', '#2aa198', '#d33682'])
    ax.set_title('Custo para a Empresa')
    ax.set_ylabel('Custo Anual (R$)')
    plt.tight_layout()
    plt.savefig('figs/empresa_custos.png')
    plt.close()

def plot_receita_liquida(receita_liquida_mei_40h, receita_liquida_pj_40h, receita_liquida_clt_40h):
    plt.style.use('Solarize_Light2')
    labels = ['MEI', 'PJ', 'CLT']
    receita = [receita_liquida_mei_40h, receita_liquida_pj_40h, receita_liquida_clt_40h]

    fig, ax = plt.subplots()
    ax.bar(labels, receita, color=['#b58900', '#cb4b16', '#6c71c4'])
    ax.set_title('Receita Líquida Anual')
    ax.set_ylabel('Receita (R$)')
    plt.tight_layout()
    plt.savefig('figs/receita_liquida.png')
    plt.close()

def plot_valor_hora(valor_hora_mei_40h, valor_hora_pj_40h, valor_hora_clt_40h, valor_hora_mei_20h, valor_hora_pj_20h, valor_hora_clt_20h):
    plt.style.use('Solarize_Light2')
    labels = ['MEI (40h)', 'PJ (40h)', 'CLT (40h)', 'MEI (20h)', 'PJ (20h)', 'CLT (20h)']
    valor_hora = [valor_hora_mei_40h, valor_hora_pj_40h, valor_hora_clt_40h, valor_hora_mei_20h, valor_hora_pj_20h, valor_hora_clt_20h]

    fig, ax = plt.subplots()
    ax.bar(labels, valor_hora, color=['#859900', '#2aa198', '#268bd2', '#b58900', '#cb4b16', '#6c71c4'])
    ax.set_title('Valor-Hora')
    ax.set_ylabel('Valor (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('figs/valor_hora.png')
    plt.close()

def plot_valor_hora_necessario(valor_hora_necessario_mei_40h, valor_hora_necessario_pj_40h, valor_hora_necessario_mei_20h, valor_hora_necessario_pj_20h):
    plt.style.use('Solarize_Light2')
    labels = ['MEI (40h)', 'PJ (40h)', 'MEI (20h)', 'PJ (20h)']
    valor_hora = [valor_hora_necessario_mei_40h, valor_hora_necessario_pj_40h, valor_hora_necessario_mei_20h, valor_hora_necessario_pj_20h]

    fig, ax = plt.subplots()
    ax.bar(labels, valor_hora, color=['#268bd2', '#2aa198', '#b58900', '#cb4b16'])
    ax.set_title('Valor-Hora Necessário para Igualar CLT')
    ax.set_ylabel('Valor (R$)')
    plt.tight_layout()
    plt.savefig('figs/valor_hora_necessario.png')
    plt.close()

# Função para gerar o relatório em PDF
# Relatório PDF
class PDF(FPDF):
    def header(self):
        if self.page_no() > 2:
            self.set_fill_color(230, 230, 230)  # Barra cinza claro
            self.rect(0, 0, 210, 20, 'F')  # Retângulo para barra
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(0, 51, 102)
            self.cell(0, 10, 'Relatório Comparativo: MEI, PJ e CLT', 0, 1, 'C')
            self.ln(5)

    def chapter_title(self, title):
        self.set_fill_color(0, 51, 102)  # Azul escuro
        self.set_text_color(255, 255, 255)  # Texto branco
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(5)

    def chapter_subtitle(self, subtitle):
        self.set_fill_color(0, 102, 204)  # Azul
        self.set_text_color(255, 255, 255)  # Texto branco
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, subtitle, 0, 1, 'L', fill=True)
        self.ln(3)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        self.set_text_color(0, 0, 0)  # Preto para o corpo do texto
        self.multi_cell(0, 7.5, body, align='J')
        self.ln(4)

    def add_table(self, data, col_widths):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(200, 200, 200)  # fundo cinza claro para cabeçalhos
        for i, row in enumerate(data):
            for item, width in zip(row, col_widths):
                if i == 0:
                    self.set_text_color(0, 0, 0)  # Texto preto para cabeçalhos
                    self.cell(width, 10, item, 1, 0, 'C', fill=True)
                else:
                    self.set_text_color(0, 0, 0)  # Texto preto para o corpo da tabela
                    self.cell(width, 10, item, 1)
            self.ln()

    def add_image(self, image_path, x=None, y=None, w=0, h=0):
        self.image(image_path, x=x, y=y, w=w, h=h)

def gerar_relatorio(autor, salario_bruto_mensal, alimentacao_saude_mensal, pj_inss_minimo_mensal, taxa_simples_nacional, pj_preco_contador_mensal):
    # Calculando variáveis
    salario_bruto_anual = salario_bruto_mensal * 12
    alimentacao_saude = alimentacao_saude_mensal * 12
    mei_impostos_fixos_anuais = 804.00
    pj_custos_iniciais = 895.00
    pj_taxa_prefeitura_mensal = 100.00

    horas_anuais_40h = 2080
    custo_clt_40h = calcular_custos_clt(salario_bruto_anual, alimentacao_saude)
    receita_liquida_mei_40h = calcular_receita_liquida_mei(salario_bruto_anual, mei_impostos_fixos_anuais)
    receita_liquida_pj_40h = calcular_receita_liquida_pj(salario_bruto_anual, taxa_simples_nacional, pj_inss_minimo_mensal, pj_preco_contador_mensal, pj_taxa_prefeitura_mensal, pj_custos_iniciais)
    receita_liquida_clt_40h = calcular_receita_liquida_clt(salario_bruto_anual, alimentacao_saude)

    valor_hora_mei_40h = calcular_valor_hora(receita_liquida_mei_40h, horas_anuais_40h)
    valor_hora_pj_40h = calcular_valor_hora(receita_liquida_pj_40h, horas_anuais_40h)
    valor_hora_clt_40h = calcular_valor_hora(receita_liquida_clt_40h, horas_anuais_40h)

    valor_hora_necessario_mei_40h = (receita_liquida_clt_40h + mei_impostos_fixos_anuais) / horas_anuais_40h
    valor_hora_necessario_pj_40h = (receita_liquida_clt_40h + pj_custos_iniciais + (pj_preco_contador_mensal * 12) + (pj_taxa_prefeitura_mensal * 12) + (taxa_simples_nacional * salario_bruto_anual)) / horas_anuais_40h

    horas_anuais_20h = 1040
    salario_bruto_anual_20h = salario_bruto_anual / 2
    custo_clt_20h = calcular_custos_clt(salario_bruto_anual_20h, alimentacao_saude)
    receita_liquida_mei_20h = calcular_receita_liquida_mei(salario_bruto_anual_20h, mei_impostos_fixos_anuais)
    receita_liquida_pj_20h = calcular_receita_liquida_pj(salario_bruto_anual_20h, taxa_simples_nacional, pj_inss_minimo_mensal, pj_preco_contador_mensal, pj_taxa_prefeitura_mensal, pj_custos_iniciais)
    receita_liquida_clt_20h = calcular_receita_liquida_clt(salario_bruto_anual_20h, alimentacao_saude)

    valor_hora_mei_20h = calcular_valor_hora(receita_liquida_mei_20h, horas_anuais_20h)
    valor_hora_pj_20h = calcular_valor_hora(receita_liquida_pj_20h, horas_anuais_20h)
    valor_hora_clt_20h = calcular_valor_hora(receita_liquida_clt_20h, horas_anuais_20h)

    valor_hora_necessario_mei_20h = (receita_liquida_clt_20h + mei_impostos_fixos_anuais) / horas_anuais_20h
    valor_hora_necessario_pj_20h = (receita_liquida_clt_20h + pj_custos_iniciais + (pj_preco_contador_mensal * 12) + (pj_taxa_prefeitura_mensal * 12) + (taxa_simples_nacional * salario_bruto_anual_20h)) / horas_anuais_20h

    economia_mei_40h, percentual_economia_mei_40h = calcular_economia(custo_clt_40h, salario_bruto_anual)
    economia_pj_40h, percentual_economia_pj_40h = calcular_economia(custo_clt_40h, salario_bruto_anual + pj_custos_iniciais + (pj_preco_contador_mensal * 12) + (pj_taxa_prefeitura_mensal * 12) + (taxa_simples_nacional * salario_bruto_anual))

    custo_mei_ajustado_40h = valor_hora_necessario_mei_40h * horas_anuais_40h
    custo_pj_ajustado_40h = valor_hora_necessario_pj_40h * horas_anuais_40h
    economia_pj_40h_ajustada, percentual_economia_pj_40h_ajustada = calcular_economia(custo_clt_40h, custo_pj_ajustado_40h)

    economia_mei_20h, percentual_economia_mei_20h = calcular_economia(custo_clt_20h, salario_bruto_anual_20h)
    economia_pj_20h, percentual_economia_pj_20h = calcular_economia(custo_clt_20h, salario_bruto_anual_20h + (pj_custos_iniciais) + (pj_preco_contador_mensal * 12) + (pj_taxa_prefeitura_mensal * 12) + (taxa_simples_nacional * salario_bruto_anual_20h))

    custo_mei_ajustado_20h = valor_hora_necessario_mei_20h * horas_anuais_20h
    custo_pj_ajustado_20h = valor_hora_necessario_pj_20h * horas_anuais_20h
    economia_pj_20h_ajustada, percentual_economia_pj_20h_ajustada = calcular_economia(custo_clt_20h, custo_pj_ajustado_20h)

    # Criação dos gráficos
    plot_empresa_custos(salario_bruto_anual, custo_clt_40h)
    plot_receita_liquida(receita_liquida_mei_40h, receita_liquida_pj_40h, receita_liquida_clt_40h)
    plot_valor_hora(valor_hora_mei_40h, valor_hora_pj_40h, valor_hora_clt_40h, valor_hora_mei_20h, valor_hora_pj_20h, valor_hora_clt_20h)
    plot_valor_hora_necessario(valor_hora_necessario_mei_40h, valor_hora_necessario_pj_40h, valor_hora_necessario_mei_20h, valor_hora_necessario_pj_20h)

    pdf = PDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # SEÇÃO: Adicionando a capa com design
    pdf.add_page()
    pdf.set_fill_color(0, 51, 102)  # Azul escuro
    pdf.set_text_color(0, 51, 102)  # Texto azul escuro
    pdf.set_font('Helvetica', 'B', 36)
    pdf.set_xy(40, 100)  # Posiciona o texto mais para o centro
    pdf.cell(0, 10, 'Proposta de Trabalho', 0, 1, 'L')
    pdf.set_font('Helvetica', 'I', 12)
    pdf.set_xy(70, 130)  # Posiciona o texto mais para o centro
    pdf.cell(0, 10, f'Autor: {autor}', 0, 1, 'L')

    # SEÇÃO: Adicionando a página de proposta
    pdf.add_page()
    pdf.chapter_title("Proposta")
    economia_pj_valor = economia_pj_20h_ajustada
    percentual_economia_pj = percentual_economia_pj_20h_ajustada

    proposta_texto = f"""
    Proponho ser contratado como PJ por 20 horas semanais, o que resultará em uma economia significativa para a empresa, com uma redução de custo de aproximadamente {percentual_economia_pj:.2f}% em comparação à CLT, mesmo após equiparar o valor-hora de colaboração do tipo PJ com o regime CLT, para R$ {valor_hora_necessario_pj_20h:.2f}. Ou seja, em termos financeiros, todos ganham: contratante e contratado.

    Também há um ganho qualitativo relevante. Esta abordagem permitirá que a empresa tenha flexibilidade para alocar recursos adicionais, otimizando a equipe sem sobrecarregar os colaboradores. Caso haja interesse, pode-se contratar duas pessoas para 20 horas semanais cada, ao invés de uma única pessoa para 40 horas, tornando a equipe mais produtiva, ágil e eficiente. A combinação de diferentes habilidades e a distribuição da carga de trabalho garantem uma rotina sustentável, promovendo a saúde e bem-estar dos colaboradores.

    Como PJ, minha rotina de trabalho pode ser de comprometimento contínuo para um ou diversos projetos com o contratante, atendendo às demandas da empresa conforme elas aparecem, pelo período que houver interesse de colaboração. No restante do tempo, posso me dedicar a outras atividades que tenho em vista, como estudar, aperfeiçoar minhas habilidades, lazer e projetos pessoais.

    Além disso, a modalidade PJ me possibilitará ter experiência de tecnologia enquanto empresa, o que permite concorrer a licitações públicas que começam a aparecer cada vez mais na área de tecnologia.

    Segue nas próximas páginas um relatório detalhado que demonstra como a proposta é vantajosa pra ambas as partes, comparando os ganhos para o contratante com os ganhos para o contratado.
    """

    pdf.chapter_body(proposta_texto)
    pdf.add_page()

    # SEÇÃO: Custos para empresa em cada situação
    pdf.chapter_title("1) Quanto a Empresa Gasta em Cada Situação (40h)")

    pdf.chapter_subtitle("a) Contratação como MEI")
    pdf.chapter_body(f"  - Custo para a Empresa: R$ {salario_bruto_anual:,.2f} (salário bruto anual)")

    pdf.chapter_subtitle("b) Contratação como PJ")
    pdf.chapter_body(f"  - Custo para a Empresa: R$ {salario_bruto_anual:,.2f} (salário bruto anual)")

    pdf.chapter_subtitle("c) Contratação como CLT")
    pdf.chapter_body(f"""  1. Salário Bruto Anual: R$ {salario_bruto_anual:,.2f}
    2. INSS Patronal: 20% x R$ {salario_bruto_anual:,.2f} = R$ {0.20 * salario_bruto_anual:,.2f}
    3. FGTS: 8% x R$ {salario_bruto_anual:,.2f} = R$ {0.08 * salario_bruto_anual:,.2f}
    4. SAT: 2% x R$ {salario_bruto_anual:,.2f} = R$ {0.02 * salario_bruto_anual:,.2f}
    5. Salário-Educação: 2,5% x R$ {salario_bruto_anual:,.2f} = R$ {0.025 * salario_bruto_anual:,.2f}
    6. 13º Salário e Férias (com 1/3 adicional): R$ {calcular_decimo_terceiro_ferias(salario_bruto_anual):,.2f}
    7. Alimentação e Saúde: R$ 1.000,00 x 12 = R$ {alimentacao_saude:,.2f}

    - Custo Total para a Empresa (CLT): R$ {custo_clt_40h:,.2f}
    """)

    pdf.chapter_subtitle("Comparação dos Custos para a Empresa")
    table_data = [
        ["Situação", "Custo Anual para a Empresa"],
        ["MEI", f"R$ {salario_bruto_anual:,.2f}"],
        ["PJ", f"R$ {salario_bruto_anual:,.2f}"],
        ["CLT", f"R$ {custo_clt_40h:,.2f}"]
    ]
    pdf.add_table(table_data, [70, 70])

    pdf.set_font('Helvetica', 'B', 12)
    pdf.ln(10)
    pdf.chapter_body(f"A empresa economiza R$ {custo_clt_40h - salario_bruto_anual:,.2f} ({(custo_clt_40h - salario_bruto_anual) / custo_clt_40h * 100:.2f}%) ao contratar como MEI ou PJ em vez de como CLT. Já o contratado, sai em prejuízo considerável. Isso necessariamente abre espaço para negociações mais justas e equilibradas, onde ambas as partes saem ganhando.")

    # Adicionando gráfico de comparação dos custos para a empresa
    if pdf.get_y() + 100 > pdf.h - pdf.b_margin:
        pdf.add_page()
    pdf.add_image('figs/empresa_custos.png', x=40, y=pdf.get_y(), w=120)
    pdf.ln(100)

    pdf.add_page()

    # SEÇÃO: Custos para contratado em cada situação
    pdf.chapter_title("2) Quanto o Contratado Gasta em Cada Situação (40h)")

    pdf.chapter_subtitle("a) Como MEI")
    pdf.chapter_body(f"""  1. Impostos Fixos Mensais: R$ 67,00 x 12 = R$ 804,00""")
    pdf.ln(0.02)   # Adiciona um espaço menor que uma linha completa
    pdf.chapter_body(f"""   Receita Líquida Anual: R$ {salario_bruto_anual:,.2f} - R$ 804,00 = R$ {receita_liquida_mei_40h:,.2f}""")

    pdf.chapter_subtitle("b) Como PJ")
    pdf.chapter_body(f"""  1. Custos Iniciais:
        - Abertura da Empresa: R$ 800,00
        - Taxa Jucesp: R$ 95,00
    2. Custos Mensais:
        - Contador: R$ {pj_preco_contador_mensal:.2f} x 12 = R$ {pj_preco_contador_mensal * 12:,.2f}
        - Taxa com a Prefeitura: R$ 100,00 x 12 = R$ 1.200,00
        - Contribuição do INSS: R$ 145,20 x 12 = R$ {145.20 * 12:,.2f}
        - Total Mensal: R$ {(pj_preco_contador_mensal * 12) + 1200 + (145.20 * 12):,.2f}
    3. Impostos sobre Faturamento (Simples Nacional, estimativa média de {taxa_simples_nacional * 100:.2f}%):
        - {taxa_simples_nacional * 100:.2f}% x R$ {salario_bruto_anual:,.2f} = R$ {taxa_simples_nacional * salario_bruto_anual:,.2f}
    4. Total de Custos Anuais:
        - Custos Mensais: R$ {(pj_preco_contador_mensal * 12) + 1200 + (145.20 * 12):,.2f}
        - Custos Iniciais: R$ 895,00
        - Impostos: R$ {taxa_simples_nacional * salario_bruto_anual:,.2f}
        - Total: R$ {895 + (pj_preco_contador_mensal * 12) + 1200 + (145.20 * 12) + (taxa_simples_nacional * salario_bruto_anual):,.2f}""")
    pdf.ln(0.02)   # Adiciona um espaço menor que uma linha completa
    pdf.chapter_body(f"""   Receita Líquida Anual: R$ {salario_bruto_anual:,.2f} - R$ {895 + (pj_preco_contador_mensal * 12) + 1200 + (145.20 * 12) + (taxa_simples_nacional * salario_bruto_anual):,.2f} = R$ {receita_liquida_pj_40h:,.2f}""")

    pdf.chapter_subtitle("c) Como CLT")
    pdf.chapter_body(f"""  1. Salário Líquido Anual (bruto - impostos): R$ {calcular_salario_liquido_anual(salario_bruto_anual):,.2f}
    2. Benefícios Anuais (Férias e 13º): R$ {calcular_decimo_terceiro_ferias(salario_bruto_anual):,.2f}
    3. Alimentação e Saúde: R$ 1.000,00 x 12 = R$ {alimentacao_saude:,.2f}
    4. FGTS: 8% x R$ {salario_bruto_anual:,.2f} = R$ {0.08 * salario_bruto_anual:,.2f}
    """)

    # Calculando o valor total dos benefícios adicionais
    beneficios_adicionais = calcular_decimo_terceiro_ferias(salario_bruto_anual) + alimentacao_saude + (0.08 * salario_bruto_anual)

    pdf.ln(0.02)  # Adiciona um espaço menor que uma linha completa
    # Adicionando a linha de Receita Líquida Anual com a soma dos benefícios
    pdf.chapter_body(f"""  Receita Líquida Anual: R$ {calcular_salario_liquido_anual(salario_bruto_anual):,.2f} + R$ {beneficios_adicionais:,.2f} = R$ {receita_liquida_clt_40h:,.2f}""")

    pdf.chapter_subtitle("Comparação dos Seus Custos e Receita Líquida")
    table_data = [
        ["Situação", "Receita Bruta Anual", "Custos Anuais", "Benefícios", "Receita Líquida Anual"],
        ["MEI", f"R$ {salario_bruto_anual:,.2f}", "R$ 804,00", "-", f"R$ {receita_liquida_mei_40h:,.2f}"],
        ["PJ", f"R$ {salario_bruto_anual:,.2f}", f"R$ {895 + 4440 + (taxa_simples_nacional * salario_bruto_anual):,.2f}", "-", f"R$ {receita_liquida_pj_40h:,.2f}"],
        ["CLT", f"R$ {salario_bruto_anual:,.2f}", f"R$ {abs(salario_bruto_anual - calcular_salario_liquido_anual(salario_bruto_anual)):,.2f}", f"R$ {calcular_decimo_terceiro_ferias(salario_bruto_anual) + alimentacao_saude:,.2f}", f"R$ {receita_liquida_clt_40h:,.2f}"]
    ]
    pdf.add_table(table_data, [25, 41, 34, 29, 45])

    # Adicionando gráfico de receita líquida
    pdf.add_image('figs/receita_liquida.png', x=40, y=pdf.get_y() + 10, w=120)
    pdf.ln(110)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 5, "MUITO IMPORTANTE: O teto para MEI é R$81 mil anuais.", 0, 1, 'C')
    pdf.cell(0, 5, "Caso a receita bruta seja maior do que isso, devemos desconsiderar MEI", 0, 1, 'C')
    pdf.cell(0, 5, "como uma alternativa em todos os cenários do relatório.", 0, 1, 'C')
    pdf.cell(0, 5, "Vale notar que existe uma lei para ser aprovada que sobe o teto para aproximadamente R$145 mil.", 0, 1, 'C')

    pdf.add_page()

    # SEÇÃO: Comparação do valor-hora para cada situação
    pdf.chapter_title("3) Comparação do Valor-Hora (20h e 40h)")

    pdf.chapter_subtitle("40 horas semanais (2080 horas por ano)")
    table_data = [
        ["Situação", "Receita Líquida Anual", "Valor-Hora"],
        ["MEI", f"R$ {receita_liquida_mei_40h:,.2f}", f"R$ {valor_hora_mei_40h:,.2f}"],
        ["PJ", f"R$ {receita_liquida_pj_40h:,.2f}", f"R$ {valor_hora_pj_40h:,.2f}"],
        ["CLT", f"R$ {receita_liquida_clt_40h:,.2f}", f"R$ {valor_hora_clt_40h:,.2f}"]
    ]
    pdf.add_table(table_data, [70, 60, 50])

    pdf.ln(5)
    pdf.chapter_subtitle("20 horas semanais (1040 horas por ano)")
    table_data = [
        ["Situação", "Receita Líquida Anual", "Valor-Hora"],
        ["MEI", f"R$ {receita_liquida_mei_20h:,.2f}", f"R$ {valor_hora_mei_20h:,.2f}"],
        ["PJ", f"R$ {receita_liquida_pj_20h:,.2f}", f"R$ {valor_hora_pj_20h:,.2f}"],
        ["CLT", f"R$ {receita_liquida_clt_20h:,.2f}", f"R$ {valor_hora_clt_20h:,.2f}"]
    ]
    pdf.add_table(table_data, [70, 60, 50])

    # Adicionando gráfico de valor-hora
    pdf.add_image('figs/valor_hora.png', x=40, y=pdf.get_y() + 10, w=120)
    pdf.ln(70)

    pdf.add_page()

    # SEÇÃO: Equiparando valor-hora de MEI e PJ para CLT
    pdf.chapter_title("4) Ajustando Valor-Hora para Igualar à Receita Líquida CLT")

    pdf.chapter_subtitle(f"40 horas semanais (2080 horas por ano) - R$ {valor_hora_clt_40h:.2f} CLT")
    table_data = [
        ["Situação", "Receita Líquida Alvo", "Valor-Hora Necessário"],
        ["MEI", f"R$ {receita_liquida_clt_40h:,.2f}", f"R$ {valor_hora_necessario_mei_40h:,.2f}"],
        ["PJ", f"R$ {receita_liquida_clt_40h:,.2f}", f"R$ {valor_hora_necessario_pj_40h:,.2f}"]
    ]
    pdf.add_table(table_data, [70, 60, 50])

    pdf.ln(5)
    pdf.chapter_subtitle(f"20 horas semanais (1040 horas por ano) - R$ {valor_hora_clt_20h:.2f} CLT")
    table_data = [
        ["Situação", "Receita Líquida Alvo", "Valor-Hora Necessário"],
        ["MEI", f"R$ {receita_liquida_clt_20h:,.2f}", f"R$ {valor_hora_necessario_mei_20h:,.2f}"],
        ["PJ", f"R$ {receita_liquida_clt_20h:,.2f}", f"R$ {valor_hora_necessario_pj_20h:,.2f}"]
    ]
    pdf.add_table(table_data, [70, 60, 50])
    pdf.ln(7)

    # Adicionando gráfico de quanto cobrar por hora para igualar CLT
    pdf.add_image('figs/valor_hora_necessario.png', x=40, y=pdf.get_y(), w=120)
    pdf.ln(100)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 5, f"A empresa ainda economiza {percentual_economia_pj_20h_ajustada:.2f}%-{percentual_economia_pj_40h_ajustada:.2f}% ao contratar como PJ com valor-hora ajustado.", 0, 1, 'C')
    pdf.cell(0, 5, f"A empresa economiza R$ {economia_pj_20h_ajustada:,.2f} para 20h e R$ {economia_pj_40h_ajustada:,.2f} para 40h.", 0, 1, 'C')

    # SEÇÃO: Resumo das Comparações
    pdf.add_page()
    pdf.chapter_title("Resumo das Comparações")

    pdf.chapter_subtitle("Custo para a Empresa")
    pdf.chapter_body(f"1. MEI: R$ {salario_bruto_anual:,.2f}\n2. PJ: R$ {salario_bruto_anual:,.2f}\n3. CLT: R$ {custo_clt_40h:,.2f}")

    pdf.chapter_subtitle("Sua Receita Líquida")
    pdf.chapter_body(f"1. MEI: R$ {receita_liquida_mei_40h:,.2f}\n2. PJ: R$ {receita_liquida_pj_40h:,.2f}\n3. CLT: R$ {receita_liquida_clt_40h:,.2f}")

    pdf.chapter_subtitle("Valor-Hora")
    pdf.chapter_body(f"""40 horas semanais:
    - MEI: R$ {valor_hora_mei_40h:,.2f}
    - PJ: R$ {valor_hora_pj_40h:,.2f}
    - CLT: R$ {valor_hora_clt_40h:,.2f}

    20 horas semanais:
    - MEI: R$ {valor_hora_mei_20h:,.2f}
    - PJ: R$ {valor_hora_pj_20h:,.2f}
    - CLT: R$ {valor_hora_clt_20h:,.2f}""")

    pdf.chapter_subtitle("Valor-Hora Necessário para Igualar CLT")
    pdf.chapter_body(f"""40 horas semanais:
    - MEI: R$ {valor_hora_necessario_mei_40h:,.2f}
    - PJ: R$ {valor_hora_necessario_pj_40h:,.2f}

    20 horas semanais:
    - MEI: R$ {valor_hora_necessario_mei_20h:,.2f}
    - PJ: R$ {valor_hora_necessario_pj_20h:,.2f}""")

    pdf.chapter_title("Conclusão")
    pdf.chapter_body(f"""- Para a Empresa: Contratar como MEI ou PJ é significativamente mais econômico do que como CLT, economizando aproximadamente R$ {custo_clt_40h - salario_bruto_anual:,.2f} ({(custo_clt_40h - salario_bruto_anual) / custo_clt_40h * 100:.2f}%) para 40h.
    - Para Contratado: A receita líquida anual é maior como CLT quando consideramos os benefícios adicionais de alimentação e saúde, seguida por MEI e depois PJ.
    - Valor-Hora: O valor-hora é consideravelmente mais alto no regime CLT, seguido por MEI e apenas depois por PJ, tanto para 40 horas semanais quanto para 20 horas semanais. Entendemos que isso abre margem para negociação.
    - Valor-Hora Necessário para Igualar CLT: Para igualar a receita líquida do CLT, o contratado precisaria cobrar R$ {valor_hora_necessario_mei_40h:,.2f} por hora como MEI e R$ {valor_hora_necessario_pj_40h:,.2f} por hora como PJ para 40 horas semanais. Para 20 horas semanais, precisaria cobrar R$ {valor_hora_necessario_mei_20h:,.2f} por hora como MEI e R$ {valor_hora_necessario_pj_20h:,.2f} por hora como PJ.
    """)

    # Adiciona o texto em negrito logo após o texto anterior
    pdf.set_font('Helvetica', 'B', 12)  # Define a fonte para negrito
    pdf.multi_cell(0, 7.5, f"- Após o ajuste de horas para igualar CLT, a empresa ainda continua economizando aproximadamente R$ {economia_pj_40h_ajustada:,.2f} ({percentual_economia_pj_40h_ajustada:.2f}%) para 40h e R$ {economia_pj_20h_ajustada:,.2f} ({percentual_economia_pj_20h_ajustada:.2f}%) para 20h. A contratante continua a maior beneficiária na troca do regime CLT para PJ.")
    pdf.set_font('Helvetica', '', 12)  # Volta para a fonte normal

    # Gerar e salvar PDF
    pdf_path = 'report/Relatorio_Comparativo_MEI_PJ_CLT.pdf'
    pdf.output(pdf_path)
    return pdf_path


# Definir estilos CSS
st.markdown("""
    <style>
    .container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        gap: 20px;
    }
    .container div {
        flex: 1 1 45%;
        max-width: 45%;
    }
    .css-18e3th9 {
        background-color: #2e3b4e !important;
        padding: 20px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        color: white !important;
    }
    .css-18e3th9 input, .css-18e3th9 select {
        background-color: #3f4c63 !important;
        border: 1px solid #ffffff !important;
        color: white !important;
    }
    .css-18e3th9 .stNumberInput input {
        color: white !important;
    }
    .stButton>button {
        background-color: #ff4081 !important;
        border: 1px solid #ff4081 !important;
        color: white !important;
        margin: 0 auto !important;
        display: block !important;
    }
    .stButton>button:hover {
        background-color: #ff79a6 !important;
        border: 1px solid #ff79a6 !important;
    }
    .css-145kmo2 {
        display: flex;
        justify-content: center;
    }
    .css-145kmo2 h1 {
        color: #2e3b4e !important;
    }
    .css-145kmo2 h2 {
        color: #2e3b4e !important;
    }
    </style>
""", unsafe_allow_html=True)

# Interface Streamlit
st.title("Gerador de Relatório")
st.subheader("Vantagens e desvantagens do PJ para contratante e contratado")

col1, col2 = st.columns(2)

with st.container():
    with col1:
        autor = st.text_input("Autor", value="Guilherme G. Nicolau, PhD")
        salario_bruto_mensal = st.number_input("Salário Bruto Mensal (R$) - CLT", value=23000.00, step=500.00)
    with col2:
        alimentacao_saude_mensal = st.number_input("Alimentação e Saúde Mensal - CLT (R$)", value=1200.00, step=50.00)
        pj_inss_minimo_mensal = st.number_input("Contribuição INSS Mínimo PJ Mensal - PJ (R$)", value=145.20, step=10.00)

col3, col4 = st.columns(2)

with st.container():
    with col3:
        taxa_simples_nacional = st.number_input("Taxa Simples Nacional - PJ (%)", value=8.00, step=0.5) / 100
    with col4:
        pj_preco_contador_mensal = st.number_input("Preço do Contador Mensal - PJ (R$)", value=300.00, step=50.00)

if st.button("Gerar Relatório"):
    with st.spinner("Gerando relatório..."):
        pdf_path = gerar_relatorio(autor, salario_bruto_mensal, alimentacao_saude_mensal, pj_inss_minimo_mensal, taxa_simples_nacional, pj_preco_contador_mensal)
        st.success("Relatório gerado com sucesso!")
        with open(pdf_path, "rb") as file:
            st.download_button(label="Baixar Relatório", data=file, file_name="Relatorio_Comparativo_MEI_PJ_CLT.pdf")