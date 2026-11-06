# Espaço Santa Maria — Gestão de Consultas

Projeto acadêmico demonstrativo em português para praticar gestão ágil, Python, lógica proposicional, fila FIFO e diagrama UML. Marca: **Espaço Santa Maria**. Lema: **“Seu tratamento, nossa alegria”**.

## Arquivos

- `index.html`, `styles.css`, `app.js`: site estático interativo, sem etapa de compilação.
- `clinica_vida.py`: programa Python real de cadastro em terminal.
- `.nojekyll`: evita o processamento de arquivos pelo Jekyll no GitHub Pages.

## Abrir localmente

Para ver a página, abra `index.html` em um navegador. Se preferir servir por HTTP, entre nesta pasta no terminal e execute:

```bash
python3 -m http.server 8000
```

Depois visite `http://localhost:8000`.

Para executar o programa Python:

```bash
python3 clinica_vida.py
```

Requer Python 3. O script não utiliza dependências externas. Cadastros são mantidos apenas na memória até o programa ser encerrado.

## Publicar pelo GitHub Pages

1. Crie um repositório no GitHub (por exemplo, `espaco-santa-maria`).
2. Envie **todos** os arquivos desta pasta para a raiz do repositório, mantendo `.nojekyll`.
3. No GitHub, abra **Settings → Pages**.
4. Em **Build and deployment**, escolha **Deploy from a branch**; selecione a branch `main` e a pasta `/(root)`, e salve.
5. Aguarde a publicação. O endereço aparecerá na própria tela de configurações do Pages.

Este projeto não foi enviado a um repositório GitHub nem publicado automaticamente. Esses passos publicam os arquivos quando você os subir à sua conta.

## O que funciona no site

- Quadro com Backlog, Sprint Atual, Em Progresso e Concluído; seleção e edição de sprint; criação/edição/exclusão de tarefas; movimentação por arrastar ou pelo seletor de lista; checklists e comentários.
- Retrospectiva por sprint com contadores, campos editáveis, salvamento no `localStorage`, exportação Markdown e impressão/salvamento em PDF pelo navegador.
- Duas tabelas-verdade completas (16 combinações cada), análise do caso solicitado e exportação CSV.
- Pseudocódigo FIFO copiável e diagrama SVG de casos de uso com atores, limite do sistema e relações `<<include>>`.
- Navegação responsiva, impressão e download do arquivo Python.

Os dados demonstrativos do quadro ficam no armazenamento local do navegador. Limpar os dados do site no navegador remove essas alterações. O projeto não cria quadros no Trello real; o link do site abre o Trello para criação manual.

## Privacidade e escopo

Este é um exercício acadêmico: não é prontuário eletrônico, não tem servidor, banco de dados, login, conexão ao Trello ou controles de segurança clínica. **Não insira dados pessoais, CPFs reais, telefones reais ou informações médicas.** Exemplos de pacientes, nomes e CPFs são fictícios e servem apenas para ilustrar a atividade. O código Python também usa dados temporários, sem persistência.
