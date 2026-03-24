from tinydb import TinyDB, where
import streamlit as st

#criar o banco de dados

db = TinyDB("loja.json")

#criar tabela de vendas dentro do db
estoque = db.table("Estoque")
vendas =  db.table("Vendas")

#configurações da página
#titulo, icone e layout
st.set_page_config(
    page_title="Sistema de loja",
    page_icon="🏬",
    layout="wide")

#título exibido dentro da página

st.title("🏬Sistema loja V1")

aba_estoque, aba_cadastro, aba_venda, aba_vendas = st.tabs([
    "📦Estoque",
    "➕Cadastrar produto",
    "🛒Vender produto",
    "📊Vendas"])

#aba cadastrar produto

with aba_cadastro:
    st.header("Cadastrar novo Produto")

    id_produto = st.number_input(
    "ID do produto:",
        min_value=1,
        step=1,
        key="cad_id")
    nome_produto = st.text_input(
    "Nome do produto:",
            key="cad_nome"
    )

    preco_produto = st.number_input(
        "Preço (R$):",
        min_value=0.0,
        step=0.5,
        key="cad_preco",
        format="%.2f"

        )

    qtd_produto = st.number_input(
        "Quantidade em estoque",
        min_value=1,
        step=1,
        key="cad_qtd"
    )

    #botão de cadastrar

    if st.button("Cadastrar produto",type="primary"):
        #validação 1: nome vazio
        if nome_produto.strip() == "":
            st.error("Digite o nome do produto!")

        #inserir no db (banco de dados)
        else:
            estoque.insert({
                "id": int(id_produto),
                "nome": nome_produto.strip(),
                "preco": float(preco_produto),
                "qtd": int(qtd_produto)
            })
            st.success(f"Produto '{nome_produto}' cadastrado com sucesso")

with aba_estoque:
    st.header("Estoque atual")

    #pegar todos os produtos da tabela estoque e colocar na variavel produtos
    produtos =  estoque.all()

    if len(produtos) == 0:
        st.info("Estoque vazio! cadastre produtos na aba ao lado!")
    else:
        tabela = []
        for produto in produtos:
            tabela.append({
                "ID": produto['id'],
                "Nome": produto['nome'],
                "Preço (R$)": produto['preco'],
                "Quantidade": produto['qtd']
            })

        st.table(tabela)

        st.metric("Quantidade de produtos cadastrados ", len(produtos))

with aba_venda:
    st.header("Registrar venda")

    #carregar todos os produtos da tabela estoque para produtos
    produtos = estoque.all()


    #validar se tem produtos no estoque
    if len(produtos) == 0:
        st.info("Nenhum produto em estoque para vender.")

    else:
        opcoes = ["Selecione um produto..."]

        mapa_produtos = {}

        #percorrer os produtos

        for produto in produtos:
                if produto['qtd'] > 0:
                    label = f"#ID: {produto['id']} - Nome: {produto['nome']} - (estoque: {produto['qtd']})"
                    opcoes.append(label)
                    mapa_produtos[label] = produto

        produto_escolhido = st.selectbox("Produto:", opcoes, key="venda_produto")

        if produto_escolhido != "Selecione um produto...":
            produto = mapa_produtos[produto_escolhido]

            #quantidade que o cliente quer comprar
            qtd_venda = st.number_input(
                "Quantidade:",
                min_value=1,
                max_value=produto['qtd'],
                step=1,
                key="venda_qtd")

            cliente = st.text_input(
                "Nome do cliente: ",
                    key="venda_cliente")

            #Calcular valor total da venda
            total = produto['preco'] * qtd_venda

            st.info(f"Total da venda: R$ {total}")

            if st.button("Confirmar venda", type="primary"):
                if cliente.strip() == "":
                    st.error("Digite o nome do cliente!")
                else:
                    #registrar venda no DB
                    vendas.insert(
                        {
                            "id_produto": produto['id'],
                            "nome_produto": produto['nome'],
                            "qtd_venda": int(qtd_venda),
                            "preco_unit": produto['preco'],
                            "total": total,
                            "cliente": cliente.strip()
                        }
                    )

                    estoque.update(
                        {"qtd": produto["qtd"] - int(qtd_venda)},
                        where("id") == produto["id"]
                    )

                    st.success(f"Venda registrada! Total: R$ {total}")
                    st.balloons()


with aba_vendas:
    st.header("Vendas")
    dados = db.table("Vendas").all()  # busca direto pelo banco, sem depender da variável

    if len(dados) == 0:
        st.info("Nenhuma venda registrada ainda.")
    else:
        vendas_tabela = []
        for v in dados:
            vendas_tabela.append({
                "Cliente": v['cliente'],
                "Produto": v['nome_produto'],
                "Qtd": v['qtd_venda'],
                "Preço Unit.": f"R$ {v['preco_unit']:.2f}",
                "Total": f"R$ {v['total']:.2f}"
            })
        st.table(vendas_tabela)
        st.metric("Total de vendas", len(dados))