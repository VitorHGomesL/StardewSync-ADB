# StardewSync-ADB 🌱📱

**StardewSync-ADB** é uma ferramenta em Python para auxiliar a sincronização de saves do *Stardew Valley* entre o computador e um dispositivo Android usando **ADB**.

> Status atual: a **CLI está funcionando** com painel visual em tempo real, detecção de caminhos, detecção do Android via ADB e mudança visual de status. A **sincronização automática ainda não foi reativada** nesta versão.

---

## Status da versão atual

Esta versão está focada na base da CLI e na preparação do fluxo de configuração.

### Funcionando

- CLI com comandos via **Typer**.
- Interface visual com **Rich**.
- Painel fixo no terminal usando `Live`.
- Status do Android mudando visualmente:
  - vermelho quando desconectado;
  - verde quando conectado.
- Leitura de caminhos salvos em `caminhos.json`.
- Configuração de caminho do save do PC e pasta de backup.
- Detecção do ADB instalado no sistema via `shutil.which("adb")`.
- Fallback para ADB local dentro da pasta `platform-tools/`.
- Detecção do diretório de saves do Android via ADB.

### Ainda não reativado

- Sincronização automática PC ↔ Android.
- Watchdog de alterações de save.
- Push automático do PC para o Android.
- Pull automático do Android para o PC durante o fluxo principal.
- Backup automático antes da sincronização.

As funções relacionadas à sincronização ainda existem no código, mas o fluxo principal da CLI está temporariamente focado na interface e nas detecções.

---

## Objetivo do projeto

O projeto busca reduzir o trabalho manual de copiar saves do *Stardew Valley* entre PC e Android.

A ideia final é:

1. detectar o Android conectado;
2. identificar onde estão os saves do PC;
3. identificar onde estão os saves do Android;
4. comparar qual lado possui o save mais recente;
5. criar backup de segurança;
6. sincronizar a versão correta entre os dispositivos.

No momento, a versão atual cobre principalmente as etapas de **CLI, configuração e detecção**.

---

## Tecnologias usadas

- **Python 3**
- **Typer** para comandos de terminal
- **Rich** para interface visual no terminal
- **ADB** para comunicação com o Android
- **pathlib** para manipulação de caminhos
- **JSON** para persistência simples de configuração

---

## Requisitos

### Python

Recomenda-se usar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências usadas pelo projeto:

```bash
pip install typer rich
```

### ADB no Linux

No Linux Mint/Ubuntu:

```bash
sudo apt update
sudo apt install adb
```

Teste se o ADB foi instalado:

```bash
adb version
```

Teste se o Android foi reconhecido:

```bash
adb devices
```

No celular, ative:

```txt
Opções de desenvolvedor → Depuração USB
```

Ao conectar o cabo USB, aceite a permissão RSA no celular.

---

## Configuração

Antes de iniciar o painel, configure os caminhos:

```bash
python3 main.py config
```

Esse comando salva os caminhos em:

```txt
caminhos.json
```

O arquivo guarda:

```json
{
    "caminho_pc": "/caminho/para/saves/do/pc",
    "caminho_backup": "/caminho/para/backups"
}
```

---

## Uso da CLI

Ver ajuda:

```bash
python3 main.py --help
```

Configurar caminhos:

```bash
python3 main.py config
```

Iniciar painel da CLI:

```bash
python3 main.py iniciar
```

Ver caminhos configurados:

```bash
python3 main.py caminhos
```

Ver versão:

```bash
python3 main.py versao
```

---

## Comportamento atual da CLI

Ao executar:

```bash
python3 main.py iniciar
```

A aplicação abre um painel no terminal com:

- logo do StardewSyncADB;
- sistema atual ↔ Android;
- status do Android;
- status do diretório do PC;
- status da pasta de backup.

O status do Android muda automaticamente conforme a conexão:

```txt
Android: DESCONECTADO  → vermelho
Android: CONECTADO     → verde
```

A CLI não deve ficar imprimindo mensagens repetidas no terminal. O objetivo atual é manter uma tela fixa e atualizar apenas os estados visuais.

---

## Estrutura atual

```txt
StardewSync-ADB/
├── main.py
├── caminhos.json
├── src/
│   ├── __init__.py
│   ├── adb.py
│   ├── cli.py
│   ├── config.py
│   └── watchdog.py
└── README.md
```

Resumo dos arquivos principais:

```txt
main.py        → entrada da aplicação e comandos Typer
src/cli.py     → painel visual com Rich
src/config.py  → configuração, caminhos, JSON e backup
src/adb.py     → localização do ADB e comandos ADB
src/watchdog.py → monitoramento de alterações, ainda não reintegrado ao fluxo principal
```

---

## Observações importantes

A versão atual ainda está em desenvolvimento.

O foco neste momento é estabilizar:

1. CLI;
2. configuração;
3. detecção de ADB;
4. detecção de Android;
5. exibição correta de status.

A sincronização real será reativada depois que essa base estiver estável.

---

## Próximos passos

- Remover efeitos colaterais nos imports.
- Garantir que `--help` funcione mesmo sem configuração inicial.
- Melhorar tratamento quando `caminhos.json` não existir.
- Integrar mensagens de estado no painel Rich.
- Reativar `sincronia_inicial()` com segurança.
- Reativar backup antes de qualquer transferência.
- Reativar watchdog para detectar saves no PC.
- Substituir comandos ADB antigos por funções centralizadas em `src/adb.py`.

---

## Aviso sobre sincronização

Esta versão **não deve ser considerada pronta para sincronizar saves reais automaticamente**.

Use por enquanto para testar:

- CLI;
- configuração;
- reconhecimento de caminhos;
- detecção do Android;
- visualização do painel.

Antes de reativar a sincronização, é recomendado testar com uma pasta fake de saves e manter backup manual dos arquivos reais.
