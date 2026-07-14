#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do painel PinkPapa (G3 Health Service) — rastreio de cancer de colo do utero
por teste DNA-HPV com autocoleta (produto PinkPapa / PinkLab).
HTML self-contained: 5.570 municipios + 27 estados (IBGE Censo 2022, mulheres 25-64),
funil/ROI ao vivo, comparativo de custo, ranking, e gerador de PROPOSTA PDF hi-tech (PNSB).
Publica no GitHub Pages g3healthservice/dashboard-pinkpapa.
"""
import json, datetime, pathlib

BASE = pathlib.Path("/Users/gersongomes/pinkpapa")
DADOS = json.load(open(BASE/"dados/municipios_pinkpapa.json", encoding="utf-8"))
BUILD = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# endpoint do Apps Script (envio real de e-mail com anexo). Vazio = fallback mailto.
EP = BASE/"mail_endpoint.txt"
MAIL_ENDPOINT = EP.read_text(encoding="utf-8").strip() if EP.exists() else ""

CAPITAIS = {
 'AC':'Rio Branco','AL':'Maceió','AP':'Macapá','AM':'Manaus','BA':'Salvador','CE':'Fortaleza',
 'DF':'Brasília','ES':'Vitória','GO':'Goiânia','MA':'São Luís','MT':'Cuiabá','MS':'Campo Grande',
 'MG':'Belo Horizonte','PA':'Belém','PB':'João Pessoa','PR':'Curitiba','PE':'Recife','PI':'Teresina',
 'RJ':'Rio de Janeiro','RN':'Natal','RS':'Porto Alegre','RO':'Porto Velho','RR':'Boa Vista',
 'SC':'Florianópolis','SP':'São Paulo','SE':'Aracaju','TO':'Palmas'}
UF_NOMES = {
 'AC':'Acre','AL':'Alagoas','AP':'Amapá','AM':'Amazonas','BA':'Bahia','CE':'Ceará','DF':'Distrito Federal',
 'ES':'Espírito Santo','GO':'Goiás','MA':'Maranhão','MT':'Mato Grosso','MS':'Mato Grosso do Sul',
 'MG':'Minas Gerais','PA':'Pará','PB':'Paraíba','PR':'Paraná','PE':'Pernambuco','PI':'Piauí',
 'RJ':'Rio de Janeiro','RN':'Rio Grande do Norte','RS':'Rio Grande do Sul','RO':'Rondônia','RR':'Roraima',
 'SC':'Santa Catarina','SP':'São Paulo','SE':'Sergipe','TO':'Tocantins'}

muns = [[d['nome'], d['uf'], d['pop'] or 0, d['m2564'] or 0] for d in DADOS if d['m2564']]
muns.sort(key=lambda x:-x[3])
uf_stats = {}
for nome,uf,pop,m in muns:
    s = uf_stats.setdefault(uf, {'pop':0,'m':0,'capital':None,'n':0})
    s['pop']+=pop; s['m']+=m; s['n']+=1
for nome,uf,pop,m in muns:
    if CAPITAIS.get(uf)==nome:
        uf_stats[uf]['capital']=[nome,uf,pop,m]
# "Estado de/do/da X" — artigo correto por UF (DF não é Estado)
UF_ARTIGO = {
 'AC':'do Acre','AL':'de Alagoas','AP':'do Amapá','AM':'do Amazonas','BA':'da Bahia','CE':'do Ceará',
 'DF':'','ES':'do Espírito Santo','GO':'de Goiás','MA':'do Maranhão','MT':'de Mato Grosso',
 'MS':'de Mato Grosso do Sul','MG':'de Minas Gerais','PA':'do Pará','PB':'da Paraíba','PR':'do Paraná',
 'PE':'de Pernambuco','PI':'do Piauí','RJ':'do Rio de Janeiro','RN':'do Rio Grande do Norte',
 'RS':'do Rio Grande do Sul','RO':'de Rondônia','RR':'de Roraima','SC':'de Santa Catarina',
 'SP':'de São Paulo','SE':'de Sergipe','TO':'do Tocantins'}
for uf,s in uf_stats.items():
    s['nome'] = UF_NOMES.get(uf,uf)
    # rótulo pronto: "Estado da Bahia" / "Distrito Federal"
    s['label'] = 'Distrito Federal' if uf=='DF' else 'Estado '+UF_ARTIGO.get(uf,'de '+s['nome'])
    s['orgao'] = ('Secretaria de Saúde do Distrito Federal' if uf=='DF'
                  else 'Secretaria Estadual de Saúde '+UF_ARTIGO.get(uf,'de '+s['nome']))
TOT_M = sum(x[3] for x in muns); TOT_POP = sum(x[2] for x in muns)

DATA_JS   = json.dumps(muns, ensure_ascii=False, separators=(',',':'))
UFSTATS_JS= json.dumps(uf_stats, ensure_ascii=False, separators=(',',':'))

def vend(name):
    return open(BASE/"vendor"/name, encoding="utf-8").read().replace('</script','<\\/script')
CHART = vend("chart.umd.js"); JSPDF = vend("jspdf.umd.min.js"); AUTOTABLE = vend("jspdf.autotable.min.js")

TOTM_BR = f"{TOT_M:,}".replace(",",".")

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>PinkPapa · Painel de Rastreio de Câncer de Colo do Útero (DNA-HPV) — G3 Health Service</title>
<style>
:root{--pink:#E6007E;--pink2:#FF4DA6;--wine:#7C1D4F;--green:#12A97A;--red:#C81E5B;
 --ink:#2A1622;--muted:#7a6b73;--bg:#fff;--soft:#fff2f8;--line:#f1d9e6;--card:#fff;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.5}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
a{color:var(--pink)} h1,h2,h3{margin:0}
.hero{background:linear-gradient(135deg,#E6007E 0%,#B4126A 55%,#7C1D4F 100%);color:#fff;padding:46px 0 40px}
.hero .brand{font-weight:800;letter-spacing:.5px;font-size:14px;opacity:.9;text-transform:uppercase}
.hero h1{font-size:30px;margin:10px 0 6px;font-weight:800;line-height:1.15}
.hero p{font-size:15px;opacity:.95;max-width:760px}
.hero .kpis{display:flex;flex-wrap:wrap;gap:14px;margin-top:22px}
.hero .kpi{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:12px 16px;min-width:150px}
.hero .kpi b{display:block;font-size:22px;font-weight:800}
.hero .kpi span{font-size:12px;opacity:.9}
section{padding:38px 0;border-bottom:1px solid var(--line)}
section.alt{background:var(--soft)}
.h{color:var(--pink);font-weight:800;font-size:13px;letter-spacing:1px;text-transform:uppercase}
.title{font-size:23px;font-weight:800;margin:6px 0 18px;line-height:1.2}
.lead{color:var(--muted);max-width:820px;margin:-8px 0 18px;font-size:15px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.card .num{font-size:27px;font-weight:800;color:var(--wine)}
.card .num.pink{color:var(--pink)}.card .num.green{color:var(--green)}.card .num.red{color:var(--red)}
.card .lbl{font-size:13.5px;margin-top:4px}
.card .src{font-size:11px;color:var(--muted);margin-top:8px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;margin-top:6px}
.selrow{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end}
.selrow .fld{flex:1;min-width:200px}
label{font-size:12.5px;color:var(--muted);font-weight:600;display:block;margin-bottom:4px}
input[type=text],input[type=number],select{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font-size:14px;background:#fff;color:var(--ink)}
.tabs{display:flex;gap:8px;margin-bottom:14px}
.tab{padding:9px 18px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--muted);font-weight:700;font-size:13.5px;cursor:pointer}
.tab.on{background:var(--pink);color:#fff;border-color:var(--pink)}
.muni-hero{display:flex;flex-wrap:wrap;gap:16px;align-items:baseline;margin:16px 0 4px}
.muni-hero .mn{font-size:24px;font-weight:800}
.muni-hero .mt{color:var(--muted);font-size:14px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:14px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.ctl{display:flex;align-items:center;gap:10px;margin:9px 0}
.ctl label{flex:1;margin:0}
.ctl input[type=range]{flex:1.4;accent-color:var(--pink)}
.ctl .rangeval{width:56px;text-align:right;font-weight:700;color:var(--wine);font-size:13px}
.ctl input[type=number]{width:96px}
.step{display:flex;align-items:center;gap:10px;margin:7px 0}
.step .lbl{width:230px;font-size:12.5px}
.step .bar-track{flex:1;background:#f6e6ef;border-radius:8px;height:16px;overflow:hidden}
.step .bar-fill{height:100%;background:linear-gradient(90deg,var(--pink),var(--pink2));border-radius:8px}
.step .val{width:92px;text-align:right;font-weight:700;font-size:13px;color:var(--wine)}
.roi{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:14px}
.roi .b{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;text-align:center}
.roi .b b{display:block;font-size:22px;font-weight:800;color:var(--wine)}
.roi .b.green b{color:var(--green)}.roi .b span{font-size:11.5px;color:var(--muted)}
.callout{background:#fff6fb;border:1px solid var(--line);border-left:4px solid var(--pink);border-radius:10px;padding:12px 14px;font-size:13px;margin-top:12px}
.btnrow{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px;align-items:center}
.btn{background:var(--pink);color:#fff;border:none;border-radius:10px;padding:11px 18px;font-size:14px;font-weight:700;cursor:pointer}
.btn.sec{background:#fff;color:var(--pink);border:1px solid var(--pink)}
.btn:disabled{opacity:.5;cursor:wait}
.btn:hover{filter:brightness(1.05)}
#mailStatus{font-size:13px;font-weight:600}
table.cmp{width:100%;border-collapse:collapse;margin-top:10px;font-size:13.5px}
table.cmp th,table.cmp td{border:1px solid var(--line);padding:10px 12px;text-align:left}
table.cmp th{background:#fbe7f2;color:var(--wine)}
table.cmp td.pp{background:#fff2f8;font-weight:600}
.rank{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:8px}
.rank th,.rank td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right}
.rank th:first-child,.rank td:first-child,.rank th:nth-child(2),.rank td:nth-child(2){text-align:left}
.rank th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase}
.rank tr{cursor:pointer}.rank tr:hover td{background:var(--soft)}
.pill{display:inline-block;background:#fbe7f2;color:var(--wine);border-radius:999px;padding:3px 10px;font-size:12px;font-weight:700;margin:2px 4px 2px 0}
.foot{padding:26px 0;color:var(--muted);font-size:12.5px}
.foot b{color:var(--ink)}
.tag{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:4px 12px;font-size:12px;margin-top:14px}
.note{font-size:11.5px;color:var(--muted);margin-top:6px}
.src2{font-size:11px;color:var(--muted)}
</style>
</head>
<body>

<div class="hero"><div class="wrap">
  <div class="brand">G3 Health Service · PinkPapa (PinkLab)</div>
  <h1>Rastreio de câncer de colo do útero por teste DNA-HPV com autocoleta</h1>
  <p>Painel de apoio à decisão para secretarias municipais e estaduais de saúde: dimensiona a população-alvo (mulheres de 25 a 64 anos), o custo-benefício frente ao tratamento oncológico e o alinhamento às metas oficiais — por município ou por estado.</p>
  <div class="kpis">
    <div class="kpi"><b>__TOTM__</b><span>mulheres de 25 a 64 anos no Brasil (Censo 2022) — população-alvo</span></div>
    <div class="kpi"><b>17.010</b><span>casos novos/ano de câncer de colo do útero (INCA)</span></div>
    <div class="kpi"><b>7.143</b><span>óbitos em 2023 — 1 mulher a cada ~90 min</span></div>
    <div class="kpi"><b>R$ 350</b><span>custo do kit × dezenas de milhares no tratamento tardio</span></div>
  </div>
  <div class="tag">Autoteste DNA-HPV homologado ANVISA · SIGTAP 0202100251 · Incorporado ao SUS (Portaria SECTICS/MS nº 3/2024)</div>
</div></div>

<section><div class="wrap">
  <div class="h">01 · O problema</div>
  <h3 class="title">Câncer de colo do útero: quase 100% evitável, mas ainda mata milhares por rastreio tardio</h3>
  <div class="cards">
    <div class="card"><div class="num red">17.010</div><div class="lbl">casos novos por ano (taxa 15,38/100 mil mulheres)</div><div class="src">INCA — Estimativa 2023–2025</div></div>
    <div class="card"><div class="num red">7.143</div><div class="lbl">óbitos em 2023, +8,3% desde 2019 — 3º câncer mais frequente entre brasileiras</div><div class="src">Observatório de Oncologia (SIM/SUS)</div></div>
    <div class="card"><div class="num">1 em 7</div><div class="lbl">mulheres com citologia normal e HPV-16+ tinham lesão de alto grau <b>não detectada</b> pelo Papanicolau</div><div class="src">Estudo ATHENA</div></div>
    <div class="card"><div class="num">4 a 6 meses</div><div class="lbl">de espera no agendamento; rastreio ainda oportunístico</div><div class="src">Diretrizes MS / PinkLab</div></div>
  </div>
  <div class="callout">O HPV é a infecção sexualmente transmissível mais prevalente do mundo e o <b>principal causador do câncer de colo do útero</b>. A citologia (Papanicolau) tem sensibilidade de apenas 55–70% para lesões de alto grau (NIC2+); o teste de DNA-HPV chega a 90–95%, com valor preditivo negativo de 98–99% — o que permite espaçar o rastreio para 5 anos após resultado negativo.</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="h">02 · A solução e seu enquadramento oficial</div>
  <h3 class="title">PinkPapa: autocoleta de DNA-HPV, alinhada às novas diretrizes do Ministério da Saúde</h3>
  <div class="grid2">
    <div class="panel">
      <b style="color:var(--wine)">Como funciona</b>
      <p style="font-size:14px">Autoteste de HPV homologado pela ANVISA. A mulher faz a <b>autocoleta</b> em UBS, UPA, centros comunitários ou hospitais — sem mesa ginecológica, sem espéculo, sem constrangimento. Detecta <b>28 tipos de HPV</b> (19 de alto risco oncogênico + 9 de baixo risco), informando o tipo viral. Acompanhamento por IA por até 5 anos.</p>
      <div><span class="pill">Alto risco: 16, 18, 31, 33, 35, 39, 45, 51, 52, 56, 58, 59, 66, 68…</span>
      <span class="pill">Antecipa o diagnóstico em até 10 anos</span>
      <span class="pill">Aceitação ~100% (não invasivo)</span></div>
    </div>
    <div class="panel">
      <b style="color:var(--wine)">Nome técnico e enquadramento (o que buscar no edital)</b>
      <table class="cmp" style="margin-top:8px">
        <tr><th>Campo</th><th>Valor oficial</th></tr>
        <tr><td>Procedimento SIGTAP</td><td class="pp">0202100251 — Exame molecular de detecção de HPV</td></tr>
        <tr><td>Descrição técnica</td><td>Análise molecular de material cérvico-vaginal por amplificação de ácido nucleico (PCR) com genotipagem parcial ou estendida</td></tr>
        <tr><td>Faixa etária</td><td>25 a 64 anos (300–779 meses)</td></tr>
        <tr><td>Financiamento</td><td>Média e Alta Complexidade (MAC)</td></tr>
        <tr><td>Incorporação</td><td>Portaria SECTICS/MS nº 3, de 07/03/2024 (CONITEC)</td></tr>
        <tr><td>Diretriz</td><td>Rastreamento organizado — DNA-HPV substitui o Papanicolau (MS/INCA, 2024)</td></tr>
      </table>
      <div class="note">Para compra de insumo/kit, o item é catalogado como material de detecção de DNA-HPV (CATMAT/BPS); o procedimento/serviço é o SIGTAP 0202100251.</div>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="h">03 · Dimensionamento</div>
  <h3 class="title">Perfil por município ou por estado</h3>
  <p class="lead">Todos os números partem da população feminina de 25 a 64 anos do Censo 2022 (IBGE). Premissas ajustáveis; valores-padrão documentados na metodologia.</p>
  <div class="panel">
    <div class="tabs">
      <div class="tab on" id="tab-mun" onclick="setEscopo('mun')">🏙️ Município</div>
      <div class="tab" id="tab-uf" onclick="setEscopo('uf')">🗺️ Estado (UF)</div>
    </div>
    <div class="selrow" id="row-mun">
      <div class="fld">
        <label>Município (digite para buscar — sem precisar de acento)</label>
        <input type="text" id="busca" placeholder="Ex.: sao paulo, salvador, campinas…" autocomplete="off" oninput="onBusca()">
        <div id="sug" style="position:relative"></div>
      </div>
    </div>
    <div class="selrow" id="row-uf" style="display:none">
      <div class="fld" style="max-width:380px">
        <label>Estado — a proposta será dirigida à Secretaria Estadual de Saúde</label>
        <select id="seluf" onchange="pickUF(this.value)"><option value="">Selecione o estado…</option></select>
      </div>
    </div>

    <div id="muniBox" style="display:none">
      <div class="muni-hero"><div class="mn" id="mn"></div><div class="mt" id="mt"></div></div>
      <div class="grid2">
        <div>
          <div class="ctl"><label>Cobertura atual de rastreio (ajuste manual)</label><input type="range" id="in-cov-atual" min="1" max="100" value="40" oninput="calc()"><span class="rangeval" id="v-cov-atual">40%</span></div>
          <div class="ctl"><label>Cobertura-meta (OMS: 70%)</label><input type="range" id="in-cov-meta" min="1" max="100" value="70" oninput="calc()"><span class="rangeval" id="v-cov-meta">70%</span></div>
          <div class="ctl"><label>Adesão ao convite</label><input type="range" id="in-adesao" min="1" max="100" value="80" oninput="calc()"><span class="rangeval" id="v-adesao">80%</span></div>
          <div class="ctl"><label>Prevalência de HPV de alto risco</label><input type="range" id="in-prev" min="1" max="30" value="10" oninput="calc()"><span class="rangeval" id="v-prev">10%</span></div>
          <div class="ctl"><label>Lesões alto grau (NIC2+) entre HPV+</label><input type="range" id="in-lesao" min="1" max="40" value="12" oninput="calc()"><span class="rangeval" id="v-lesao">12%</span></div>
          <div class="ctl"><label>Progressão a câncer se não tratada</label><input type="range" id="in-prog" min="1" max="40" value="15" oninput="calc()"><span class="rangeval" id="v-prog">15%</span></div>
          <div class="ctl"><label>Preço do kit PinkPapa (R$)</label><input type="number" id="in-preco" value="350" min="1" oninput="calc()"></div>
          <div class="ctl"><label>Prazo de execução (meses)</label><input type="number" id="in-prazo" value="12" min="1" max="60" oninput="calc()"></div>
        </div>
        <div>
          <div id="funnel-box"></div>
          <div class="roi">
            <div class="b"><b id="roi-custo">—</b><span>Investimento no rastreio</span></div>
            <div class="b green"><b id="roi-cpm">—</b><span>Custo por morte evitada</span></div>
            <div class="b green"><b id="roi-soc">—</b><span>Retorno socioeconômico</span></div>
          </div>
          <div class="callout" style="margin-top:12px" id="resumo"></div>
        </div>
      </div>
      <div class="callout"><b>Premissa importante:</b> "casos suspeitos/lesões" não são câncer confirmado. O funil aplica etapas de confirmação e progressão ajustáveis (história natural do HPV) antes de estimar casos e mortes evitados — para não superestimar o retorno. Ajuste os controles à realidade epidemiológica local.</div>

      <div class="selrow" style="margin-top:16px">
        <div class="fld"><label>Destinatário / autoridade (entra na proposta)</label><input type="text" id="in-dest-nome" placeholder="Ex.: Sr. Nicolau — Secretário de Saúde"></div>
        <div class="fld" style="max-width:280px"><label>E-mail do destinatário</label><input type="text" id="in-dest-email" placeholder="nome@municipio.gov.br"></div>
      </div>
      <div class="selrow" style="margin-top:8px">
        <div class="fld"><label>Proponente — representante</label><input type="text" id="in-prop-nome" value="Gerson Gomes"></div>
        <div class="fld"><label>Proponente — e-mail</label><input type="text" id="in-prop-email" value="g3.healthservice@proton.me"></div>
        <div class="fld" style="max-width:200px"><label>Proponente — telefone</label><input type="text" id="in-prop-tel" value="+55 61 99255-7690"></div>
      </div>
      <div class="btnrow">
        <button class="btn" onclick="baixarPDF()">📄 Baixar proposta em PDF (PNSB)</button>
        <button class="btn sec" id="btnMail" onclick="enviarEmail()">✉️ Enviar proposta por e-mail</button>
        <span id="mailStatus"></span>
      </div>
      <div class="note" id="mailNote"></div>
    </div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="h">04 · Custo-benefício</div>
  <h3 class="title">R$ 350 na prevenção × dezenas de milhares no tratamento tardio</h3>
  <p class="lead">O valor por exame do PinkPapa cruzado com o custo real dos procedimentos do SUS. Fontes: Observatório de Oncologia (APAC/SIA-SIH) e Tabela SIGTAP.</p>
  <table class="cmp">
    <tr><th>Item</th><th>PinkPapa (DNA-HPV, autocoleta)</th><th>Papanicolau (citologia)</th><th>Tratamento do câncer (tardio)</th></tr>
    <tr><td>Custo unitário</td><td class="pp">R$ 350 / mulher</td><td>R$ 14,37 / exame (SIGTAP)</td><td>R$ 10.000 / paciente / ano</td></tr>
    <tr><td>Sensibilidade (NIC2+)</td><td class="pp">90–95%</td><td>55–70%</td><td>—</td></tr>
    <tr><td>Intervalo</td><td class="pp">5 anos (após negativo)</td><td>3 anos (2 normais)</td><td>—</td></tr>
    <tr><td>Coleta</td><td class="pp">Autocoleta (sem profissional/estrutura)</td><td>Requer médico/enfermeiro + estrutura</td><td>—</td></tr>
    <tr><td>Procedimentos típicos</td><td class="pp">1 teste + acompanhamento IA</td><td>Exame + consulta + repetições</td><td>Cirurgia + radioterapia (R$ 4.038/APAC) + braquiterapia (R$ 3.936/APAC) + quimioterapia + internações (R$ 2.183)</td></tr>
  </table>
  <div class="cards" style="margin-top:16px">
    <div class="card"><div class="num pink">≈ 28×</div><div class="lbl">um tratamento oncológico anual equivale a ~28 kits PinkPapa</div><div class="src">R$ 10 mil ÷ R$ 350</div></div>
    <div class="card"><div class="num green">−30%</div><div class="lbl">de redução estimada de custos do SUS no longo prazo com rastreio por DNA-HPV</div><div class="src">CONITEC</div></div>
    <div class="card"><div class="num">R$ 184 mi</div><div class="lbl">impacto incremental em 5 anos da incorporação — compensado pela queda em tratamentos tardios</div><div class="src">CONITEC (2024)</div></div>
    <div class="card"><div class="num red">64%</div><div class="lbl">das pacientes em radioterapia se tratam fora do município</div><div class="src">Observatório de Oncologia</div></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="h">05 · Metas e cobertura</div>
  <h3 class="title">Alinhamento às metas oficiais de eliminação</h3>
  <div class="cards">
    <div class="card"><div class="num pink">90-70-90</div><div class="lbl">Meta OMS até 2030: <b>90%</b> vacinadas, <b>70%</b> rastreadas com teste de alta performance, <b>90%</b> tratadas</div><div class="src">OMS/ONU (194 países, 2020)</div></div>
    <div class="card"><div class="num">≥ 40%</div><div class="lbl">meta de cobertura do exame de rastreio (Previne Brasil)</div><div class="src">Ministério da Saúde</div></div>
    <div class="card"><div class="num red">em queda</div><div class="lbl">cobertura de citologia nas capitais no menor valor da série histórica (2023)</div><div class="src">SISCAN / INCA</div></div>
    <div class="card"><div class="num green">-97%</div><div class="lbl">de redução possível na incidência atingindo as metas 90-70-90</div><div class="src">OMS / SBOC</div></div>
  </div>
  <div class="callout">Estratégia de eliminação = <b>Vacinação + Rastreio + Tratamento</b>. O PinkPapa atua no pilar do <b>rastreio</b>, com o teste de alta performance (DNA-HPV) recomendado pela OMS para atingir a meta de 70% — e a autocoleta é o vetor para alcançar as mulheres que nunca se rastrearam.</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="h">06 · Ranking de oportunidade</div>
  <h3 class="title">Por população-alvo (mulheres 25–64 anos)</h3>
  <div class="tabs">
    <div class="tab on" id="rtab-mun" onclick="setRank('mun')">Municípios</div>
    <div class="tab" id="rtab-uf" onclick="setRank('uf')">Estados</div>
  </div>
  <p class="lead">Clique em uma linha para carregá-la no dimensionamento acima.</p>
  <table class="rank"><thead id="rankHead"></thead><tbody id="rankBody"></tbody></table>
</div></section>

<section><div class="wrap">
  <div class="h">07 · Metodologia e fontes</div>
  <h3 class="title">Como os números são calculados</h3>
  <div class="grid2">
    <div class="panel"><b style="color:var(--wine)">Modelo do funil</b>
      <ol style="font-size:13.5px;padding-left:18px">
        <li>População-alvo = mulheres de 25 a 64 anos (IBGE, Censo 2022, SIDRA 9514) — do município ou somadas no estado.</li>
        <li>Mulheres adicionais = alvo × (cobertura-meta − cobertura atual).</li>
        <li>Testes DNA-HPV = adicionais × adesão ao convite.</li>
        <li>HPV alto risco+ = testes × prevalência.</li>
        <li>Lesões NIC2+ = HPV+ × % de lesão; das quais a citologia perderia (95%−60%).</li>
        <li>Casos de câncer evitados = lesões × progressão evitada pelo tratamento precoce.</li>
        <li>Mortes evitadas = casos × letalidade evitável (40%).</li>
      </ol>
    </div>
    <div class="panel"><b style="color:var(--wine)">Fontes oficiais</b>
      <ul class="src2" style="padding-left:18px;line-height:1.7">
        <li>IBGE — Censo 2022 (SIDRA 9514/4709).</li>
        <li>INCA — Estimativa de Incidência 2023–2025.</li>
        <li>Observatório de Oncologia — custos APAC/SIA-SIH.</li>
        <li>SIGTAP — procedimentos 0202100251 e 0203010086.</li>
        <li>CONITEC/MS — Portaria SECTICS nº 3/2024.</li>
        <li>OMS/ONU — estratégia 90-70-90.</li>
      </ul>
      <div class="note">Ferramenta de apoio à decisão e prospecção. Não substitui avaliação epidemiológica local nem diagnóstico médico.</div>
    </div>
  </div>
</div></section>

<div class="wrap foot">
  <b>G3 Health Service</b> · Painel PinkPapa (PinkLab) — rastreio de câncer de colo do útero por DNA-HPV.<br>
  Contato: g3.healthservice@proton.me · Build __BUILD__ · Dados: IBGE Censo 2022, INCA, Observatório de Oncologia, CONITEC, OMS.
</div>

<script>__CHART__</script>
<script>__JSPDF__</script>
<script>__AUTOTABLE__</script>
<script>
const MUNICIPIOS = __DATA__;    // [nome, uf, pop, m2564]
const UF_STATS   = __UFSTATS__; // {uf:{pop,m,n,capital,nome}}
const MAIL_ENDPOINT = "__MAIL_ENDPOINT__";
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
let selected = null, lastCalc = null, escopo = 'mun';

const fmt = n => Math.round(n).toLocaleString('pt-BR');
const fmtMoney = n => 'R$ '+Math.round(n).toLocaleString('pt-BR');
const fmtPct = n => (n*100).toFixed(0).replace('.',',')+'%';

/* ---------- escopo município / estado ---------- */
function setEscopo(e){
  escopo = e;
  document.getElementById('tab-mun').classList.toggle('on', e==='mun');
  document.getElementById('tab-uf').classList.toggle('on', e==='uf');
  document.getElementById('row-mun').style.display = e==='mun'?'flex':'none';
  document.getElementById('row-uf').style.display  = e==='uf'?'flex':'none';
  document.getElementById('muniBox').style.display='none';
  selected=null; lastCalc=null;
}
function onBusca(){
  const q = norm(document.getElementById('busca').value.trim());
  const sug = document.getElementById('sug');
  if(q.length<2){ sug.innerHTML=''; return; }
  const hits = MUNICIPIOS.filter(m=>norm(m[0]).includes(q)).slice(0,8);
  sug.innerHTML = '<div style="position:absolute;z-index:9;background:#fff;border:1px solid var(--line);border-radius:10px;width:100%;box-shadow:0 8px 24px rgba(124,29,79,.12);overflow:hidden">'+
    hits.map(m=>`<div style="padding:9px 12px;cursor:pointer;font-size:14px" onmousedown="pick('${m[0].replace(/'/g,"\\'")}','${m[1]}')">${m[0]} <span style="color:var(--muted)">/ ${m[1]} · ${m[3].toLocaleString('pt-BR')} mulheres 25-64</span></div>`).join('')+'</div>';
}
function pick(nome,uf){
  escopo='mun'; setEscopoTabs('mun');
  selected = MUNICIPIOS.find(m=>m[0]===nome && m[1]===uf);
  selected = [selected[0],selected[1],selected[2],selected[3],false];
  document.getElementById('busca').value = nome+' / '+uf;
  document.getElementById('sug').innerHTML='';
  show();
}
function pickUF(uf){
  if(!uf) return;
  escopo='uf'; setEscopoTabs('uf');
  const s = UF_STATS[uf];
  selected = [s.label, uf, s.pop, s.m, true];
  document.getElementById('seluf').value = uf;
  show();
}
function setEscopoTabs(e){
  document.getElementById('tab-mun').classList.toggle('on', e==='mun');
  document.getElementById('tab-uf').classList.toggle('on', e==='uf');
  document.getElementById('row-mun').style.display = e==='mun'?'flex':'none';
  document.getElementById('row-uf').style.display  = e==='uf'?'flex':'none';
}
function show(){
  if(!selected) return;
  document.getElementById('muniBox').style.display='block';
  const isUF = selected[4];
  document.getElementById('mn').textContent = isUF ? selected[0] : selected[0]+' / '+selected[1];
  const extra = isUF ? ' · '+UF_STATS[selected[1]].n+' municípios' : '';
  document.getElementById('mt').textContent = selected[3].toLocaleString('pt-BR')+' mulheres de 25 a 64 anos · '+selected[2].toLocaleString('pt-BR')+' habitantes (Censo 2022)'+extra;
  calc();
}

/* ---------- núcleo do cálculo ---------- */
const CUSTO_PRECOCE=1500, CUSTO_TARDIO=30000, VALOR_MORTE=1000000;
const SENS_DNA=0.95, SENS_CITO=0.60, LETALIDADE_EVIT=0.40;
const val = id => document.getElementById('in-'+id).value;

function calc(){
  if(!selected) return;
  ['cov-atual','cov-meta','adesao','prev','lesao','prog'].forEach(id=>{
    const el=document.getElementById('v-'+id); if(el) el.textContent=val(id)+'%'; });
  const popAlvo=selected[3];
  const covA=+val('cov-atual')/100, covM=+val('cov-meta')/100, ades=+val('adesao')/100;
  const prev=+val('prev')/100, pLes=+val('lesao')/100, pProg=+val('prog')/100;
  const preco=+val('preco')||0, prazo=+val('prazo')||12;

  const adicionais = popAlvo*Math.max(0,covM-covA);
  const testes = adicionais*ades;
  const hpvPos = testes*prev;
  const lesoes = hpvPos*pLes;
  const lesoesCitoPerde = lesoes*(SENS_DNA-SENS_CITO);
  const casosEvit = lesoes*pProg;
  const mortesEvit = casosEvit*LETALIDADE_EVIT;

  const custoPrograma = testes*preco;
  const custoEvitado = casosEvit*(CUSTO_TARDIO-CUSTO_PRECOCE);
  const valorSocial = mortesEvit*VALOR_MORTE;
  const roiSoc = custoPrograma>0 ? (custoEvitado+valorSocial-custoPrograma)/custoPrograma : 0;
  const custoPorMorte = mortesEvit>0 ? custoPrograma/mortesEvit : 0;
  const custoPorCaso = casosEvit>0 ? custoPrograma/casosEvit : 0;
  const testesMes = prazo>0 ? testes/prazo : 0;

  const steps = [
    ['População-alvo (25–64 anos)', popAlvo, popAlvo],
    ['Mulheres adicionais no rastreio', adicionais, popAlvo],
    ['Testes DNA-HPV (c/ adesão)', testes, popAlvo],
    ['HPV de alto risco positivos', hpvPos, popAlvo],
    ['Lesões NIC2+ detectadas', lesoes, popAlvo],
    ['Casos de câncer evitados', casosEvit, popAlvo],
    ['Mortes potencialmente evitadas', mortesEvit, popAlvo],
  ];
  document.getElementById('funnel-box').innerHTML = steps.map(s=>{
    const pct=Math.max(1,(s[1]/s[2])*100);
    return `<div class="step"><div class="lbl">${s[0]}</div><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div><div class="val">${fmt(s[1])}</div></div>`;}).join('');
  document.getElementById('roi-custo').textContent=fmtMoney(custoPrograma);
  document.getElementById('roi-cpm').textContent = mortesEvit>0?fmtMoney(custoPorMorte):'—';
  document.getElementById('roi-soc').textContent = (roiSoc>=0?'+':'')+fmtPct(roiSoc);
  const alvoNome = selected[4] ? selected[0] : selected[0];
  document.getElementById('resumo').innerHTML =
    `Para levar <b>${alvoNome}</b> de ${(covA*100).toFixed(0)}% a ${(covM*100).toFixed(0)}% de cobertura, seriam <b>${fmt(testes)}</b> testes DNA-HPV (<b>${fmtMoney(custoPrograma)}</b>), `+
    `detectando ~<b>${fmt(lesoes)}</b> lesões de alto grau — sendo <b>${fmt(lesoesCitoPerde)}</b> que o Papanicolau perderia. `+
    `Estimativa: <b>${fmt(casosEvit)}</b> cânceres e <b>${fmt(mortesEvit)}</b> mortes evitados; retorno socioeconômico de <b>${(roiSoc*100).toFixed(0)}%</b>. `+
    `Frente ao Papanicolau (não somado a ele), o DNA-HPV é custo-efetivo e reduz gastos no longo prazo (CONITEC: −30%).`;

  lastCalc = {muni:selected, steps, custoPrograma, custoEvitado, valorSocial, roiSoc, custoPorMorte, custoPorCaso,
    lesoes, lesoesCitoPerde, testes, casosEvit, mortesEvit, preco, prazo, testesMes, isUF:selected[4],
    premissas:[['Cobertura atual',(covA*100).toFixed(0)+'%'],['Cobertura-meta',(covM*100).toFixed(0)+'%'],
      ['Adesão ao convite',(ades*100).toFixed(0)+'%'],['Prevalência HPV alto risco',(prev*100).toFixed(0)+'%'],
      ['Lesões NIC2+ entre HPV+',(pLes*100).toFixed(0)+'%'],['Progressão a câncer evitada',(pProg*100).toFixed(0)+'%'],
      ['Preço unitário do kit','R$ '+preco.toLocaleString('pt-BR')],['Prazo de execução',prazo+' meses']]};
}

/* ---------- rankings ---------- */
let rankMode='mun';
function setRank(m){
  rankMode=m;
  document.getElementById('rtab-mun').classList.toggle('on',m==='mun');
  document.getElementById('rtab-uf').classList.toggle('on',m==='uf');
  renderRank();
}
function renderRank(){
  const head=document.getElementById('rankHead'), body=document.getElementById('rankBody');
  if(rankMode==='mun'){
    head.innerHTML='<tr><th>#</th><th>Município</th><th>UF</th><th>Mulheres 25–64</th><th>População</th><th>% alvo</th></tr>';
    body.innerHTML=MUNICIPIOS.slice(0,60).map((m,i)=>
      `<tr onclick="pick('${m[0].replace(/'/g,"\\'")}','${m[1]}');document.querySelector('.panel').scrollIntoView({behavior:'smooth'})"><td>${i+1}</td><td>${m[0]}</td><td>${m[1]}</td><td>${m[3].toLocaleString('pt-BR')}</td><td>${m[2].toLocaleString('pt-BR')}</td><td>${(100*m[3]/m[2]).toFixed(1)}%</td></tr>`).join('');
  } else {
    const ufs=Object.entries(UF_STATS).sort((a,b)=>b[1].m-a[1].m);
    head.innerHTML='<tr><th>#</th><th>Estado</th><th>UF</th><th>Mulheres 25–64</th><th>População</th><th>Municípios</th></tr>';
    body.innerHTML=ufs.map(([uf,s],i)=>
      `<tr onclick="pickUF('${uf}');document.querySelector('.panel').scrollIntoView({behavior:'smooth'})"><td>${i+1}</td><td>${s.nome}</td><td>${uf}</td><td>${s.m.toLocaleString('pt-BR')}</td><td>${s.pop.toLocaleString('pt-BR')}</td><td>${s.n}</td></tr>`).join('');
  }
}
function initUF(){
  const ufs=Object.entries(UF_STATS).sort((a,b)=>a[1].nome.localeCompare(b[1].nome));
  document.getElementById('seluf').innerHTML='<option value="">Selecione o estado…</option>'+
    ufs.map(([uf,s])=>`<option value="${uf}">${s.nome} (${uf}) — ${s.m.toLocaleString('pt-BR')} mulheres 25-64</option>`).join('');
}

/* ================= PROPOSTA PDF (hi-tech) ================= */
const MESES=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
const dataExtenso = d => d.getDate()+' de '+MESES[d.getMonth()]+' de '+d.getFullYear();
const C_PINK=[230,0,126], C_WINE=[124,29,79], C_DARK=[36,12,26], C_GREEN=[18,169,122], C_GREY=[120,110,116];

const valueLabelPlugin={id:'vl',afterDatasetsDraw(c){const{ctx}=c;c.data.datasets.forEach((ds,di)=>{c.getDatasetMeta(di).data.forEach((bar,i)=>{ctx.save();ctx.fillStyle='#2A1622';ctx.font='bold 13px Arial';ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText(Math.round(ds.data[i]).toLocaleString('pt-BR'),bar.x+8,bar.y);ctx.restore();});});}};
function chartImg(config,w,h){
  const cv=document.createElement('canvas');cv.width=w;cv.height=h;
  config.plugins=(config.plugins||[]).concat([valueLabelPlugin]);
  const ch=new Chart(cv.getContext('2d'),config);const img=ch.toBase64Image('image/png',1.0);ch.destroy();return img;
}
/* estilo limpo: sem grid vertical pesado, fonte maior, barras arredondadas */
const baseOpts = (titulo)=>({responsive:false,animation:false,indexAxis:'y',
  layout:{padding:{right:90,left:4,top:4,bottom:4}},
  plugins:{legend:{display:false},title:{display:true,text:titulo,font:{size:14,weight:'bold'},color:'#7C1D4F',padding:{bottom:12}}},
  scales:{x:{display:false,grid:{display:false}},y:{grid:{display:false},border:{display:false},ticks:{font:{size:12},color:'#2A1622'}}}});

function imgRegional(m){
  const uf=m[1],s=UF_STATS[uf],cap=s.capital,labels=[],data=[],bg=[];
  if(m[4]){ // estado: compara com capital e Brasil
    labels.push(s.nome);data.push(m[3]);bg.push('#E6007E');
    if(cap){labels.push('Capital ('+cap[0]+')');data.push(cap[3]);bg.push('#7C1D4F');}
  } else {
    labels.push(m[0]);data.push(m[3]);bg.push('#E6007E');
    if(cap&&cap[0]!==m[0]){labels.push('Capital ('+cap[0]+')');data.push(cap[3]);bg.push('#B4126A');}
    labels.push('Total '+uf);data.push(s.m);bg.push('#7C1D4F');
  }
  return chartImg({type:'bar',data:{labels,datasets:[{data,backgroundColor:bg,borderRadius:6,barThickness:26}]},
    options:baseOpts('Mulheres 25–64 anos — comparação regional (Censo 2022)')},760,210);
}
function imgFunil(steps){
  const a=steps.slice(0,3),d=steps.slice(3);
  const i1=chartImg({type:'bar',data:{labels:a.map(s=>s[0]),datasets:[{data:a.map(s=>Math.round(s[1])),backgroundColor:['#E6007E','#F0398B','#FF4DA6'],borderRadius:6,barThickness:26}]},
    options:baseOpts('Alcance do programa')},760,190);
  const i2=chartImg({type:'bar',data:{labels:d.map(s=>s[0]),datasets:[{data:d.map(s=>Math.round(s[1])),backgroundColor:['#7C1D4F','#9B2A63','#B4126A','#C81E5B'],borderRadius:6,barThickness:24}]},
    options:baseOpts('Resultados de detecção estimados')},760,230);
  return [i1,i2];
}
function imgCusto(c){
  return chartImg({type:'bar',
    data:{labels:['PinkPapa (kit)','Papanicolau','Tratamento/ano'],datasets:[{data:[c.preco,14.37,10000],backgroundColor:['#E6007E','#C9B2BF','#C81E5B'],borderRadius:6,barThickness:26}]},
    options:Object.assign(baseOpts('Custo unitário comparado (R$, escala log)'),{scales:{x:{type:'logarithmic',display:false,grid:{display:false}},y:{grid:{display:false},border:{display:false},ticks:{font:{size:12},color:'#2A1622'}}}})},760,180);
}

function pnsb(c){
  const m=c.muni,uf=m[1],passo=l=>c.steps.find(s=>s[0]===l)[1];
  const alvo = m[4] ? m[0] : m[0]+'/'+uf;
  const covA=c.premissas[0][1], covM=c.premissas[1][1];
  const ente = m[4] ? 'o estado' : 'o município';
  return {
    problema:'O câncer de colo do útero é o 3º mais frequente entre as brasileiras e a 1ª causa de morte por câncer na América Latina: 17.010 casos novos e mais de 7.100 óbitos por ano no Brasil (INCA; Observatório de Oncologia) — uma mulher a cada 90 minutos. É causado pelo HPV e quase 100% evitável com rastreio de qualidade, mas a citologia (Papanicolau) detecta apenas 55–70% das lesões de alto grau e a cobertura está em queda. Em '+alvo+', a cobertura estimada hoje é de '+covA+', para uma população-alvo de '+m[3].toLocaleString('pt-BR')+' mulheres de 25 a 64 anos (Censo 2022, IBGE).',
    necessidade:'Para levar '+alvo+' à cobertura-meta de '+covM+' (patamar da meta de 70% da OMS), é preciso incluir mais '+fmt(passo('Mulheres adicionais no rastreio'))+' mulheres no rastreio — cerca de '+fmt(c.testes)+' testes, considerando a adesão estimada, executados em '+c.prazo+' meses ('+fmt(c.testesMes)+' testes/mês). O rastreio oportunístico atual e a espera de 4 a 6 meses por consulta deixam muitas mulheres sem qualquer exame.',
    solucao:'O PinkPapa é um autoteste de DNA-HPV homologado pela ANVISA, correspondente ao procedimento SIGTAP 0202100251 (Exame molecular de detecção de HPV), incorporado ao SUS pela Portaria SECTICS/MS nº 3/2024 e financiado por MAC. A autocoleta é feita pela própria mulher em UBS, UPA, centros comunitários ou hospitais — sem espéculo, sem mesa ginecológica, sem constrangimento, com aceitação próxima de 100%. Detecta 28 tipos de HPV (19 de alto risco), com sensibilidade de 90–95% (contra 55–70% do Papanicolau), antecipa o diagnóstico em até 10 anos e permite espaçar o rastreio para 5 anos após resultado negativo, com acompanhamento por inteligência artificial por 5 anos.',
    beneficio:'Com as premissas simuladas, o investimento é de '+fmtMoney(c.custoPrograma)+', detectando ~'+fmt(c.lesoes)+' lesões de alto grau (das quais ~'+fmt(c.lesoesCitoPerde)+' que o Papanicolau perderia), evitando '+fmt(c.casosEvit)+' casos de câncer e '+fmt(c.mortesEvit)+' mortes — a um custo de '+fmtMoney(c.custoPorMorte)+' por morte evitada e retorno socioeconômico de '+(c.roiSoc*100).toFixed(0)+'%. Substituindo (e não somando-se a) o Papanicolau, o DNA-HPV é custo-efetivo e reduz o gasto do SUS no longo prazo (estimativa CONITEC: -30%), alinhando '+ente+' às metas 90-70-90 da OMS e ao indicador de cobertura do Previne Brasil.'
  };
}

function montarPDF(){
  if(!lastCalc){alert('Selecione um município ou estado primeiro.');return null;}
  const c=lastCalc,m=c.muni,uf=m[1],{jsPDF}=window.jspdf;
  const doc=new jsPDF({unit:'pt',format:'a4'});
  const W=doc.internal.pageSize.getWidth(),H=doc.internal.pageSize.getHeight(),M=44;
  const isUF=m[4];
  const alvo = isUF ? m[0] : m[0]+'/'+uf;
  const orgao = isUF ? UF_STATS[uf].orgao : ('Secretaria Municipal de Saúde de '+m[0]+'/'+uf);
  const dest=document.getElementById('in-dest-nome').value.trim();
  const pNome=document.getElementById('in-prop-nome').value.trim()||'G3 Health Service';
  const pMail=document.getElementById('in-prop-email').value.trim()||'g3.healthservice@proton.me';
  const pTel =document.getElementById('in-prop-tel').value.trim();
  const hoje=new Date();
  const ref='PINKPAPA-'+uf+'-'+(isUF?'UF':'MUN')+'-'+hoje.getFullYear()+String(hoje.getMonth()+1).padStart(2,'0')+String(hoje.getDate()).padStart(2,'0');
  let y=0;

  /* gradiente simulado por faixas finas (jsPDF não tem gradiente nativo) */
  function gradiente(x,yy,w,h,c1,c2){
    const N=90;
    for(let i=0;i<N;i++){
      const t=i/(N-1);
      doc.setFillColor(Math.round(c1[0]+(c2[0]-c1[0])*t),Math.round(c1[1]+(c2[1]-c1[1])*t),Math.round(c1[2]+(c2[2]-c1[2])*t));
      doc.rect(x, yy+(h/N)*i, w, h/N+0.7, 'F');
    }
  }
  function barraTopo(){
    doc.setFillColor(...C_PINK);doc.rect(0,0,W,24,'F');
    doc.setTextColor(255);doc.setFont('helvetica','bold');doc.setFontSize(10);doc.text('G3 HEALTH SERVICE',M,16);
    doc.setFont('helvetica','normal');doc.setFontSize(7.5);
    doc.text('PinkPapa · rastreio de câncer de colo do útero por DNA-HPV (autocoleta)',W-M,16,{align:'right'});
  }
  function header(sub){
    barraTopo();
    doc.setTextColor(...C_WINE);doc.setFont('helvetica','bold');doc.setFontSize(13);doc.text('Proposta — '+alvo,M,46);
    doc.setTextColor(...C_GREY);doc.setFont('helvetica','normal');doc.setFontSize(9);doc.text(sub+' · Ref. '+ref,M,60);
    doc.setDrawColor(240,215,230);doc.line(M,68,W-M,68);
    return 84;
  }
  /* rodapé em 2 linhas — numa linha só, contato e fontes se sobrepõem */
  function rodape(){
    const p=doc.internal.getNumberOfPages();
    for(let i=2;i<=p;i++){doc.setPage(i);
      doc.setDrawColor(240,215,230);doc.line(M,H-40,W-M,H-40);
      doc.setFontSize(7.3);doc.setTextColor(150);
      doc.text('G3 Health Service · '+pMail+(pTel?' · '+pTel:''),M,H-28);
      doc.text(i+'/'+p,W-M,H-28,{align:'right'});
      doc.setFontSize(6.8);doc.setTextColor(170);
      doc.text('Fontes: IBGE (Censo 2022), INCA, Obs. de Oncologia, CONITEC/MS, OMS · Apoio à decisão; não substitui diagnóstico médico',M,H-17);}
  }
  /* KPI card */
  function kpi(x,yy,w,h,valor,rot,cor){
    doc.setFillColor(255,255,255);doc.setDrawColor(240,215,230);doc.roundedRect(x,yy,w,h,6,6,'FD');
    doc.setFillColor(...cor);doc.rect(x,yy,3.5,h,'F');
    doc.setTextColor(...cor);doc.setFont('helvetica','bold');doc.setFontSize(15);doc.text(valor,x+12,yy+22);
    doc.setTextColor(...C_GREY);doc.setFont('helvetica','normal');doc.setFontSize(7.8);
    doc.text(doc.splitTextToSize(rot,w-18),x+12,yy+34);
  }

  /* ======== PÁGINA 1 — CAPA hi-tech ======== */
  gradiente(0,0,W,H,[230,0,126],[36,12,26]);
  // grid decorativo
  doc.setDrawColor(255,255,255);doc.setLineWidth(0.3);
  for(let i=1;i<7;i++){doc.setGState(new doc.GState({opacity:0.07}));doc.line(0,H*i/7,W,H*i/7);doc.line(W*i/7,0,W*i/7,H);}
  doc.setGState(new doc.GState({opacity:1}));doc.setLineWidth(1);

  doc.setTextColor(255);doc.setFont('helvetica','bold');doc.setFontSize(11);
  doc.text('G3 HEALTH SERVICE',M,64);
  doc.setFont('helvetica','normal');doc.setFontSize(8.5);doc.setTextColor(255,220,238);
  doc.text('em parceria com PinkLab · PinkPapa',M,78);

  // título: posiciona o subtítulo DEPOIS das linhas reais do título (senão sobrepõe)
  doc.setTextColor(255);doc.setFont('helvetica','bold');doc.setFontSize(30);
  const tLines=doc.splitTextToSize('PROPOSTA TÉCNICA E COMERCIAL',W-2*M-30);
  let ty=172;
  doc.text(tLines,M,ty); ty += tLines.length*33;
  doc.setFont('helvetica','normal');doc.setFontSize(12.5);doc.setTextColor(255,210,234);
  const sLines=doc.splitTextToSize('Programa de rastreio de câncer de colo do útero por teste de DNA-HPV com autocoleta',W-2*M-30);
  doc.text(sLines,M,ty+6);

  // faixa do alvo
  doc.setFillColor(255,255,255);doc.setGState(new doc.GState({opacity:0.12}));
  doc.roundedRect(M,258,W-2*M,62,8,8,'F');doc.setGState(new doc.GState({opacity:1}));
  doc.setTextColor(255,190,225);doc.setFont('helvetica','bold');doc.setFontSize(8);
  doc.text(isUF?'ENTE FEDERATIVO (ESTADUAL)':'MUNICÍPIO',M+16,278);
  doc.setTextColor(255);doc.setFontSize(20);doc.text(alvo,M+16,302);
  doc.setFont('helvetica','normal');doc.setFontSize(9);doc.setTextColor(255,210,234);
  doc.text(fmt(m[3])+' mulheres de 25 a 64 anos (população-alvo)',W-M-16,302,{align:'right'});

  // VALOR DO PROJETO — destaque grande
  doc.setFillColor(255,255,255);
  doc.roundedRect(M,340,W-2*M,104,10,10,'F');
  doc.setFillColor(...C_PINK);doc.rect(M,340,6,104,'F');
  doc.setTextColor(...C_GREY);doc.setFont('helvetica','bold');doc.setFontSize(8);
  doc.text('VALOR TOTAL DO PROJETO (AQUISIÇÃO DOS TESTES)',M+20,364);
  doc.setTextColor(...C_PINK);doc.setFont('helvetica','bold');doc.setFontSize(30);
  doc.text(fmtMoney(c.custoPrograma),M+20,398);
  doc.setTextColor(...C_WINE);doc.setFont('helvetica','normal');doc.setFontSize(9.5);
  doc.text(fmt(c.testes)+' testes × '+fmtMoney(c.preco)+' por kit  ·  execução em '+c.prazo+' meses ('+fmt(c.testesMes)+'/mês)',M+20,420);
  doc.setFontSize(8);doc.setTextColor(...C_GREY);
  doc.text('Financiamento: Média e Alta Complexidade (MAC) · SIGTAP 0202100251',M+20,436);

  // KPIs da capa
  const kw=(W-2*M-24)/3;
  doc.setGState(new doc.GState({opacity:1}));
  kpi(M,468,kw,58,fmt(c.casosEvit),'casos de câncer potencialmente evitados',C_PINK);
  kpi(M+kw+12,468,kw,58,fmt(c.mortesEvit),'mortes potencialmente evitadas',C_WINE);
  kpi(M+2*(kw+12),468,kw,58,(c.roiSoc*100).toFixed(0)+'%','retorno socioeconômico estimado',C_GREEN);

  // destinatário + proponente
  doc.setDrawColor(255,255,255);doc.setGState(new doc.GState({opacity:0.25}));
  doc.line(M,566,W-M,566);doc.setGState(new doc.GState({opacity:1}));
  doc.setTextColor(255,190,225);doc.setFont('helvetica','bold');doc.setFontSize(8);
  doc.text('DESTINATÁRIO',M,588);
  doc.text('PROPONENTE',W/2+10,588);
  doc.setTextColor(255);doc.setFont('helvetica','normal');doc.setFontSize(10);
  doc.text(doc.splitTextToSize(dest||orgao,W/2-M-20),M,604);
  doc.text(doc.splitTextToSize(orgao,W/2-M-20),M,dest?620:620);
  doc.setFont('helvetica','bold');doc.text('G3 Health Service',W/2+10,604);
  doc.setFont('helvetica','normal');doc.setFontSize(9);
  doc.text(pNome,W/2+10,618);
  doc.text(pMail,W/2+10,631);
  if(pTel) doc.text(pTel,W/2+10,644);

  doc.setFontSize(8);doc.setTextColor(255,190,225);
  doc.text('Ref. '+ref,M,H-56);
  doc.text('Brasília/DF, '+dataExtenso(hoje),W-M,H-56,{align:'right'});
  doc.setFontSize(7.5);doc.setTextColor(255,170,215);
  doc.text('Documento gerado com dados oficiais: IBGE (Censo 2022), INCA, Observatório de Oncologia, CONITEC/MS, OMS.',M,H-38);

  /* ======== PÁGINA 2 — PNSB ======== */
  doc.addPage();y=header('Problema · Necessidade · Solução · Benefício (PNSB)');
  const P=pnsb(c);
  function bloco(tit,txt,cor){
    const lines=doc.splitTextToSize(txt,W-2*M-22);
    const h=lines.length*11.5+30;
    doc.setFillColor(252,244,248);doc.roundedRect(M,y,W-2*M,h,6,6,'F');
    doc.setFillColor(...cor);doc.rect(M,y,4,h,'F');
    doc.setTextColor(...cor);doc.setFont('helvetica','bold');doc.setFontSize(10.5);doc.text(tit,M+14,y+18);
    doc.setTextColor(55,42,50);doc.setFont('helvetica','normal');doc.setFontSize(9.2);
    doc.text(lines,M+14,y+32);
    y+=h+12;
  }
  bloco('PROBLEMA',P.problema,[200,30,91]);
  bloco('NECESSIDADE',P.necessidade,C_WINE);
  bloco('SOLUÇÃO',P.solucao,C_PINK);
  bloco('BENEFÍCIO',P.beneficio,C_GREEN);

  /* ======== PÁGINA 3 — EXECUÇÃO (destaque) ======== */
  doc.addPage();y=header('Plano de execução');
  doc.setFillColor(...C_DARK);doc.roundedRect(M,y,W-2*M,52,8,8,'F');
  doc.setTextColor(255);doc.setFont('helvetica','bold');doc.setFontSize(13);
  doc.text('EXECUÇÃO DO PROGRAMA',M+16,y+22);
  doc.setFont('helvetica','normal');doc.setFontSize(9);doc.setTextColor(255,190,225);
  doc.text(fmt(c.testes)+' testes em '+c.prazo+' meses  ·  '+fmt(c.testesMes)+' testes/mês  ·  autocoleta em UBS, UPA, centros comunitários e hospitais',M+16,y+40);
  y+=68;

  doc.autoTable({startY:y,
    head:[['Fase','Atividades','Prazo','Responsável']],
    body:[
      ['1. Planejamento','Pactuação com a Secretaria, definição das unidades de coleta (UBS/UPA/centros comunitários), meta por unidade e cadastro no SISCAN.','Mês 1','G3 + Secretaria'],
      ['2. Capacitação','Treinamento das equipes da Atenção Primária (ACS/enfermagem) para orientar a autocoleta e registrar o procedimento SIGTAP 0202100251.','Mês 1–2','G3 / PinkLab'],
      ['3. Convocação','Busca ativa das mulheres de 25 a 64 anos, priorizando as que nunca se rastrearam; campanha local e agendamento.','Mês 2 em diante','Secretaria + ACS'],
      ['4. Autocoleta','Entrega e retirada do coletor; a mulher realiza a autocoleta sem espéculo e sem constrangimento. Sem necessidade de mesa ginecológica.','Contínuo','Unidades de saúde'],
      ['5. Análise laboratorial','Processamento por PCR com genotipagem (28 tipos de HPV, 19 de alto risco) e emissão de laudo.','Contínuo','PinkLab'],
      ['6. Encaminhamento','Mulheres HPV+ de alto risco encaminhadas à colposcopia/tratamento da lesão precursora (CAF/EZT), fechando a linha de cuidado.','Contínuo','Secretaria'],
      ['7. Monitoramento por IA','Acompanhamento por inteligência artificial por até 5 anos, com painel de cobertura e indicadores (Previne Brasil / metas 90-70-90).','5 anos','G3 + PinkLab'],
    ],
    theme:'grid',headStyles:{fillColor:C_PINK,fontSize:9},styles:{fontSize:8.4,cellPadding:5,lineColor:[240,215,230]},
    columnStyles:{0:{cellWidth:80,fontStyle:'bold',textColor:C_WINE},2:{cellWidth:66},3:{cellWidth:88}},margin:{left:M,right:M}});
  y=doc.lastAutoTable.finalY+16;

  doc.setFillColor(252,244,248);doc.roundedRect(M,y,W-2*M,58,6,6,'F');
  doc.setFillColor(...C_GREEN);doc.rect(M,y,4,58,'F');
  doc.setTextColor(...C_GREEN);doc.setFont('helvetica','bold');doc.setFontSize(10);
  doc.text('ONDE A AUTOCOLETA ACONTECE',M+14,y+18);
  doc.setTextColor(55,42,50);doc.setFont('helvetica','normal');doc.setFontSize(9);
  doc.text(doc.splitTextToSize('UBS · UPA · Centros comunitários · Hospitais · Ações itinerantes. O PinkPapa elimina a necessidade de mesa ginecológica, espéculo, foco de luz e da presença de vários profissionais — o que permite escalar o rastreio sem ampliar a estrutura física instalada.',W-2*M-24),M+14,y+34);

  /* ======== PÁGINA 4 — DIMENSIONAMENTO / GRÁFICOS ======== */
  doc.addPage();y=header('Dimensionamento e alcance');
  const wImg=W-2*M;
  doc.addImage(imgRegional(m),'PNG',M,y,wImg,wImg*210/760);y+=wImg*210/760+6;
  const[i1,i2]=imgFunil(c.steps);
  doc.addImage(i1,'PNG',M,y,wImg,wImg*190/760);y+=wImg*190/760+6;
  doc.addImage(i2,'PNG',M,y,wImg,wImg*230/760);y+=wImg*230/760+6;
  doc.addImage(imgCusto(c),'PNG',M,y,wImg,wImg*180/760);

  /* ======== PÁGINA 5 — INVESTIMENTO ======== */
  doc.addPage();y=header('Investimento e custo-benefício');
  // caixa do valor
  gradiente(M,y,W-2*M,76,[230,0,126],[124,29,79]);
  doc.setTextColor(255,190,225);doc.setFont('helvetica','bold');doc.setFontSize(8);
  doc.text('VALOR TOTAL DA CONTRATAÇÃO / AQUISIÇÃO',M+16,y+22);
  doc.setTextColor(255);doc.setFontSize(26);doc.text(fmtMoney(c.custoPrograma),M+16,y+52);
  doc.setFont('helvetica','normal');doc.setFontSize(9);doc.setTextColor(255,215,238);
  doc.text(fmt(c.testes)+' kits × '+fmtMoney(c.preco),W-M-16,y+38,{align:'right'});
  doc.text('Execução: '+c.prazo+' meses',W-M-16,y+54,{align:'right'});
  y+=92;

  doc.autoTable({startY:y,head:[['Composição do investimento','Quantidade','Unitário','Total']],
    body:[
      ['Kit PinkPapa (autoteste DNA-HPV) — SIGTAP 0202100251',fmt(c.testes),fmtMoney(c.preco),fmtMoney(c.custoPrograma)],
      ['Capacitação das equipes, logística e monitoramento por IA (5 anos)','—','incluso','incluso'],
    ],theme:'grid',headStyles:{fillColor:C_PINK,fontSize:9},styles:{fontSize:8.6,cellPadding:5,lineColor:[240,215,230]},
    columnStyles:{1:{halign:'right'},2:{halign:'right'},3:{halign:'right',fontStyle:'bold',textColor:C_PINK}},margin:{left:M,right:M}});
  y=doc.lastAutoTable.finalY+12;

  doc.autoTable({startY:y,head:[['Retorno estimado para o SUS','Valor']],
    body:[
      ['Custo de tratamento evitado',fmtMoney(c.custoEvitado)],
      ['Custo por câncer evitado',c.custoPorCaso>0?fmtMoney(c.custoPorCaso):'—'],
      ['Custo por morte evitada',c.custoPorMorte>0?fmtMoney(c.custoPorMorte):'—'],
      ['Valor social (mortes evitadas)',fmtMoney(c.valorSocial)],
      ['Retorno socioeconômico',(c.roiSoc*100).toFixed(0)+'%'],
      ['Comparativo — Papanicolau (SIGTAP)','R$ 14,37 / exame (sensibilidade 55–70%)'],
      ['Comparativo — tratamento oncológico','R$ 10.000 / paciente / ano'],
      ['Projeção CONITEC','-30% de custo no longo prazo (substituindo a citologia)'],
    ],theme:'grid',headStyles:{fillColor:C_GREEN,fontSize:9},styles:{fontSize:8.6,cellPadding:5,lineColor:[240,215,230]},
    columnStyles:{1:{halign:'right'}},margin:{left:M,right:M}});
  y=doc.lastAutoTable.finalY+12;

  doc.autoTable({startY:y,head:[['Premissas utilizadas','Valor']],body:c.premissas,
    theme:'grid',headStyles:{fillColor:C_WINE,fontSize:9},styles:{fontSize:8.4,cellPadding:4,lineColor:[240,215,230]},
    columnStyles:{1:{halign:'right'}},margin:{left:M,right:M}});
  y=doc.lastAutoTable.finalY+30;

  if(y>H-120) { doc.addPage(); y=header('Aceite'); y+=10; }
  doc.setDrawColor(190,170,182);
  doc.line(M,y+26,M+210,y+26);doc.line(W-M-210,y+26,W-M,y+26);
  doc.setFontSize(9);doc.setTextColor(60);
  doc.setFont('helvetica','bold');doc.text('G3 Health Service',M,y+40);
  doc.setFont('helvetica','normal');doc.setFontSize(8);doc.setTextColor(120);
  doc.text(pNome+(pTel?' · '+pTel:''),M,y+52);
  doc.setFont('helvetica','bold');doc.setFontSize(9);doc.setTextColor(60);
  doc.text(doc.splitTextToSize(dest||orgao,210),W-M-210,y+40);
  doc.setFont('helvetica','normal');doc.setFontSize(8);doc.setTextColor(120);
  doc.text('Contratante',W-M-210,y+52);
  doc.setFontSize(8);doc.setTextColor(120);
  doc.text('Local e data: ____________________________________, '+dataExtenso(hoje),M,y+80);

  rodape();
  return {doc,ref,alvo};
}

function nomeArq(){ return 'Proposta_PinkPapa_'+(selected?selected[0].replace(/[^\w]/g,'_'):'')+'.pdf'; }
function baixarPDF(){const r=montarPDF();if(r) r.doc.save(nomeArq());}

/* ---------- envio de e-mail DIRETO (Apps Script + MailApp) ---------- */
async function enviarEmail(){
  const r=montarPDF(); if(!r) return;
  const email=document.getElementById('in-dest-email').value.trim();
  const btn=document.getElementById('btnMail'), st=document.getElementById('mailStatus');
  if(!email){ st.style.color='#C81E5B'; st.textContent='Informe o e-mail do destinatário.'; return; }
  const assunto='Proposta PinkPapa — rastreio de câncer de colo do útero ('+r.alvo+')';
  const corpo='Prezado(a) '+(document.getElementById('in-dest-nome').value.trim()||'Gestor(a)')+',\n\n'+
    'Segue em anexo a proposta técnica e comercial do PinkPapa — programa de rastreio de câncer de colo do útero por teste de DNA-HPV com autocoleta — para '+r.alvo+'.\n\n'+
    'Valor total do projeto: '+fmtMoney(lastCalc.custoPrograma)+' ('+fmt(lastCalc.testes)+' testes).\n'+
    'Referência: '+r.ref+'\n\n'+
    'Permaneço à disposição.\n\n'+
    document.getElementById('in-prop-nome').value.trim()+'\nG3 Health Service\n'+
    document.getElementById('in-prop-email').value.trim()+'\n'+document.getElementById('in-prop-tel').value.trim();

  if(!MAIL_ENDPOINT){
    // sem backend: baixa o PDF e abre o compositor JÁ preenchido (sem menu de escolha)
    r.doc.save(nomeArq());
    st.style.color='#7C1D4F';
    st.textContent='Abrindo seu e-mail… anexe o PDF que acabou de baixar.';
    location.href='mailto:'+email+'?subject='+encodeURIComponent(assunto)+'&body='+encodeURIComponent(corpo+'\n\n(Anexe o PDF baixado: '+nomeArq()+')');
    return;
  }
  // com backend: envia de verdade, com anexo, sem sair da página
  btn.disabled=true; st.style.color='#7C1D4F'; st.textContent='Enviando…';
  try{
    const b64 = r.doc.output('datauristring').split(',')[1];
    await fetch(MAIL_ENDPOINT,{method:'POST',mode:'no-cors',
      headers:{'Content-Type':'text/plain;charset=utf-8'},
      body:JSON.stringify({action:'enviarProposta',para:email,assunto,corpo,
        nomeArquivo:nomeArq(),pdfBase64:b64,ref:r.ref,alvo:r.alvo,
        valor:lastCalc.custoPrograma,copia:document.getElementById('in-prop-email').value.trim()})});
    st.style.color='#12A97A'; st.textContent='✅ Proposta enviada para '+email;
  }catch(e){
    st.style.color='#C81E5B'; st.textContent='Falha no envio. Baixando o PDF…'; r.doc.save(nomeArq());
  }finally{ btn.disabled=false; }
}

initUF(); renderRank();
document.getElementById('mailNote').textContent = MAIL_ENDPOINT
  ? 'O e-mail é enviado diretamente pelo servidor, com o PDF em anexo.'
  : 'Envio direto com anexo requer o Apps Script configurado (mail_endpoint.txt). Sem ele, o PDF é baixado e seu cliente de e-mail abre já preenchido.';
</script>
</body>
</html>
"""

out = (HTML.replace("__TOTM__", TOTM_BR).replace("__BUILD__", BUILD)
       .replace("__DATA__", DATA_JS).replace("__UFSTATS__", UFSTATS_JS)
       .replace("__MAIL_ENDPOINT__", MAIL_ENDPOINT)
       .replace("__CHART__", CHART).replace("__JSPDF__", JSPDF).replace("__AUTOTABLE__", AUTOTABLE))

(BASE/"index.html").write_text(out, encoding="utf-8")
(BASE/".nojekyll").write_text("", encoding="utf-8")
print(f"OK: index.html ({len(out)//1024} KB) build {BUILD}")
print(f"Mail endpoint: {'CONFIGURADO' if MAIL_ENDPOINT else 'nao configurado (fallback mailto)'}")
print(f"Brasil 25-64: {TOT_M:,} | {len(muns)} municipios | {len(uf_stats)} UFs")
