<?php
/* Bistrô Connect · funções do link de acompanhamento do pedido (usadas por pedido.php e og.php).
   Lê o pedido pela função pública rastrear_pedido do Supabase, com a chave anon de assets/config.js,
   e devolve só o que o cliente já vê na página: itens, valores e status. Nunca telefone nem endereço. */
if (basename($_SERVER['SCRIPT_FILENAME'] ?? '') === basename(__FILE__)) { http_response_code(403); exit; }

function cfg(): array {
    static $c = null;
    if ($c !== null) return $c;
    $c = ['url' => '', 'key' => '', 'site' => ''];
    $txt = @file_get_contents(__DIR__ . '/assets/config.js');
    if ($txt !== false) {
        if (preg_match('/supabaseUrl:\s*"([^"]*)"/', $txt, $m)) $c['url'] = $m[1];
        if (preg_match('/supabaseKey:\s*"([^"]*)"/', $txt, $m)) $c['key'] = $m[1];
        if (preg_match('/\bsite:\s*"([^"]*)"/', $txt, $m)) $c['site'] = $m[1];
    }
    if (getenv('BC_SUPABASE_URL')) $c['url'] = getenv('BC_SUPABASE_URL');   // só para testes locais
    if (getenv('BC_SUPABASE_KEY')) $c['key'] = getenv('BC_SUPABASE_KEY');
    $c['url'] = rtrim($c['url'], '/');
    return $c;
}

function site_url(): string {
    $s = rtrim(cfg()['site'], '/');
    if ($s !== '') return $s;
    $host = preg_replace('/[^A-Za-z0-9.:-]/', '', $_SERVER['HTTP_HOST'] ?? 'localhost');
    return 'https://' . $host;
}

function codigo_valido($c): bool {
    return is_string($c) && preg_match('/^([a-f0-9]{16}|[a-f0-9]{32,64})$/', $c) === 1;
}

function busca_pedido(string $codigo, string $rpc = 'rastrear_pedido'): ?array {
    $c = cfg();
    if ($c['url'] === '' || $c['key'] === '' || !codigo_valido($codigo)) return null;
    $url = (getenv('BC_REST_BASE') ?: $c['url'] . '/rest/v1') . '/rpc/' . $rpc;   // BC_REST_BASE: só para testes locais
    $corpo = json_encode([$rpc === 'cartao_pedido' ? 'p_code' : 'p_token' => $codigo]);
    $cab = ['apikey: ' . $c['key'], 'Authorization: Bearer ' . $c['key'], 'Content-Type: application/json', 'Accept: application/json'];
    $resp = false;
    if (function_exists('curl_init')) {
        $h = curl_init($url);
        curl_setopt_array($h, [CURLOPT_POST => true, CURLOPT_POSTFIELDS => $corpo, CURLOPT_HTTPHEADER => $cab,
            CURLOPT_RETURNTRANSFER => true, CURLOPT_CONNECTTIMEOUT => 4, CURLOPT_TIMEOUT => 6]);
        $resp = curl_exec($h);
        $http = curl_getinfo($h, CURLINFO_HTTP_CODE);
        curl_close($h);
        if ($http < 200 || $http >= 300) $resp = false;
    } else {
        $ctx = stream_context_create(['http' => ['method' => 'POST', 'header' => implode("\r\n", $cab), 'content' => $corpo, 'timeout' => 6]]);
        $resp = @file_get_contents($url, false, $ctx);
    }
    if ($resp === false || $resp === '' || $resp === 'null') return null;
    $j = json_decode($resp, true);
    return is_array($j) && isset($j['code']) ? $j : null;
}

if (!function_exists('mb_strlen')) {      // hospedagem sem mbstring: versões simples
    function mb_strlen($t) { return preg_match_all('/./us', (string)$t); }
    function mb_substr($t, $ini, $len = null) { preg_match_all('/./us', (string)$t, $m); return implode('', array_slice($m[0], $ini, $len)); }
}

/* cartão completo (com nome, telefone e endereço): só para quem tem o código de 16 caracteres */
function busca_cartao(string $codigo): ?array { return preg_match('/^[a-f0-9]{16}$/', $codigo) ? busca_pedido($codigo, 'cartao_pedido') : null; }

function reais($v): string { return 'R$ ' . number_format((float)$v, 2, ',', '.'); }

function rotulo_status(array $p): string {
    $entrega = ($p['delivery_type'] ?? '') === 'entrega';
    $map = ['novo' => 'Pedido recebido', 'confirmado' => 'Confirmado', 'em_preparo' => 'Em preparo',
            'pronto' => $entrega ? 'Saiu para entrega' : (!empty($p['mesa']) ? 'Pronto para servir' : 'Pronto para retirar'),
            'entregue' => $entrega ? 'Entregue' : (!empty($p['mesa']) ? 'Servido' : 'Retirado'), 'cancelado' => 'Cancelado'];
    return $map[$p['status'] ?? ''] ?? 'Pedido recebido';
}

function esc(string $t): string { return htmlspecialchars($t, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
