/* Bistrô Connect · cadastro, entrada, criação da loja e aceite de convite.
   A sessão fica no sessionStorage (igual ao painel), então ao abrir /painel/ na mesma aba já está logado.
   Tudo que vem do usuário ou do banco vai para a tela com textContent. */
(function () {
  "use strict";
  var BC = window.BC || {};
  var $ = function (id) { return document.getElementById(id); };
  var PASSOS = ["semConexao", "carregando", "passoConta", "passoConfirmar", "passoNovaSenha", "passoTemLoja", "passoLoja", "passoPronto", "passoConvite"];
  var base = String(BC.site || location.origin).replace(/\/+$/, "");
  var params = new URLSearchParams(location.search);
  var convite = (params.get("convite") || (location.hash.match(/convite=([a-f0-9]{32,64})/) || [])[1] || "").trim();
  if (convite && !/^[a-f0-9]{32,64}$/.test(convite)) convite = "";
  var recuperando = false, db = null;

  function mostra(id) { PASSOS.forEach(function (p) { $(p).hidden = p !== id; }); var h = $(id).querySelector("h2"); if (h) { h.setAttribute("tabindex", "-1"); try { h.focus({ preventScroll: true }); } catch (e) {} } window.scrollTo(0, 0); }
  function erro(el, txt) { el.textContent = txt || ""; el.hidden = !txt; }
  function ocupado(btn, sim, txt) { if (sim) { btn.dataset.txt = btn.textContent; btn.textContent = txt || "Aguarde…"; btn.disabled = true; } else { btn.textContent = btn.dataset.txt || btn.textContent; btn.disabled = false; } }

  function amigavel(e) {
    var m = String((e && (e.message || e.error_description || e.msg)) || e || "");
    if (/invalid login credentials/i.test(m)) return "E-mail ou senha incorretos.";
    if (/email not confirmed/i.test(m)) return "Confirme seu e-mail pelo link que enviamos antes de entrar.";
    if (/already registered|already been registered|user already exists/i.test(m)) return "Já existe uma conta com este e-mail. Use a aba “Já tenho conta”.";
    if (/password.*(at least|should|weak|short)|weak password/i.test(m)) return "Senha fraca. Use pelo menos 10 caracteres, misturando letras, números e símbolos.";
    if (/rate limit|too many|security purposes|over_email_send_rate/i.test(m)) return "Muitas tentativas seguidas. Espere alguns minutos e tente de novo.";
    if (/invalid.*email|unable to validate email/i.test(m)) return "E-mail inválido.";
    if (/signups? not allowed|signup.*disabled/i.test(m)) return "Os cadastros estão fechados no momento. Fale com o suporte.";
    if (/failed to fetch|network|load failed/i.test(m)) return "Sem conexão. Confira a internet e tente de novo.";
    if (/jwt|token.*expired|not authenticated/i.test(m)) return "Sua sessão expirou. Entre de novo.";
    if (/[a-zà-ú]{4}/i.test(m) && m.length < 160 && !/[{}<>]/.test(m)) return m;
    return "Não foi possível concluir agora. Tente de novo.";
  }

  if (!BC.supabaseUrl || !BC.supabaseKey || !window.supabase) { mostra("semConexao"); return; }
  db = window.supabase.createClient(BC.supabaseUrl.replace(/\/+$/, ""), BC.supabaseKey,
    { auth: { storage: window.sessionStorage, persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
  $("prefixoSlug").textContent = base.replace(/^https?:\/\//, "") + "/l/";

  /* ---------- abas criar / entrar ---------- */
  function aba(criar) {
    $("abaCriar").setAttribute("aria-selected", String(criar));
    $("abaEntrar").setAttribute("aria-selected", String(!criar));
    $("formCriar").hidden = !criar; $("formEntrar").hidden = criar;
    $("tituloConta").textContent = criar ? "Crie sua conta" : "Entre na sua conta";
    $("dicaConta").textContent = convite ? "Entre ou crie a conta com o e-mail que recebeu o convite." : criar ? "É com ela que você entra no painel da loja." : "Use o e-mail e a senha do cadastro.";
    erro($("msgConta"), "");
  }
  $("abaCriar").addEventListener("click", function () { aba(true); });
  $("abaEntrar").addEventListener("click", function () { aba(false); });

  /* força da senha */
  $("cSenha").addEventListener("input", function () {
    var s = this.value, p = 0;
    if (s.length >= 10) p++; if (s.length >= 14) p++;
    if (/[a-z]/.test(s) && /[A-Z]/.test(s)) p++; if (/\d/.test(s)) p++; if (/[^A-Za-z0-9]/.test(s)) p++;
    var b = $("forcaBarra"), cores = ["#B3261E", "#B3261E", "#E2852B", "#F2B544", "#2F7A55", "#2F7A55"];
    b.style.width = Math.max(8, p * 20) + "%"; b.style.background = cores[p];
    $("cSenhaDica").textContent = s.length && s.length < 10 ? "Faltam " + (10 - s.length) + " caracteres." : p >= 4 ? "Senha forte." : "Pelo menos 10 caracteres. Misture letras, números e símbolos.";
  });

  $("formCriar").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var nome = $("cNome").value.trim(), email = $("cEmail").value.trim().toLowerCase(), senha = $("cSenha").value, btn = $("btnCriar");
    if (nome.length < 2) return erro($("msgConta"), "Informe seu nome.");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) return erro($("msgConta"), "Informe um e-mail válido.");
    if (senha.length < 10) return erro($("msgConta"), "A senha precisa de pelo menos 10 caracteres.");
    if (!$("cAceite").checked) return erro($("msgConta"), "Para continuar, aceite os Termos de uso e a Política de privacidade.");
    erro($("msgConta"), ""); ocupado(btn, true, "Criando conta…");
    var volta = base + "/entrar.html" + (convite ? "?convite=" + convite : "");
    db.auth.signUp({ email: email, password: senha, options: { data: { name: nome }, emailRedirectTo: volta } })
      .then(function (r) {
        if (r.error) throw r.error;
        if (r.data && r.data.user && Array.isArray(r.data.user.identities) && r.data.user.identities.length === 0)
          throw new Error("User already registered");
        if (r.data && r.data.session) return continuar();
        $("emailEnviado").textContent = email; mostra("passoConfirmar");
      })
      .catch(function (e) { erro($("msgConta"), amigavel(e)); })
      .then(function () { ocupado(btn, false); });
  });

  $("formEntrar").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var email = $("eEmail").value.trim().toLowerCase(), senha = $("eSenha").value, btn = $("btnEntrar");
    if (!email || !senha) return erro($("msgConta"), "Informe e-mail e senha.");
    erro($("msgConta"), ""); ocupado(btn, true, "Entrando…");
    db.auth.signInWithPassword({ email: email, password: senha })
      .then(function (r) { if (r.error) throw r.error; return continuar(); })
      .catch(function (e) { erro($("msgConta"), amigavel(e)); })
      .then(function () { ocupado(btn, false); });
  });

  $("btnEsqueci").addEventListener("click", function () {
    var email = $("eEmail").value.trim().toLowerCase(), msg = $("msgConta");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) { erro(msg, "Digite seu e-mail acima e toque de novo em “Esqueci a senha”."); $("eEmail").focus(); return; }
    db.auth.resetPasswordForEmail(email, { redirectTo: base + "/entrar.html" }).then(function (r) {
      if (r.error) throw r.error;
      msg.className = "msg ok"; erro(msg, "Se existir uma conta com este e-mail, enviamos um link para criar uma nova senha.");
    }).catch(function (e) { msg.className = "msg erro"; erro(msg, amigavel(e)); });
  });
  $("btnVoltarConta").addEventListener("click", function () { mostra("passoConta"); aba(true); });

  $("formNovaSenha").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var s = $("nSenha").value;
    if (s.length < 10) return erro($("msgSenha"), "A senha precisa de pelo menos 10 caracteres.");
    db.auth.updateUser({ password: s }).then(function (r) {
      if (r.error) throw r.error; recuperando = false; return continuar();
    }).catch(function (e) { erro($("msgSenha"), amigavel(e)); });
  });

  /* ---------- depois de logado ---------- */
  function continuar() {
    if (convite) return aceitarConvite();
    return db.rpc("minhas_lojas").then(function (r) {
      if (r.error) throw r.error;
      var lojas = r.data || [];
      if (lojas.length) {
        var ul = $("listaLojas"); ul.textContent = "";
        lojas.forEach(function (l, i) {
          var li = document.createElement("li"), b = document.createElement("b"), sp = document.createElement("span");
          b.textContent = String(i + 1); sp.textContent = l.store_name + " · " + ({ dono: "dono", gerente: "gerente", atendente: "atendente", cozinha: "cozinha" }[l.papel] || l.papel);
          li.appendChild(b); li.appendChild(sp); ul.appendChild(li);
        });
        mostra("passoTemLoja");
      } else abrirLoja();
    }).catch(function (e) { mostra("passoConta"); aba(false); erro($("msgConta"), amigavel(e)); });
  }

  function aceitarConvite() {
    mostra("passoConvite");
    return db.rpc("aceitar_convite", { p_token: convite }).then(function (r) {
      if (r.error) throw r.error;
      convite = "";
      try { history.replaceState(null, "", "/entrar.html"); } catch (e) {}
      location.href = "/painel/";
    }).catch(function (e) {
      $("passoConvite").querySelector("h2").textContent = "Não deu para aceitar o convite";
      erro($("msgConvite"), amigavel(e));
      $("btnConvitePainel").hidden = false;
    });
  }

  /* ---------- criar loja ---------- */
  var TIPOS = [
    ["padaria", "Padaria", '<path d="M4 15c0-5 3.6-9 8-9s8 4 8 9v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M9 9l1.5 4M15 9l-1.5 4M12 8v5"/>'],
    ["cafeteria", "Cafeteria", '<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8 3c0 1.5 1 1.5 1 3M12 3c0 1.5 1 1.5 1 3"/>'],
    ["hamburgueria", "Hamburgueria", '<path d="M4 11a8 8 0 0 1 16 0z"/><path d="M3 14h18"/><path d="M4 17h16a0 0 0 0 1 0 0 3 3 0 0 1-3 3H7a3 3 0 0 1-3-3z"/>'],
    ["pizzaria", "Pizzaria", '<path d="M12 21L3 6a14 14 0 0 1 18 0z"/><circle cx="10" cy="10" r="1.2"/><circle cx="14" cy="13" r="1.2"/><circle cx="12" cy="16.5" r="1"/>'],
    ["restaurante", "Restaurante", '<path d="M6 3v8a2 2 0 0 0 2 2v8M10 3v8a2 2 0 0 1-2 2M8 3v6"/><path d="M17 21V3c-2 1-3 4-3 8h3"/>'],
    ["doceria", "Doceria", '<path d="M5 12h14l-1.5 9h-11z"/><path d="M7 12a5 5 0 0 1 10 0"/><circle cx="12" cy="5" r="1.5"/>'],
    ["outro", "Outro", '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M9 12h6M12 9v6"/>']
  ];
  var caixa = $("tipos");
  TIPOS.forEach(function (t, i) {
    var lab = document.createElement("label"); lab.className = "tipo";
    var inp = document.createElement("input"); inp.type = "radio"; inp.name = "modelo"; inp.value = t[0]; if (i === 0) inp.required = true;
    var sp = document.createElement("span");
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none"); svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "1.8"); svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round"); svg.setAttribute("aria-hidden", "true");
    svg.innerHTML = t[2]; /* ícones fixos deste arquivo, sem dado do usuário */
    sp.appendChild(svg); sp.appendChild(document.createTextNode(t[1]));
    lab.appendChild(inp); lab.appendChild(sp); caixa.appendChild(lab);
  });

  function paraSlug(s) {
    return String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/&/g, " e ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").replace(/-{2,}/g, "-").slice(0, 40).replace(/-+$/, "");
  }
  var slugMexido = false, timerSlug = null, ultimoSlug = "";
  function slugValido(s) { return /^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$/.test(s); }
  function disp(txt, cls) { var d = $("slugDisp"); d.textContent = txt; d.className = "disp" + (cls ? " " + cls : ""); }
  function confereSlug() {
    var s = $("lSlug").value;
    clearTimeout(timerSlug);
    if (!s) return disp("Use letras minúsculas, números e hífen.");
    if (!slugValido(s)) return disp("De 3 a 40 caracteres: letras minúsculas, números e hífen (sem hífen no começo ou no fim).", "nao");
    disp("Conferindo…");
    timerSlug = setTimeout(function () {
      ultimoSlug = s;
      fetch(BC.supabaseUrl.replace(/\/+$/, "") + "/rest/v1/lojas?select=slug&slug=eq." + encodeURIComponent(s), {
        headers: { apikey: BC.supabaseKey, Authorization: "Bearer " + BC.supabaseKey }
      }).then(function (r) { return r.ok ? r.json() : []; }).then(function (l) {
        if (s !== $("lSlug").value) return;
        if (Array.isArray(l) && l.length) disp("Esse endereço já está em uso. Tente outro.", "nao");
        else disp("Endereço livre: " + base.replace(/^https?:\/\//, "") + "/l/" + s, "ok");
      }).catch(function () { disp("Não deu para conferir agora. Confirmamos ao criar a loja."); });
    }, 450);
  }
  $("lNome").addEventListener("input", function () { if (!slugMexido) { $("lSlug").value = paraSlug(this.value); confereSlug(); } });
  $("lSlug").addEventListener("input", function () {
    slugMexido = true;
    var pos = this.value; var limpo = pos.toLowerCase().replace(/[^a-z0-9-]/g, "-").replace(/-{2,}/g, "-").slice(0, 40);
    if (limpo !== this.value) this.value = limpo;
    confereSlug();
  });

  $("lZap").addEventListener("input", function () {
    var d = this.value.replace(/\D/g, "");
    if (d.length > 11 && d.indexOf("55") === 0) d = d.slice(2);
    d = d.slice(0, 11);
    var f = d;
    if (d.length > 2) f = "(" + d.slice(0, 2) + ") " + d.slice(2);
    if (d.length > 7) f = "(" + d.slice(0, 2) + ") " + d.slice(2, d.length - 4) + "-" + d.slice(-4);
    this.value = f;
  });

  function abrirLoja() { $("btnLoja").disabled = false; mostra("passoLoja"); }
  $("btnOutraLoja").addEventListener("click", abrirLoja);

  $("formLoja").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var nome = $("lNome").value.trim(), slug = $("lSlug").value.trim(), msg = $("msgLoja"), btn = $("btnLoja");
    var modelo = (document.querySelector('input[name="modelo"]:checked') || {}).value || "";
    var fone = $("lZap").value.replace(/\D/g, "");
    if (nome.length < 2) { $("lNome").focus(); return erro(msg, "Informe o nome da loja."); }
    if (!slugValido(slug)) { $("lSlug").focus(); return erro(msg, "Confira o endereço da loja: de 3 a 40 caracteres, letras minúsculas, números e hífen."); }
    if (!modelo) return erro(msg, "Escolha o tipo do seu negócio.");
    if (fone.length < 10 || fone.length > 11) { $("lZap").focus(); return erro(msg, "Informe o WhatsApp da loja com DDD."); }
    erro(msg, ""); ocupado(btn, true, "Criando a loja…");
    db.rpc("criar_loja", { p_nome: nome, p_slug: slug, p_modelo: modelo, p_whatsapp: fone }).then(function (r) {
      if (r.error) {
        if (r.error.hint === "SLUG") { disp("Esse endereço já está em uso. Tente outro.", "nao"); $("lSlug").focus(); }
        throw r.error;
      }
      var url = base + "/l/" + (r.data && r.data.slug || slug);
      $("nomeCriada").textContent = nome;
      $("linkLoja").textContent = url;
      mostra("passoPronto");
    }).catch(function (e) { erro(msg, amigavel(e)); })
      .then(function () { ocupado(btn, false); });
  });

  $("btnCopiar").addEventListener("click", function () {
    var t = $("linkLoja").textContent, b = this;
    var ok = function () { b.textContent = "Copiado!"; setTimeout(function () { b.textContent = "Copiar"; }, 1800); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, function () { window.prompt("Copie o link:", t); });
    else window.prompt("Copie o link:", t);
  });

  /* ---------- início ---------- */
  db.auth.onAuthStateChange(function (evento) {
    if (evento === "PASSWORD_RECOVERY") { recuperando = true; mostra("passoNovaSenha"); }
  });
  db.auth.getSession().then(function (r) {
    if (recuperando) return;
    if (r.data && r.data.session) return continuar();
    mostra("passoConta");
    aba(!convite);
  }).catch(function () { mostra("passoConta"); aba(!convite); });
})();
