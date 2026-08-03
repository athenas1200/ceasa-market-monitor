#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Completo de Cotações CEASA — Agrolink
Raspa TODOS os produtos (Frutas + Hortaliças) e gera:
  - ceasa_todos.csv            -> registros brutos
  - ceasa_dashboard.json       -> dados processados para o dashboard
  - ceasa_YYYY-MM-DD.csv       -> somente a última data

Uso:
    python scraper_ceasa_completo.py
    python scraper_ceasa_completo.py --categoria frutas
    python scraper_ceasa_completo.py --max-paginas 3   (teste rápido)
    python scraper_ceasa_completo.py --delay 0.8
"""

import argparse
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URLS = {
    "frutas": "https://www.agrolink.com.br/cotacoes/ceasa/frutas/",
    "hortalicas": "https://www.agrolink.com.br/cotacoes/ceasa/hortalicas/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

DELAY = 1.0
session = requests.Session()
session.headers.update(HEADERS)


def fetch_page(url: str, page_num: int) -> str:
    full_url = f"{url}?pagina={page_num}" if page_num > 1 else url
    resp = session.get(full_url, timeout=30)
    resp.raise_for_status()
    return resp.text


def get_total_records(html: str) -> int:
    m = re.search(r"Mostrando\s+\d+\s+at[eé]\s+\d+\s+de\s+([\d.]+)", html)
    if not m:
        return 0
    return int(m.group(1).replace(".", ""))


def parse_table(html: str, categoria: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    records = []
    for tr in rows[1:]:
        tds = tr.find_all(["td", "th"])
        if len(tds) < 4:
            continue

        produto_raw = tds[0].get_text(" ", strip=True)
        ceasa_raw = tds[1].get_text(" ", strip=True)
        preco_raw = tds[2].get_text(" ", strip=True)
        data_raw = tds[3].get_text(" ", strip=True)

        # Remove o nome da CEASA que vem repetido dentro da célula do produto
        nome_celula = produto_raw.replace(ceasa_raw, " ").strip()
        nome_celula = re.sub(r"\s+", " ", nome_celula)

        # Separa unidade do final (1Kg, 1Dz, 1Un, 1Maço, 1unidade, 12Un, 10Kg...)
        unidade = ""
        m_un = re.search(r"(\d+\s*(?:Kg|kg|gr|g|Dz|dz|Un|un|Maç|mç|Maço|unidade|saco|Saco|CX|cx|ml|L|caixa|Caixa|dúzia|Dúzia))\s*$", nome_celula)
        if m_un:
            unidade = m_un.group(1).replace(" ", "")
            produto_nome = nome_celula[: m_un.start()].strip()
        else:
            produto_nome = nome_celula

        # Estado a partir dos parênteses no fim da CEASA
        m_est = re.search(r"\(([A-Za-z]{2})\)\s*$", ceasa_raw)
        estado = m_est.group(1).upper() if m_est else ""

        # Preço
        preco_str = preco_raw.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            preco = float(preco_str)
        except ValueError:
            continue

        # Data
        try:
            data = datetime.strptime(data_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            continue

        if not produto_nome or not estado or preco <= 0:
            continue

        records.append({
            "produto": produto_nome,
            "unidade": unidade,
            "categoria": categoria,
            "ceasa": ceasa_raw,
            "estado": estado,
            "preco": round(preco, 2),
            "data": data,
        })

    return records


def scrape_categoria(nome: str, url: str, max_paginas: int = None, progress: dict = None) -> list[dict]:
    try:
        html = fetch_page(url, 1)
        total_rec = get_total_records(html)
        total_pages = (total_rec + 29) // 30 if total_rec else 1
        if max_paginas:
            total_pages = min(total_pages, max_paginas)
    except Exception as e:
        print(f"[{nome}] ERRO página 1: {e}")
        return []

    all_records = parse_table(html, nome)
    print(f"[{nome}] {len(all_records)} registros (pág 1/{total_pages})")

    for page in range(2, total_pages + 1):
        try:
            html = fetch_page(url, page)
            recs = parse_table(html, nome)
            all_records.extend(recs)
            if progress is not None:
                progress["done"] = progress.get("done", 0) + 1
            time.sleep(DELAY)
            if page % 10 == 0 or page == total_pages:
                print(f"[{nome}] pág {page}/{total_pages} -> {len(all_records)} registros")
        except Exception as e:
            print(f"[{nome}] ERRO pág {page}: {e}")
            break

    print(f"[{nome}] TOTAL: {len(all_records)} registros")
    return all_records


def build_dashboard(records: list[dict]) -> dict:
    # Agrupar por chave (produto, unidade, estado) e ordenar por data
    por_chave = {}
    for r in records:
        chave = (r["produto"], r["unidade"], r["estado"])
        por_chave.setdefault(chave, []).append(r)
    for serie in por_chave.values():
        serie.sort(key=lambda x: x["data"])

    datas = sorted({r["data"] for r in records})

    # Cobertura por dia (quantos registros cada data tem)
    cobertura = {}
    for r in records:
        cobertura[r["data"]] = cobertura.get(r["data"], 0) + 1

    # Data de referência: última data com cobertura completa (máxima)
    max_cobertura = max(cobertura.values())
    datas_cheias = [d for d in datas if cobertura[d] >= max_cobertura * 0.5]
    data_referencia = datas_cheias[-1] if datas_cheias else datas[-1]
    ultima = datas[-1]

    # Séries completas por produto+estado
    series = []
    for (produto, unidade, estado), serie in por_chave.items():
        primeira = serie[0]
        series.append({
            "produto": produto,
            "unidade": unidade,
            "categoria": primeira["categoria"],
            "estado": estado,
            "ceasa": primeira["ceasa"],
            "precos": [[s["data"], s["preco"]] for s in serie],
        })
    series.sort(key=lambda x: (x["produto"], x["estado"]))

    # Histórico por categoria (média nacional por dia)
    cat_map = {}
    for r in records:
        cat_map.setdefault(r["categoria"], {}).setdefault(r["data"], []).append(r["preco"])
    historico = {}
    for cat, dias in sorted(cat_map.items()):
        serie = []
        for d in sorted(dias):
            vals = dias[d]
            serie.append([datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m"), round(sum(vals) / len(vals), 2)])
        historico[cat] = serie

    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "fonte": "Agrolink",
        "url_fonte": "https://www.agrolink.com.br/cotacoes/ceasa/",
        "ultima_data": ultima,
        "data_referencia": data_referencia,
        "datas": datas,
        "cobertura": {d: cobertura[d] for d in datas},
        "series": series,
        "historico": historico,
        "raw_count": len(records),
        "n_produtos": len({(s["produto"], s["unidade"]) for s in series}),
        "n_estados": len({s["estado"] for s in series}),
    }


def exportar(df: list[dict], dashboard: dict, output_dir: str = "."):
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    with open(out / "ceasa_todos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(df[0].keys()))
        writer.writeheader()
        writer.writerows(df)

    with open(out / "ceasa_dashboard.json", "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    ultima = dashboard["ultima_data"]
    ultima_rows = [r for r in df if r["data"] == ultima]
    with open(out / f"ceasa_{ultima}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(df[0].keys()))
        writer.writeheader()
        writer.writerows(ultima_rows)

    print("\nArquivos gerados:")
    print(f"  {out / 'ceasa_todos.csv'}")
    print(f"  {out / 'ceasa_dashboard.json'}")
    print(f"  {out / f'ceasa_{ultima}.csv'}")

    print("\n=== RESUMO ===")
    print(f"Última data: {ultima}")
    print(f"Data de referência (cobertura completa): {dashboard['data_referencia']}")
    print(f"Registros totais: {dashboard['raw_count']}")
    print(f"Produtos únicos: {dashboard['n_produtos']}")
    print(f"Estados: {dashboard['n_estados']}")
    print(f"Categorias: {list(dashboard['historico'].keys())}")
    print(f"Datas disponíveis: {dashboard['datas'][0]} .. {dashboard['datas'][-1]} ({len(dashboard['datas'])})")


def main():
    parser = argparse.ArgumentParser(description="Scraper CEASA Agrolink")
    parser.add_argument("--categoria", choices=["frutas", "hortalicas", "todas"], default="todas")
    parser.add_argument("--max-paginas", type=int, help="Limitar páginas (teste)")
    parser.add_argument("--output", default=".", help="Diretório de saída")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay entre requests")
    args = parser.parse_args()

    global DELAY
    DELAY = args.delay

    print("=" * 60)
    print("  SCRAPER CEASA AGROLINK — TODOS OS PRODUTOS")
    print("=" * 60)

    cats = [("Frutas", BASE_URLS["frutas"])]
    if args.categoria in ("todas", "hortalicas"):
        cats.append(("Hortaliças", BASE_URLS["hortalicas"]))

    all_records = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(scrape_categoria, nome, url, args.max_paginas): nome for nome, url in cats}
        for fut in as_completed(futures):
            nome = futures[fut]
            try:
                all_records.extend(fut.result())
            except Exception as e:
                print(f"[{nome}] falhou: {e}")

    if not all_records:
        print("Nenhum registro encontrado.")
        sys.exit(1)

    dashboard = build_dashboard(all_records)
    exportar(all_records, dashboard, args.output)
    print("\nScraping concluido!")


if __name__ == "__main__":
    main()
