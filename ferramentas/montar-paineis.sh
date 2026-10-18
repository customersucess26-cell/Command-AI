#!/bin/sh
# Copia o painel da loja (paineis/loja) e a página de rastreio (paineis/rastreio) para os sites de nicho
# e recalcula a CSP das páginas.
# Rode da raiz do repositório depois de mudar algo em paineis/:  sh ferramentas/montar-paineis.sh
#
# A Padaria & Café (sites/padaria-cafe) tem painel próprio dentro do site (index.html#admin),
# então recebe só o rastreio. Sites sem pedido pelo site (Âmbar) não recebem o rastreio.
set -e
for site in sites/*/; do
  cp .htaccess "${site}.htaccess"
  if [ -f "${site}assets/app.js" ]; then
    : # painel próprio (padaria)
  else
    mkdir -p "${site}admin/vendor"
    cp paineis/loja/index.html paineis/loja/painel.css paineis/loja/painel.js "${site}admin/"
    cp paineis/loja/vendor/* "${site}admin/vendor/"
    cp admin/.htaccess "${site}admin/.htaccess"
  fi
  cp admin/.htaccess "${site}admin/.htaccess"
  if grep -q 'pedidos: *true' "${site}assets/config.js" || [ -f "${site}assets/app.js" ]; then
    cp paineis/rastreio/pedido.html "${site}pedido.html"
    cp paineis/rastreio/pedido.js "${site}assets/pedido.js"
    python3 ferramentas/csp.py "${site}pedido.html"
  fi
  python3 ferramentas/csp.py "${site}index.html" "${site}admin/index.html"
done
