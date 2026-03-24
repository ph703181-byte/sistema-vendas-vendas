
import streamlit as st
from tinydb import TinyDB, where

## Criar o banco de dados
db = TinyDB("loja.json")

## Vamos criar uma tabela de estoque
## dentro do bd
estoque = db.table("estoque")
vendas = db.table("vendas")

## Configurações da página
## titulo, icone, layout

st.set_page_config(
    page_title="Sistema Loja",
    page_icon="🏪",
    layout="wide"
)

## Título exibido na página
st.title("🏪 Sistema Loja v1")

aba_estoque, aba_cadastro, aba_venda, aba_vendas = st.tabs([
    "📦 Estoque",
    "➕ Cadastrar Produto",
    "🛒 Vender Produto",
    "📊 Vendas"
])

### Aba Cadastrar Produto

with aba_cadastro:
    st.header("Cadastrar novo produto")

    id_produto = st.number_input(
        "ID do produto",
        min_value=1,
        step=1,
        key="cad_id"
    )

    nome_produto = st.text_input(
        "Nome do produto",
        key="cad_nome"
    )

    preco_produto = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        step=0.5,
        format="%.2f",
        key="cad_preco"
    )

    qtd_produto = st.number_input(
        "Quantidade em estoque",
        min_value=0,
        step=1,
        key="cad_qtd"
    )

    ## Botão de envio
    if st.button("Cadastrar Produto", type="primary"):

        # Validação 1: nome vazio
        if nome_produto.strip() == "":
            st.error("Digite o nome do produto!")
        else:
            # Insere no BD
            estoque.insert({
                "id": int(id_produto),
                "nome": nome_produto.strip(),
                "preco": float(preco_produto),
                "qtd": int(qtd_produto)
            })

            st.success(f"Produto {nome_produto} cadastrado com sucesso!")

with aba_estoque:
    st.header("Estoque atual")

    # Carregar todos os produtos da tabela
    # estoque na variavel produtos
    produtos = estoque.all()

    if len(produtos) == 0:
        st.info("Estoque vazio! Cadastre produtos na aba ao lado!")
    else:
        tabela = []

        # Percorrer (loop) a lista de produtos existentes no BD

        for produto in produtos:

            tabela.append({
                "ID": produto["id"],
                "Produto": produto["nome"],
                "Preço (R$)": f"{produto['preco']:.2f}",
                "Quantidade": produto["qtd"]
            })

        st.table(tabela)
        st.metric("Total de produtos cadastrados", len(produtos))

with aba_venda:
    st.header("Registrar venda")

    # Carregar todos os produtos da tabela estoque na lista produtos
    produtos = estoque.all()

    # Validar se tem produto no estoque
    if len(produtos) == 0:
        st.info("Nenhum produto em estoque para vender.")
    else:
        opcoes = ["Selecione um produto..."]

        mapa_produtos = {}

        # Percorrer os produtos

        for produto in produtos:
            if produto["qtd"] > 0:
                label = f"#{produto["id"]} - {produto["nome"]} (estoque: {produto['qtd']})"

                opcoes.append(label)
                mapa_produtos[label] = produto


        produto_escolhido = st.selectbox("Produto", opcoes, key="venda_prod")

        if produto_escolhido != "Selecione um produto...":
            produto = mapa_produtos[produto_escolhido]

            # Quantidade que o cliente quer comprar...
            qtd_venda = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=produto['qtd'],
                step=1,
                key="venda_qtd"
            )

            cliente = st.text_input(
                "Nome do cliente",
                key="venda_cliente"
            )

            # Calcular o valor total da venda
            total = produto['preco'] * qtd_venda

            st.info(f"Total da venda: R${total}")

            if st.button("Confirmar Venda", type="primary"):

                if cliente.strip() == "":
                    st.error("Digite o nome do cliente!")
                else:

                    # Registrar a venda no DB
                    vendas.insert({
                        "id_produto": produto["id"],
                        "produto_nome": produto["nome"],
                        "qtd_venda": int(qtd_venda),
                        "preco_unit": produto["preco"],
                        "total": total,
                        "cliente": cliente.strip()
                    })

                    estoque.update(
                        {"qtd": produto["qtd"] - int(qtd_venda)},
                        where("id") == produto["id"]
                    )

                    st.success(f"Venda registrada! Total: R$ {total}")

                    st.balloons()
