import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime

id_item_selecionado = None

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estoque_local.db')


def inicializar_banco():
    with sqlite3.connect(DB_PATH) as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade REAL NOT NULL,
                unidade TEXT NOT NULL,
                validade TEXT NOT NULL
            )
        ''')
        conexao.commit()



def atualizar_tabela():
    for linha in tabela.get_children():
        tabela.delete(linha)

    try:
        data_hoje = datetime.now().date()
        with sqlite3.connect(DB_PATH) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, nome, quantidade, unidade, validade FROM ingredientes")
            linhas = cursor.fetchall()

        for linha in linhas:
            id_item, nome, quantidade, unidade, validade_banco = linha
            tag_status = "normal"
            data_exibicao = validade_banco  # Caso dê erro, mostra o que tá no banco

            try:
                data_validade = datetime.strptime(validade_banco, "%Y-%m-%d").date()

                data_exibicao = data_validade.strftime("%d/%m/%Y")

                if data_validade < data_hoje:
                    tag_status = "vencido"
            except ValueError:
                tag_status = "formato_invalido"

            linha_formatada = (id_item, nome, quantidade, unidade, data_exibicao)
            tabela.insert("", tk.END, values=linha_formatada, tags=(tag_status,))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao consultar o estoque: {e}")



def carregar_item_selecionado(event):
    global id_item_selecionado
    item_focado = tabela.focus()
    if not item_focado:
        return

    valores = tabela.item(item_focado, 'values')
    if valores:
        id_item_selecionado = valores[0]
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, valores[1])
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, valores[2])
        combo_unidade.set(valores[3])

        # O valor que vem da tabela já está em DD/MM/AAAA, colocamos direto no campo
        entry_validade.delete(0, tk.END)
        entry_validade.insert(0, valores[4])

        btn_salvar.config(state="disabled")
        btn_editar.config(state="normal")
        btn_excluir.config(state="normal")


def atualizar_ingrediente():
    global id_item_selecionado

    if id_item_selecionado is None:
        messagebox.showwarning("Aviso", "Nenhum item selecionado para alterar!")
        return

    nome = entry_nome.get()
    quantidade = entry_qtd.get()
    unidade = combo_unidade.get()
    validade_tela = entry_validade.get()

    if not nome or not quantidade or not validade_tela:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
        return

    try:
        data_objeto = datetime.strptime(validade_tela, "%d/%m/%Y").date()
        validade_banco = data_objeto.strftime("%Y-%m-%d")

        qtd_float = float(quantidade.replace(',', '.'))
        if qtd_float < 0:
            messagebox.showwarning("Aviso", "A quantidade não pode ser negativa!")
            return

        with sqlite3.connect(DB_PATH) as conexao:
            cursor = conexao.cursor()
            cursor.execute('''
                UPDATE ingredientes
                SET nome = ?, quantidade = ?, unidade = ?, validade = ?
                WHERE id = ?
            ''', (nome, qtd_float, unidade, validade_banco, id_item_selecionado))
            conexao.commit()

        messagebox.showinfo("Sucesso", "Ingrediente atualizado com sucesso!")
        limpar_formulario()
        atualizar_tabela()

    except ValueError:
        messagebox.showerror("Formatos Inválidos", "Verifique os campos:\n- Quantidade deve ser número.\n- Data deve ser DD/MM/AAAA.")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")

def salvar_ingrediente():
    nome = entry_nome.get()
    quantidade = entry_qtd.get()
    unidade = combo_unidade.get()
    validade_tela = entry_validade.get()

    if not nome or not quantidade or not validade_tela:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
        return

    try:
        # CONVERSÃO: Pega o DD/MM/AAAA da tela e transforma em AAAA-MM-DD para o banco
        data_objeto = datetime.strptime(validade_tela, "%d/%m/%Y").date()
        validade_banco = data_objeto.strftime("%Y-%m-%d")

        qtd_float = float(quantidade.replace(',', '.'))
        if qtd_float < 0:
            messagebox.showwarning("Aviso", "A quantidade não pode ser negativa!")
            return

        with sqlite3.connect(DB_PATH) as conexao:
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO ingredientes (nome, quantidade, unidade, validade)
                VALUES (?, ?, ?, ?)
            ''', (nome, qtd_float, unidade, validade_banco))
            conexao.commit()

        messagebox.showinfo("Sucesso", "Ingrediente cadastrado com sucesso!")
        limpar_formulario()
        atualizar_tabela()

    except ValueError:
        messagebox.showerror("Formatos Inválidos", "Verifique os campos:\n- Quantidade deve ser número.\n- Data deve ser DD/MM/AAAA.")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")

def excluir_ingrediente():
    global id_item_selecionado
    if id_item_selecionado is None:
        return
    resposta = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o item ID {id_item_selecionado}?")
    if resposta:
        try:
            with sqlite3.connect(DB_PATH) as conexao:
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM ingredientes WHERE id = ?", (id_item_selecionado,))
                conexao.commit()
            messagebox.showinfo("Sucesso", "Ingrediente excluído com sucesso!")
            limpar_formulario()
            atualizar_tabela()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")


def limpar_formulario():
    global id_item_selecionado
    id_item_selecionado = None
    entry_nome.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)
    entry_validade.delete(0, tk.END)
    combo_unidade.current(0)
    btn_salvar.config(state="normal")
    btn_editar.config(state="disabled")
    btn_excluir.config(state="disabled")

inicializar_banco()

janela = tk.Tk()
janela.title("Sistema de Controle de Estoque para Pequenos Negócios Alimentícios")
janela.geometry("580x600")

lbl_titulo_cad = tk.Label(janela, text="FORMULÁRIO (CADASTRO / EDIÇÃO)", font=("Arial", 10, "bold"))
lbl_titulo_cad.pack(pady=10)

lbl_nome = tk.Label(janela, text="Nome do Insumo:")
lbl_nome.pack()
entry_nome = tk.Entry(janela, width=40)
entry_nome.pack()

lbl_qtd = tk.Label(janela, text="Quantidade:")
lbl_qtd.pack(pady=(5, 0))
entry_qtd = tk.Entry(janela, width=40)
entry_qtd.pack()

lbl_unidade = tk.Label(janela, text="Unidade de Medida:")
lbl_unidade.pack(pady=(5, 0))
# state="readonly" impede que o usuário digite valores fora da lista (ex: "Kg", "quilo", etc.)
combo_unidade = ttk.Combobox(janela, values=["g", "kg", "un"], width=37, state="readonly")
combo_unidade.current(0)
combo_unidade.pack()

lbl_validade = tk.Label(janela, text="Data de Validade (DD/MM/AAAA):")
lbl_validade.pack(pady=(5, 0))
entry_validade = tk.Entry(janela, width=40)
entry_validade.pack()

frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=15)

btn_salvar = tk.Button(frame_botoes, text="Cadastrar", command=salvar_ingrediente, bg="#4CAF50", fg="white", width=11)
btn_salvar.pack(side="left", padx=3)

btn_editar = tk.Button(frame_botoes, text="Alterar", command=atualizar_ingrediente, bg="#2196F3", fg="white", width=11, state="disabled")
btn_editar.pack(side="left", padx=3)

btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir_ingrediente, bg="#F44336", fg="white", width=11, state="disabled")
btn_excluir.pack(side="left", padx=3)

btn_Limpar = tk.Button(frame_botoes, text="Cancelar", command=limpar_formulario, bg="#9E9E9E", fg="white", width=10)
btn_Limpar.pack(side="left", padx=3)

divisor = ttk.Separator(janela, orient='horizontal')
divisor.pack(fill='x', padx=10, pady=5)

lbl_titulo_con = tk.Label(janela, text="ESTOQUE ATUAL (Vermelho = Vencido)", font=("Arial", 10, "italic"))
lbl_titulo_con.pack(pady=5)

colunas = ("ID", "Nome", "Quantidade", "Unidade", "Validade")
tabela = ttk.Treeview(janela, columns=colunas, show="headings", height=8)

tabela.heading("ID", text="ID")
tabela.heading("Nome", text="Nome do Insumo")
tabela.heading("Quantidade", text="Qtd.")
tabela.heading("Unidade", text="Un.")
tabela.heading("Validade", text="Validade")

tabela.column("ID", width=40, anchor="center")
tabela.column("Nome", width=150)
tabela.column("Quantidade", width=80, anchor="center")
tabela.column("Unidade", width=60, anchor="center")
tabela.column("Validade", width=120, anchor="center")

tabela.pack(padx=10, pady=5, fill="both", expand=True)

tabela.tag_configure("normal", background="#FFFFFF", foreground="#000000")
tabela.tag_configure("vencido", background="#FFCDD2", foreground="#B71C1C")
tabela.tag_configure("formato_invalido", background="#FFE0B2", foreground="#E65100")

tabela.bind("<ButtonRelease-1>", carregar_item_selecionado)

atualizar_tabela()
janela.mainloop()
