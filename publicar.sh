#!/bin/bash
# Regenera o painel PinkPapa e publica no GitHub Pages (g3healthservice/dashboard-pinkpapa)
set -e
cd "$(dirname "$0")"
export PATH="$HOME/bin:$PATH"
python3 gerar_dashboard_pinkpapa.py
cp index.html ~/Downloads/Dashboard_PinkPapa_Municipios.html
git add -A
git commit -q -m "Atualiza painel PinkPapa ($(date +%F' '%H:%M))

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>" || echo "nada a commitar"
git fetch -q origin main && git rebase -q origin/main || true
git push -q origin main
echo "publicado: https://g3healthservice.github.io/dashboard-pinkpapa/"
