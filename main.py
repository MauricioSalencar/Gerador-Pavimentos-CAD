
import os
import ezdxf


# ============================================================
# 1. CONFIGURAÇÕES GERAIS DO PROJETO
# ============================================================
# Nesta seção ficam reunidos os valores que controlam a
# aparência e as dimensões gerais do desenho.
#
# Alterar esses valores permite modificar o desenho sem
# precisar procurar números espalhados pelo código.

# Comprimento horizontal das linhas que representam os pisos.
LARGURA = 6000

# Altura dos textos dos nomes dos pavimentos, em milímetros.
ALTURA_TEXTO = 120

# Distância horizontal das cotas em relação ao desenho.
X_COTA_LAJE = -700
X_COTA_ALTURA = -1500

# Nome do arquivo DXF que será gerado.
NOME_ARQUIVO = "pavimentos.dxf"

# Nome do estilo de texto utilizado nos pavimentos.
ESTILO_NOMES = "NOMES_PAVIMENTOS"


# ============================================================
# 2. CRIAÇÃO E CONFIGURAÇÃO DO DOCUMENTO DXF
# ============================================================
# Cria um novo documento DXF no formato R2010.
# O parâmetro setup=True carrega configurações e estilos
# padrão necessários para trabalhar com cotas e textos.

doc = ezdxf.new("R2010", setup=True)

# Define a unidade do desenho como milímetros.
doc.header["$INSUNITS"] = 4

# Acessa o espaço principal de desenho do DXF.
msp = doc.modelspace()


# ============================================================
# 3. CRIAÇÃO DAS CAMADAS DO DESENHO
# ============================================================
# As camadas organizam os elementos do desenho.
#
# GEOMETRIA: linhas dos pisos e tetos.
# COTAS: dimensões e indicações de medidas.
# TEXTOS: nomes dos pavimentos e topo do edifício.
#
# As cores são definidas pelo índice de cores do AutoCAD:
# 7 = branco/preto, dependendo do fundo.
# 1 = vermelho.

doc.layers.new(
    "GEOMETRIA",
    dxfattribs={"color": 7}
)

doc.layers.new(
    "COTAS",
    dxfattribs={"color": 1}
)

doc.layers.new(
    "TEXTOS",
    dxfattribs={"color": 7}
)


# ============================================================
# 4. CONFIGURAÇÃO DOS ESTILOS DE TEXTO E COTA
# ============================================================

# Cria um estilo exclusivo para os nomes dos pavimentos.
# A fonte escolhida é Liberation Sans.
#
# Os textos que não receberem esse estilo continuarão
# utilizando o estilo Standard.

if ESTILO_NOMES not in doc.styles:
    doc.styles.new(
        ESTILO_NOMES,
        dxfattribs={
            "font": "LiberationSans-Regular.ttf"
        }
    )


# Configura o fator de escala linear do estilo de cotas.
# O valor 1 significa que a medida será exibida sem
# multiplicação ou divisão.
#
# Exemplo:
# Medida real: 3000 mm
# Valor exibido: 3000

if "EZDXF" in doc.dimstyles:
    doc.dimstyles.get("EZDXF").dxf.dimlfac = 1


# ============================================================
# 5. FUNÇÃO PARA DESENHAR LINHAS
# ============================================================
# Recebe dois pontos (x1, y1) e (x2, y2) e cria uma linha
# entre eles na camada informada.
#
# Essa função é utilizada para desenhar as referências
# horizontais dos pisos e tetos.

def desenhar_linha(x1, y1, x2, y2, camada):

    msp.add_line(
        (x1, y1),
        (x2, y2),
        dxfattribs={
            "layer": camada
        }
    )


# ============================================================
# 6. FUNÇÃO PARA INSERIR TEXTOS
# ============================================================
# Insere um texto no desenho.
#
# Parâmetros:
# texto  = conteúdo que será escrito.
# x e y  = posição do texto no desenho.
# camada = camada na qual o texto será inserido.
# altura = tamanho do texto.
# estilo = fonte utilizada.
#
# O estilo Standard é o padrão.
# Para os nomes dos pavimentos, utilizamos Liberation Sans.

def escrever_texto(
    texto,
    x,
    y,
    camada,
    altura=ALTURA_TEXTO,
    estilo="Standard"
):

    msp.add_text(
        str(texto),
        dxfattribs={
            "insert": (x, y),
            "height": altura,
            "layer": camada,
            "style": estilo
        }
    )


# ============================================================
# 7. FUNÇÃO PARA DESENHAR COTAS VERTICAIS
# ============================================================
# Cria uma cota vertical nativa do AutoCAD.
#
# Ela recebe:
# y1      = primeira posição vertical.
# y2      = segunda posição vertical.
# x_cota  = posição horizontal da linha de cota.
#
# A função organiza as coordenadas para evitar medidas
# negativas e configura a aparência das cotas.
#
# Como é uma cota nativa, ela pode ser editada no AutoCAD.

def desenhar_cota_vertical(y1, y2, x_cota):

    # Não cria cotas quando as duas posições são iguais.
    if y1 == y2:
        return

    # Organiza os valores do menor para o maior.
    menor_y = min(y1, y2)
    maior_y = max(y1, y2)

    # Cria a cota vertical.
    cota = msp.add_linear_dim(

        # Define a posição da linha de cota.
        base=(
            x_cota,
            (menor_y + maior_y) / 2
        ),

        # Define os pontos que serão medidos.
        p1=(0, menor_y),
        p2=(0, maior_y),

        # Define a orientação vertical.
        angle=90,

        # Utiliza o estilo de cota EZDXF.
        dimstyle="EZDXF",

        # Configurações visuais da cota.
        override={

            # Altura do texto da cota.
            "dimtxt": 180,

            # Tamanho das setas.
            "dimasz": 100,

            # Quantidade de casas decimais.
            "dimdec": 0,

            # Cor da linha de cota.
            "dimclrd": 1,

            # Cor das linhas auxiliares.
            "dimclre": 1,

            # Cor do texto da cota.
            "dimclrt": 1,

            # Distância das linhas auxiliares.
            "dimexo": 30,
            "dimexe": 50,

            # Posicionamento do texto.
            "dimtad": 1,
            "dimtvp": 0,
        },

        # Insere a cota na camada COTAS.
        dxfattribs={
            "layer": "COTAS"
        }
    )

    # Transforma a definição da cota em elementos DXF.
    cota.render()


# ============================================================
# 8. FUNÇÃO PARA CALCULAR AS POSIÇÕES DOS PAVIMENTOS
# ============================================================
# Calcula as três alturas principais de cada pavimento:
#
# piso_atual:
# Altura da linha que representa o piso atual.
#
# teto_atual:
# Altura da parte inferior da laje.
#
# proximo_piso:
# Altura do piso do pavimento seguinte.
#
# Os valores são calculados a partir das medidas fornecidas.

def calcular_posicoes(piso_y, pavimento):

    # Posição do piso atual.
    piso_atual = piso_y

    # Posição do teto, somando a altura piso a teto.
    teto_atual = (
        piso_atual + pavimento["piso_teto"]
    )

    # Posição do próximo piso, somando a altura piso a piso.
    proximo_piso = (
        piso_atual + pavimento["piso_piso"]
    )

    return piso_atual, teto_atual, proximo_piso


# ============================================================
# 9. FUNÇÃO PARA RECEBER AS MEDIDAS MANUALMENTE
# ============================================================
# Solicita ao usuário a quantidade de pavimentos e as
# medidas de cada um.
#
# Para cada pavimento, são solicitados:
# - Altura piso a piso.
# - Espessura da laje.
#
# A altura piso a teto é calculada automaticamente:
#
# piso_teto = piso_piso - laje
#
# Os dados são armazenados em uma lista de dicionários.
# Cada dicionário representa um pavimento.

def ler_manual():

    pavimentos = []

    print("\n=== QUANTIDADE DE PAVIMENTOS ===")

    # Solicita a quantidade de pavimentos.
    # O limite permitido é de 1 a 26, incluindo o térreo.

    while True:

        try:

            quantidade = int(
                input(
                    "Quantos pavimentos, incluindo o terreo? "
                )
            )

            if 1 <= quantidade <= 26:
                break

            print(
                "Digite uma quantidade entre 1 e 26."
            )

        except ValueError:

            print(
                "Digite um numero inteiro valido."
            )

    # Percorre todos os pavimentos informados.
    for i in range(quantidade):

        # Define automaticamente o nome do pavimento.
        if i == 0:
            nome = "TERREO"
        else:
            nome = f"{i}o PAVIMENTO"

        print(f"\n=== {nome} ===")

        # Solicita as medidas até que sejam válidas.
        while True:

            try:

                # Recebe a altura entre dois pisos.
                piso_piso = float(
                    input(
                        "Altura piso a piso (mm): "
                    )
                )

                # Recebe a espessura da laje.
                laje = float(
                    input(
                        "Espessura da laje (mm): "
                    )
                )

                # Calcula automaticamente a altura piso a teto.
                piso_teto = piso_piso - laje

                # Verifica se as medidas são positivas.
                if piso_piso <= 0 or laje <= 0:

                    print(
                        "As medidas devem ser positivas."
                    )

                    continue

                # Verifica se existe altura útil entre o piso e o teto.
                if piso_teto <= 0:

                    print(
                        "A altura piso a piso deve ser maior "
                        "que a espessura da laje."
                    )

                    continue

                break

            except ValueError:

                print(
                    "Digite somente valores numericos."
                )

        # Armazena todas as informações do pavimento.
        pavimentos.append({

            "nome": nome,

            "piso_piso": piso_piso,

            "piso_teto": piso_teto,

            "laje": laje

        })

    return pavimentos


# ============================================================
# 10. FUNÇÃO PRINCIPAL DE DESENHO DOS PAVIMENTOS
# ============================================================
# Percorre a lista de pavimentos e desenha:
#
# 1. Linha do piso atual.
# 2. Linha do teto.
# 3. Linha do próximo piso.
# 4. Nome do pavimento.
# 5. Cota vertical escolhida.
# 6. Cota da espessura da laje.
#
# A cota vertical pode ser:
# modo_cota = "1": piso a piso.
# modo_cota = "2": piso a teto.
#
# A cota da laje é sempre desenhada.

def desenhar_pavimentos(pavimentos, modo_cota):

    # Define a altura inicial do desenho.
    y_atual = 0

    # Desenha a linha inicial do piso do térreo.
    desenhar_linha(
        0,
        y_atual,
        LARGURA,
        y_atual,
        "GEOMETRIA"
    )

    # Percorre individualmente cada pavimento.
    for pavimento in pavimentos:

        # Calcula as posições verticais do pavimento.
        piso_y, teto_y, proximo_piso_y = calcular_posicoes(
            y_atual,
            pavimento
        )

        # Desenha a linha do teto.
        desenhar_linha(
            0,
            teto_y,
            LARGURA,
            teto_y,
            "GEOMETRIA"
        )

        # Desenha a linha do próximo piso.
        desenhar_linha(
            0,
            proximo_piso_y,
            LARGURA,
            proximo_piso_y,
            "GEOMETRIA"
        )

        # Calcula o centro horizontal para posicionar o nome.
        meio_horizontal = LARGURA / 2

        # Escreve o nome do pavimento utilizando Liberation Sans.
        escrever_texto(
            pavimento["nome"],
            meio_horizontal,
            piso_y - ALTURA_TEXTO - 20,
            "TEXTOS",
            estilo=ESTILO_NOMES
        )

        # -----------------------------------------------
        # COTA VERTICAL ESCOLHIDA PELO USUÁRIO
        # -----------------------------------------------

        if modo_cota == "1":

            # Mede a distância entre dois pisos.
            desenhar_cota_vertical(
                piso_y,
                proximo_piso_y,
                X_COTA_ALTURA
            )

        elif modo_cota == "2":

            # Mede a distância entre piso e teto.
            desenhar_cota_vertical(
                piso_y,
                teto_y,
                X_COTA_ALTURA
            )

        # -----------------------------------------------
        # COTA DA ESPESSURA DA LAJE
        # -----------------------------------------------
        # Esta cota aparece independentemente da opção
        # escolhida para a cota vertical.

        desenhar_cota_vertical(
            teto_y,
            proximo_piso_y,
            X_COTA_LAJE
        )

        # Atualiza a altura inicial para o próximo pavimento.
        y_atual = proximo_piso_y

    # Escreve a identificação do topo do edifício.
    # Utiliza o mesmo estilo Liberation Sans dos pavimentos.

    escrever_texto(
        "TOPO DO EDIFICIO",
        LARGURA / 2,
        y_atual + 150,
        "TEXTOS",
        estilo=ESTILO_NOMES
    )


# ============================================================
# 11. FUNÇÃO PARA ESCOLHER O TIPO DE COTA
# ============================================================
# Apresenta as duas opções de cotagem vertical.
#
# A escolha é armazenada como texto:
# "1" = piso a piso.
# "2" = piso a teto.
#
# O programa só continua quando uma opção válida é escolhida.

def escolher_modo_cota():

    print("\n=== TIPO DE COTAGEM ===")

    print("1 - Piso a piso")
    print("2 - Piso a teto")

    while True:

        modo = input(
            "Escolha o tipo de cota: "
        ).strip()

        if modo in ("1", "2"):
            return modo

        print(
            "Opcao invalida. Digite 1 ou 2."
        )


# ============================================================
# 12. FUNÇÃO PRINCIPAL DO PROGRAMA
# ============================================================
# Controla a sequência de execução:
#
# 1. Apresenta o programa.
# 2. Solicita o tipo de cota.
# 3. Recebe as medidas dos pavimentos.
# 4. Executa os desenhos.
# 5. Define o caminho de salvamento.
# 6. Salva o arquivo DXF.
# 7. Exibe as informações do resultado.
#
# O arquivo será salvo na mesma pasta em que está este
# arquivo main.py, independentemente da pasta do terminal.

def main():

    print("\n================================")
    print("     GERADOR DE PAVIMENTOS CAD")
    print("================================")

    # Escolhe o tipo de cotagem vertical.
    modo_cota = escolher_modo_cota()

    # Recebe as medidas dos pavimentos.
    pavimentos = ler_manual()

    # Desenha todos os pavimentos no documento DXF.
    desenhar_pavimentos(
        pavimentos,
        modo_cota
    )

    # Identifica a pasta onde está o arquivo main.py.
    pasta_atual = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Junta a pasta com o nome do arquivo DXF.
    caminho_arquivo = os.path.join(
        pasta_atual,
        NOME_ARQUIVO
    )

    # Salva o documento DXF no endereço definido.
    doc.saveas(caminho_arquivo)

    # Apresenta um resumo da geração.
    print("\n================================")
    print("DESENHO GERADO COM SUCESSO!")
    print("================================")

    print(
        f"Pavimentos: {len(pavimentos)}"
    )

    if modo_cota == "1":

        print(
            "Cota vertical: Piso a piso"
        )

    else:

        print(
            "Cota vertical: Piso a teto"
        )

    print(
        "Cota da laje: Incluida"
    )

    print(
        f"\nArquivo salvo em:\n{caminho_arquivo}"
    )


# ============================================================
# 13. INÍCIO DA EXECUÇÃO
# ============================================================
# Esta condição verifica se o arquivo main.py foi executado
# diretamente.
#
# Caso tenha sido, chama a função main().
#
# O try/except captura erros durante a execução e apresenta
# a mensagem correspondente, evitando que o programa
# simplesmente feche sem mostrar o motivo do erro.

if __name__ == "__main__":

    try:

        main()

    except Exception as erro:

        print(
            f"\nOcorreu um erro: {erro}"
        )

    # Mantém o terminal aberto até o usuário pressionar Enter.
    input(
        "\nPressione Enter para fechar..."
    )
