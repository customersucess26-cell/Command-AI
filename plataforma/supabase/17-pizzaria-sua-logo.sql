-- Demonstração da pizzaria: logo "SUA LOGO AQUI" no lugar da logo da Fornalha (mostra ao cliente onde entra a marca dele).
update public.lojas set logo_url = '/assets/img/exemplo/fornalha/sua-logo.png' where slug = 'pizzaria';
