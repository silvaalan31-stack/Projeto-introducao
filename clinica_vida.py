#!/usr/bin/env python3
# Clínica Vida+ — cadastro demonstrativo de pacientes
# Execute com: python3 clinica_vida.py
from collections import deque

pacientes = []

def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Entrada inválida: o campo não pode ficar vazio.")

def ler_idade():
    while True:
        valor = input("Idade: ").strip()
        try:
            idade = int(valor)
            if 0 <= idade <= 120:
                return idade
            print("Informe uma idade entre 0 e 120.")
        except ValueError:
            print("Idade inválida. Digite um número inteiro.")

def cadastrar_paciente():
    print("\\n--- Cadastrar paciente ---")
    nome = ler_texto("Nome: ")
    idade = ler_idade()
    telefone = ler_texto("Telefone: ")
    pacientes.append({"nome": nome, "idade": idade, "telefone": telefone})
    print(f"Paciente '{nome}' cadastrado com sucesso.")

def ver_estatisticas():
    print("\\n--- Estatísticas ---")
    if not pacientes:
        print("Nenhum paciente cadastrado. Cadastre pacientes para ver as estatísticas.")
        return
    total = len(pacientes)
    media = sum(p["idade"] for p in pacientes) / total
    novo = min(pacientes, key=lambda p: p["idade"])
    velho = max(pacientes, key=lambda p: p["idade"])
    print(f"Total cadastrado: {total}")
    print(f"Idade média: {media:.1f} anos")
    print(f"Paciente mais novo: {novo['nome']} ({novo['idade']} anos)")
    print(f"Paciente mais velho: {velho['nome']} ({velho['idade']} anos)")

def buscar_paciente():
    print("\\n--- Buscar paciente ---")
    if not pacientes:
        print("A lista está vazia. Nenhum paciente para buscar.")
        return
    nome_busca = ler_texto("Digite o nome (busca parcial, sem diferenciar maiúsculas): ").casefold()
    encontrados = [p for p in pacientes if nome_busca in p["nome"].casefold()]
    if not encontrados:
        print("Nenhum paciente encontrado com esse nome.")
        return
    for p in encontrados:
        print(f"Nome: {p['nome']} | Idade: {p['idade']} | Telefone: {p['telefone']}")

def listar_pacientes():
    print("\\n--- Todos os pacientes ---")
    if not pacientes:
        print("Nenhum paciente cadastrado.")
        return
    for i, p in enumerate(pacientes, 1):
        print(f"{i}. {p['nome']} | {p['idade']} anos | Telefone: {p['telefone']}")

def main():
    while True:
        print("\\n========== CLÍNICA VIDA+ ==========")
        print("1. Cadastrar paciente")
        print("2. Ver estatísticas")
        print("3. Buscar paciente pelo nome")
        print("4. Listar todos os pacientes")
        print("5. Sair")
        opcao = input("Escolha uma opção (1-5): ").strip()
        if opcao == "1":
            cadastrar_paciente()
        elif opcao == "2":
            ver_estatisticas()
        elif opcao == "3":
            buscar_paciente()
        elif opcao == "4":
            listar_pacientes()
        elif opcao == "5":
            print("Programa encerrado. Obrigado por utilizar a Clínica Vida+.")
            break
        else:
            print("Opção inválida. Digite um número de 1 a 5.")

if __name__ == "__main__":
    main()
