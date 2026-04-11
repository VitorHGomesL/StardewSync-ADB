# StardewSync-ADB 🚜📱

**StardewSync-ADB** é uma ferramenta de automação desenvolvida em Python para sincronizar saves do jogo *Stardew Valley* entre o PC (Windows) e dispositivos Android. Utilizando o protocolo ADB (Android Debug Bridge), o projeto elimina a fricção da transferência manual e resolve limitações comuns de sistemas de arquivos.

---

## 📋 1. O Problema

Jogadores de Stardew Valley que utilizam as plataformas PC e Android frequentemente enfrentam dificuldades para manter o progresso sincronizado:
- **Transferência Manual Ineficiente:** Depender do Windows Explorer e do protocolo MTP (Media Transfer Protocol) é lento e instável.
- **Risco de Perda de Dados:** É fácil sobrescrever um save mais novo por um antigo acidentalmente.
- **Limitações de Hardware:** Versões recentes do Android (14+) impõem restrições de acesso a pastas `/Android/data`, dificultando a cópia direta de arquivos via interface visual do Windows.

---

## ⚙️ 2. Descrições Técnicas

O projeto foi construído utilizando as seguintes tecnologias e conceitos de **Análise e Desenvolvimento de Sistemas (ADS)**:

* **Linguagem:** Python 3.10+
* **Comunicação Android:** Protocolo **ADB (Android Debug Bridge)** via comandos shell para bypass de restrições de interface.
* **Gerenciamento de Arquivos:** Bibliotecas `pathlib` (para manipulação de caminhos dinâmicos) e `shutil` (para operações de I/O de alto nível).
* **Deep Scan (Varredura em Profundidade):** Implementação de busca recursiva via `rglob` para detectar alterações em subdiretórios, contornando a falha do Windows que não atualiza o timestamp da pasta raiz.
* **Watchdog Pattern:** Algoritmo de monitoramento contínuo (polling) que observa o estado do sistema e reage a eventos de salvamento em tempo real.

---

## 🚀 3. Como o Programa Resolve o Problema

O **StardewSync-ADB** atua como uma ponte inteligente (bridge) entre os dispositivos:

1.  **Detecção Ativa:** O script monitora a conexão USB. Assim que o celular é reconhecido via ADB, ele inicia a rotina.
2.  **Sincronia Inteligente:** No início, o programa compara os timestamps (data/hora) do save no PC e no Celular. Ele move automaticamente a versão mais recente para o dispositivo que estiver desatualizado.
3.  **Monitoramento em Tempo Real:** Enquanto o usuário joga no PC, o script vigia qualquer novo salvamento. Ao salvar o jogo (dormir no jogo), o script detecta a alteração, gera um backup de segurança local e faz o *push* imediato para o Android.
4.  **Segurança (Fail-safe):** Antes de qualquer transferência, uma cópia de segurança é criada na pasta `SAVES_TESTS`, garantindo que o usuário nunca perca seu progresso em caso de falha física (cabo desconectado).

---

## 🤖 4. Relatório de Uso de IA (AI-Assisted Development)

> **Nota:** Este relatório foi gerado pela IA (Gemini 3 Flash) para descrever o processo de colaboração.

Este projeto foi desenvolvido em um modelo de **Pair Programming** entre o desenvolvedor e a IA. A colaboração ocorreu da seguinte forma:

-   **Arquitetura e Lógica:** A IA atuou como mentora, sugerindo a transição do protocolo instável MTP para o ADB, aumentando a confiabilidade do sistema.
-   **Debugging de Hardware:** Auxílio na identificação de bloqueios de segurança específicos (como o *Samsung Auto Blocker* e restrições da *One UI 6*).
-   **Refatoração Profissional:** A IA auxiliou na transformação de comentários básicos em documentações técnicas (`Docstrings`), elevando o nível do código para padrões de mercado.
-   **Teste de Mesa:** Simulações lógicas realizadas pela IA para prever erros de execução antes mesmo do código rodar fisicamente (como o tratamento de parênteses em chamadas de funções).

---

## 🛠️ 5. Como Configurar

Para utilizar este projeto, você precisará de:

1.  **ADB Instalado:** Baixe o [Platform-Tools do Google](https://developer.android.com/tools/releases/platform-tools).
2.  **Depuração USB Ativada:** No seu Android, ative as Opções do Desenvolvedor e ligue a "Depuração USB".
3.  **Samsung Auto Blocker (Opcional):** Se usar Samsung com Android 14, desative o "Bloqueador Automático" em Segurança e Privacidade.

**Execução:**
Salve o script `main.py` na mesma pasta do `adb.exe` e execute:
```bash
python main.py