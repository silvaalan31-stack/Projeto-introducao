#!/usr/bin/env python3
"""Cadastro demonstrativo em memória para o projeto acadêmico Espaço Santa Maria.

Use apenas dados fictícios. Os registros não são persistidos entre execuções.
"""

import unicodedata


pacientes = []


def normalizar(texto):
    """Normaliza texto para busca sem diferenciar acentos ou maiúsculas."""
    texto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


def ler_texto(mensagem, campo):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print(f"{campo} não pode ficar vazio. Tente novamente.")


def cadastrar_paciente():
    print("\n--- Cadastro de paciente ---")
    nome = ler_texto("Nome: ", "O nome")

    while True:
        entrada = input("Idade (0 a 120): ").strip()
        try:
            idade = int(entrada)
            if 0 <= idade <= 120:
                break
            print("A idade deve estar entre 0 e 120 anos.")
        except ValueError:
            print("Idade inválida. Digite um número inteiro.")

    telefone = ler_texto("Telefone: ", "O telefone")
    paciente = {"nome": nome, "idade": idade, "telefone": telefone}
    pacientes.append(paciente)
    print(f"\nPaciente {nome} cadastrado com sucesso.\n")


def ver_estatisticas():
    print("\n--- Estatísticas ---")
    if not pacientes:
        print("Ainda não há pacientes cadastrados.\n")
        return

    total = len(pacientes)
    idade_media = sum(paciente["idade"] for paciente in pacientes) / total
    mais_novo = min(pacientes, key=lambda paciente: paciente["idade"])
    mais_velho = max(pacientes, key=lambda paciente: paciente["idade"])

    print(f"Total cadastrado: {total}")
    print(f"Idade média: {idade_media:.1f} anos")
    print(f"Paciente mais novo: {mais_novo['nome']} ({mais_novo['idade']} anos)")
    print(f"Paciente mais velho: {mais_velho['nome']} ({mais_velho['idade']} anos)\n")


def buscar_paciente():
    print("\n--- Buscar paciente ---")
    if not pacientes:
        print("Ainda não há pacientes cadastrados.\n")
        return

    busca = ler_texto("Digite o nome ou parte do nome: ", "A busca")
    termo = normalizar(busca)
    encontrados = [p for p in pacientes if termo in normalizar(p["nome"])]

    if not encontrados:
        print(f"Nenhum paciente encontrado com o nome '{busca}'.\n")
        return

    print(f"\n{len(encontrados)} paciente(s) encontrado(s):")
    for paciente in encontrados:
        print(f"- {paciente['nome']} | {paciente['idade']} anos | Telefone: {paciente['telefone']}")
    print()


def listar_pacientes():
    print("\n--- Pacientes cadastrados ---")
    if not pacientes:
        print("Ainda não há pacientes cadastrados.\n")
        return

    for numero, paciente in enumerate(pacientes, start=1):
        print(f"{numero}. {paciente['nome']} | {paciente['idade']} anos | Telefone: {paciente['telefone']}")
    print()


def menu():
    print("=" * 46)
    print(" ESPAÇO SANTA MARIA — CADASTRO DEMONSTRATIVO")
    print("       Seu tratamento, nossa alegria")
    print("=" * 46)
    while True:
        print("1. Cadastrar paciente")
        print("2. Ver estatísticas")
        print("3. Buscar paciente pelo nome")
        print("4. Listar todos os pacientes")
        print("5. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            cadastrar_paciente()
        elif escolha == "2":
            ver_estatisticas()
        elif escolha == "3":
            buscar_paciente()
        elif escolha == "4":
            listar_pacientes()
        elif escolha == "5":
            print("Programa encerrado. Até logo!\n")
            break
        else:
            print("Opção inválida. Escolha um número de 1 a 5.\n")


if __name__ == "__main__":
    try:
        menu()
    except (EOFError, KeyboardInterrupt):
        print("\n\nExecução encerrada pelo usuário.")
