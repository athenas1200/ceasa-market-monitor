# CEASA Market Monitor · Dashboard Hortifruti

Dashboard no estilo **Global Market Monitor** para cotações da CEASA (Frutas + Hortaliças),
com dados históricos raspados do [Agrolink](https://www.agrolink.com.br/cotacoes/ceasa/).

> Publicado no GitHub Pages: **https://athenas1200.github.io/ceasa-market-monitor/**

---

## O que o dashboard mostra

- **Ticker tape** contínuo com os maiores movimentos do dia
- **Cards de destaque**: maior alta, maior baixa, mais caro, mais barato
- **Seletor de data** — veja qualquer pregão (padrão: última data com cobertura completa)
- **Filtros**: estado, categoria (Frutas/Hortaliças), busca e "só altas"
- **Tabela ordenável** com 37 produtos (preço médio nacional, variação, mini sparkline da evolução)
- **Detalhe por estado** ao clicar em um produto (CEASA, preço e variação por UF)
- **Market breadth** (subiram / cairam / neutros + A/D ratio)
- **Mapa regional clicável** por estado
- **Gráfico de evolução** de preços por categoria
- **Top 5 altas / Top 5 baixas** do dia

## Arquivos

| Arquivo | Descrição |
|---|---|
| `index.html` | Dashboard (HTML/CSS/JS puro, sem dependências) |
| `ceasa_dashboard.json` | **Dados reais processados** consumidos pelo dashboard |
| `ceasa_todos.csv` | Registros brutos (11.226 cotações, 27 dias, 18 estados) |
| `ceasa_YYYY-MM-DD.csv` | Somente a última data |
| `scraper_ceasa_completo.py` | Scraper do Agrolink (gera tudo acima) |
| `.github/workflows/scrape.yml` | Atualização automática diária |

## Como rodar o scraper

```bash
pip install requests beautifulsoup4 pandas
python scraper_ceasa_completo.py          # frutas + hortaliças completas (~375 páginas, ~5 min)
python scraper_ceasa_completo.py --max-paginas 3   # teste rápido
```

Saída:

```
ceasa_todos.csv        -> registros brutos
ceasa_dashboard.json   -> dados do dashboard
ceasa_2026-08-03.csv   -> última data
```

Para publicar as atualizações no GitHub Pages basta rodar de novo e commitar o
`ceasa_dashboard.json` (ou deixar o workflow diário fazer isso).

## Ver localmente

Como o dashboard carrega o JSON via `fetch`, sirva a pasta por HTTP (não abra via `file://`):

```bash
python -m http.server 8000
# http://localhost:8000
```

## Estrutura do JSON

```jsonc
{
  "gerado_em": "2026-08-03T...",
  "fonte": "Agrolink",
  "ultima_data": "2026-08-03",
  "data_referencia": "2026-07-31",   // última data com cobertura completa
  "datas": ["2026-07-05", ...],
  "cobertura": { "2026-07-31": 556 },
  "series": [
    { "produto": "Mamão Formosa", "unidade": "1Kg", "categoria": "Frutas",
      "estado": "SP", "ceasa": "CEAGESP Ribeirão Preto(SP)",
      "precos": [["2026-07-05", 3.5], ...] }
  ],
  "historico": { "Frutas": [["05/07", 5.9], ...], "Hortaliças": [...] },
  "raw_count": 11226,
  "n_produtos": 37,
  "n_estados": 18
}
```

## Notas sobre os dados

- Fonte: [Agrolink — Cotações CEASA](https://www.agrolink.com.br/cotacoes/ceasa/)
- 37 produtos de catálogo × 18 estados, ~27 pregões por série
- CEASAs reportam em dias distintos — por isso as datas finais do mês podem ter
  cobertura "parcial" (marcadas no seletor de data)
- A variação compara o preço de cada produto/estado com a cota anterior disponível

## Licença

MIT — use, modifique e compartilhe à vontade.
