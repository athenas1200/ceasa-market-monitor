# 🔗 Links do Projeto — CEASA Market Monitor

> Guardados em **03/08/2026** para acesso rápido amanhã.

## Dashboard publicado (GitHub Pages)

- **https://athenas1200.github.io/ceasa-market-monitor/**
- Versão no dre_demo (menu "Preços CEASA"): **https://consultoriasoft.com.br/dre_demo/ceasa.html**

## Repositório GitHub

- **https://github.com/athenas1200/ceasa-market-monitor**

## Banco de dados (VPS) — histórico diário

- Banco: **MySQL** `agnaldon_nordeste` → tabela **`ceasa_cotacoes`**
  (produto, unidade, categoria, estado, local_text, preco, data, fonte) — chave única
  (produto, unidade, estado, data, fonte) → INSERT IGNORE
- Script diário: **`/opt/scraper_diario.py`** (raspa CEASA frutas+hortaliças e Café,
  decodifica preço de café do sprite com tesseract + template matching, grava no banco
  e regenera o `ceasa_dashboard.json` do dre_demo)
- Cron: **05:30 todo dia** → `bash /opt/rodar_ceasa.sh` (log em `/var/log/ceasa_diario.log`)
- Arquivo de templates do café: `/opt/cafe_templates.json` (28 preços decodificados;
  se o preço do dia não bater em nenhum template, o registro é pulado — atualizar
  rodando o script de decode e regenerando o template)
- MySQL: user `agnaldon_nordeste` / senha em `sincronizar_db.php` do dre_demo

## Fonte de dados (scraping)

- Cotações CEASA Agrolink: **https://www.agrolink.com.br/cotacoes/ceasa/**
- Café (grãos): **https://www.agrolink.com.br/cotacoes/graos/cafe/** — preço em sprite
  (P-AMMCYG fonte normal / C-OUXLYO fonte 7-segmentos), decodificado via tesseract + templates
- Paginação: `?pagina=N` (30 registros/página; frutas=208 págs, hortaliças=167 págs)

## Ordem fixada no dashboard

- **Café → Mamão → Maracujá → Pimenta → resto** (const `PIN_ORDEM` no index.html;
  "pimenta do reino" não existe no Agrolink — sem dados)

## Local (máquina)

- Projeto: `C:\Users\vasco\Downloads\agro`
- Scraper completo: `python scraper_ceasa_completo.py`
- Preview local: `python -m http.server 8000` → `http://localhost:8000`

## Credenciais / token GitHub

- Token OAuth do GitHub já salvo no Windows Credential Manager (`git credential fill`).
- Conta: `athenas1200` / `Athenas1200@gmail.com`
