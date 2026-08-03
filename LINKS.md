# 🔗 Links do Projeto — CEASA Market Monitor

> Guardados em **03/08/2026** para acesso rápido amanhã.

## Dashboard publicado (GitHub Pages)

- **https://athenas1200.github.io/ceasa-market-monitor/**

## Repositório GitHub

- **https://github.com/athenas1200/ceasa-market-monitor**

## Fonte de dados (scraping)

- Cotações CEASA Agrolink: **https://www.agrolink.com.br/cotacoes/ceasa/**
- Exemplo de produto (mamão): **https://www.agrolink.com.br/cotacoes/ceasa/frutas/mamao/**
- Paginação: `?pagina=N` (30 registros/página; frutas=208 págs, hortaliças=167 págs)

## Local (máquina)

- Projeto: `C:\Users\vasco\Downloads\agro`
- Scraper: `python scraper_ceasa_completo.py` (~5 min, gera CSV + JSON)
- Preview local: `python -m http.server 8000` → `http://localhost:8000`

## Para atualizar os dados manualmente

```powershell
cd C:\Users\vasco\Downloads\agro
python scraper_ceasa_completo.py
git add ceasa_dashboard.json ceasa_todos.csv
git commit -m "update dados CEASA"
git push
```

Ou aguardar o GitHub Actions (todo dia 08:20 UTC) que já comita e publica sozinho.

## Credenciais / token GitHub

- Token OAuth do GitHub já salvo no Windows Credential Manager (`git credential fill`).
- Conta: `athenas1200` / `Athenas1200@gmail.com`
