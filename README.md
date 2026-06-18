# 🎵 Spotify Rewind

Transforme seu histórico do Spotify em análises interativas e visualizações ricas. O **Spotify Rewind** é uma aplicação desktop construída com [Streamlit](https://streamlit.io/) que processa o seu *Spotify Extended Streaming History* localmente, sem enviar nenhum dado para servidores externos.

> **Privacidade em primeiro lugar:** todo o processamento acontece no seu computador. Seus dados nunca saem da sua máquina.

---

## ✨ Funcionalidades

A aplicação organiza as análises em oito abas:

| Aba | Descrição |
| --- | --- |
| 📊 **Visão Geral** | Métricas globais, resumo por ano, distribuição por hora e dia da semana, heatmap e principais destaques |
| 📈 **Tendências** | Comparação mensal entre anos, heatmap temporal e evolução dos artistas ao longo do tempo |
| 🎵 **Músicas** | Top músicas (por plays ou minutos) e busca detalhada por música/artista |
| 👤 **Artistas** | Top artistas, nuvem de palavras (WordCloud) e evolução anual |
| 🔄 **Sessões** | Análise de sessões de escuta (agrupamentos de streams consecutivos) |
| 📱 **Plataforma** | Distribuição por dispositivo e país de conexão |
| ✨ **Análises Avançadas** | WordCloud, Heatmap, Sunburst, Treemap, Ranking, Evolução Mensal, Rede de Artistas e Bar Chart Race |
| ℹ️ **Sobre** | Informações sobre o projeto, privacidade e stack técnica |

---

## 🚀 Como Usar

### 1. Obtenha seus dados do Spotify

1. Acesse [Spotify Privacy Settings](https://www.spotify.com/br/account/privacy/)
2. Na seção de privacidade, solicite o **"Spotify Extended Streaming History"**
3. Aguarde o e-mail do Spotify (pode levar alguns dias) com o link de download
4. Baixe o arquivo **ZIP** recebido

A aplicação também aceita o ZIP do **"Account Data"** (que contém arquivos `StreamingHistory*.json`), além do formato estendido (`Streaming_History_Audio_*.json`).

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a aplicação

```bash
streamlit run app/main.py
```

A aplicação abrirá automaticamente no navegador (geralmente em `http://localhost:8501`).

### 4. Faça o upload e explore

Na tela inicial, faça o upload do seu arquivo ZIP. As análises serão geradas automaticamente. Use a barra lateral para filtrar por ano, artista, ajustar o número de itens nos rankings ou carregar outro arquivo.

---

## 🗂️ Estrutura do Projeto

```
Spotify-Rewind-App/
├── .streamlit/              # Configurações do Streamlit (tema, servidor)
├── app/
│   ├── main.py              # Orquestrador principal (define as abas e o fluxo)
│   ├── config.py            # Configurações: cores, tabs, DEV_MODE, CSS
│   └── components/
│       ├── ui.py            # Componentes de interface (header, upload, sidebar, footer)
│       ├── charts.py        # Gráficos principais (Plotly)
│       └── advanced_charts.py  # Visualizações avançadas (Sunburst, Treemap, Race, Rede...)
├── src/
│   ├── data_loader.py       # Carregamento e parse do ZIP/JSONs
│   └── data_processor.py    # Filtros, estatísticas e agregações
├── clear_cache.bat          # Utilitário para limpar o cache do Python (Windows)
├── requirements.txt         # Dependências do projeto
├── SETUP_AVANCADO.md         # Guia de integração das visualizações avançadas
└── README.md                # Este arquivo
```

---

## ⚙️ Configuração

As principais opções ficam em `app/config.py`:

- **`DEV_MODE`** — Quando `True`, a aplicação carrega dados de uma pasta local automaticamente (útil para desenvolvimento), pulando o upload. Quando `False` (padrão), exibe a tela de upload para o usuário.
- **`DEV_DATA_PATH`** — Caminho da pasta local usada quando `DEV_MODE = True`.
- **`COLORS`** — Paleta de cores inspirada no tema do Spotify.
- **`DEFAULT_TOP_N`** — Número padrão de itens exibidos nos rankings.

---

## 🛠️ Stack Técnica

- **[Streamlit](https://streamlit.io/)** — Framework da interface web
- **[Pandas](https://pandas.pydata.org/)** / **[NumPy](https://numpy.org/)** — Processamento e análise de dados
- **[Plotly](https://plotly.com/python/)** — Gráficos interativos
- **[Matplotlib](https://matplotlib.org/)** + **[WordCloud](https://github.com/amueller/word_cloud)** — Nuvem de palavras
- **[PyVis](https://pyvis.readthedocs.io/)** + **[NetworkX](https://networkx.org/)** — Rede de artistas

---

## 🔒 Privacidade

Seus dados **não saem do seu computador**. Todo o processamento (parse do ZIP, agregações e visualizações) é executado localmente. Nenhuma informação é enviada para servidores externos.

---

## 💡 Solução de Problemas

**Erro de importação (`ImportError`) após editar arquivos:**
Limpe o cache do Python. No Windows, execute o utilitário incluído:

```bash
clear_cache.bat
```

Ou manualmente (PowerShell):

```powershell
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

**A Rede de Artistas não aparece:**
Certifique-se de que as dependências opcionais estão instaladas:

```bash
pip install pyvis networkx
```

**Nenhum dado é encontrado no ZIP:**
Verifique se o arquivo contém os JSONs `Streaming_History_Audio_*.json` (Extended Streaming History) ou `StreamingHistory*.json` (Account Data).

---

## 📄 Licença

Projeto de uso pessoal para análise do próprio histórico do Spotify.

> Versão 1.0 — Aplicação modular para análise do Spotify Extended Streaming History.
