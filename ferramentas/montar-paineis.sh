#!/bin/sh
# Copia o painel da loja (paineis/loja) para cada site de nicho e recalcula a CSP das páginas.
# Rode da raiz do repositório depois de mudar algo em paineis/loja:  sh ferramentas/montar-paineis.sh
set -e
for site in sites/*/; do
  mkdir -p "${site}admin/vendor"
  cp paineis/loja/index.html paineis/loja/painel.css paineis/loja/painel.js "${site}admin/"
  cp paineis/loja/vendor/* "${site}admin/vendor/"
  cp admin/.htaccess "${site}admin/.htaccess"
  cp .htaccess "${site}.htaccess"
  python3 ferramentas/csp.py "${site}index.html" "${site}admin/index.html"
done
