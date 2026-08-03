# CEASA Market Monitor · Dashboard Hortifruti

Dashboard no estilo **Global Market Monitor** para cotações CEASA (Frutas + Hortaliças)
**e Café**, com dados históricos raspados do [Agrolink](https://www.agrolink.com.br/cotacoes/ceasa/)
e salvos diariamente no banco de dados da VPS (histórico acumulado a partir de hoje).

> Publicado: **https://athenas1200.github.io/ceasa-market-monitor/**
> · dre_demo: **https://consultoriasoft.com.br/dre_demo/ceasa.html**

---

## O que o dashboard mostra

- **Ordem fixada**: Café → Mamão → Maracujá → Pimenta → resto (`PIN_ORDEM` no JS)
- **Ticker tape** contínuo com os maiores movimentos
- **Cards de destaque**: maior alta, maior baixa, mais caro, mais barato
- **Seletor de data** (padrão = últimos preços disponíveis)
- **Filtros**: estado, categoria (Café/Frutas/Hortaliças), busca e "só altas"
- **Tabela ordenável** com preço médio, variação e mini sparkline da evolução
- **Detalhe por estado** ao clicar em um produto
- **Market breadth**, **mapa regional**, **gráfico de evolução** por categoria e **top altas/baixas**

## Arquivos

| Arquivo | Descrição |
|---|---|
| `index.html` | Dashboard (HTML/CSS/JS puro) |
| `ceasa_dashboard.json` | Dados processados consumidos pelo dashboard |
| `scraper_ceasa_completo.py` | Scraper completo (histórico) |
| `scraper_diario.py` | **Script diário da VPS** (banco + JSON) — em `/opt/` |
| `cafe_templates.json` | Templates de preço do café (decodificação do sprite) |
| `LINKS.md` | Links e instruções rápidas |

## Fluxo diário (VPS)

1. **Cron 05:30** → `bash /opt/rodar_ceasa.sh`
2. `scraper_diario.py` raspa as cotações novas (CEASA + Café), grava em
   **MySQL `agnaldon_nordeste.ceasa_cotacoes`** (INSERT IGNORE, sem duplicar)
3. Regenera `ceasa_dashboard.json` a partir do banco (histórico acumulado)
4. O dre_demo serve esse JSON automaticamente

O **café** tem preço em imagem no Agrolink: o script decodifica o sprite com
**tesseract** (fonte normal) e **template matching** (fonte 7-segmentos). Preços novos
que não existam em `cafe_templates.json` são pulados até o template ser atualizado.

## Como rodar localmente

```bash
pip install requests beautifulsoup4 pandas
python scraper_ceasa_completo.py        # histórico completo (~375 páginas)
python -m http.server 8000              # preview (não abrir via file://)
```

## Licença

MIT — use, modifique e compartilhe à vontade.
