-- Cardápio inicial do Bruto Burger (igual ao site). Rode depois do 05-loja-tabelas.sql e do 03-loja-pedidos.sql.
update public.settings set store_name = 'Bruto Burger Co.', hours = 'Terça a domingo, 18h às 23h30', address = 'Rua Exemplo, 123, Centro', instagram = '@brutoburger', delivery_fee = 7 where id = 1;
insert into public.categories (id, name, position) values
  ('burgers', 'Burgers', 1),
  ('frango', 'Frango', 2),
  ('acompanhamentos', 'Acompanhamentos e bebidas', 3),
  ('combos', 'Combos', 4)
on conflict (id) do nothing;
insert into public.products (id, category_id, name, description, price, image_url, badge, position, featured) values
  ('bacon-cheddar', 'burgers', 'Bacon Cheddar', 'Blend 160g, cheddar derretido, bacon crocante e molho barbecue.', 36, 'img/classico.jpg', 'Clássico', 1, true),
  ('barbecue-onion', 'burgers', 'Barbecue Onion', 'Pão brioche escuro, blend, cheddar, onion rings e barbecue defumado.', 39, 'img/barbecue.jpg', 'Mais pedido', 2, true),
  ('trufado', 'burgers', 'Trufado', 'Pão preto, blend, queijo emental, cogumelos e aioli trufado.', 44, 'img/trufado.jpg', 'Novo', 3, true),
  ('duplo-cheddar', 'burgers', 'Duplo Cheddar', 'Dois blends, cheddar duplo, tomate, cebola e alface.', 42, 'img/w2.jpg', '', 4, true),
  ('cheese-salada', 'burgers', 'Cheese Salada', 'Blend, cheddar, tomate, cebola picada, picles e alface.', 34, 'img/w1.jpg', '', 5, false),
  ('bacon-picles', 'burgers', 'Bacon Picles', 'Blend, bacon, cheddar, picles, alface e maionese da casa.', 38, 'img/w3.jpg', '', 6, false),
  ('mexicano', 'burgers', 'Mexicano', 'Blend apimentado, jalapeño, abacate, queijo cotija e nachos.', 40, 'img/mexicano.jpg', '', 7, true),
  ('salmao-grill', 'burgers', 'Salmão Grill', 'Salmão grelhado, molho de abacate e limão, toranja e pepino.', 46, 'img/salmao.jpg', '', 8, false),
  ('halloumi-veggie', 'burgers', 'Halloumi Veggie', 'Queijo halloumi grelhado, pesto, pera e tomate seco.', 37, 'img/halloumi.jpg', '', 9, false),
  ('crispy-chicken', 'frango', 'Crispy Chicken', 'Frango empanado crocante, alface, tomate e molho caesar.', 33, 'img/crispy.jpg', 'Crocante', 1, true),
  ('chicken-cheese', 'frango', 'Chicken Cheese', 'Peito de frango, queijo, tomate, alface e barbecue.', 34, 'img/chicken-cheese.jpg', '', 2, false),
  ('chick-cheddar', 'frango', 'Chick Cheddar', 'Frango crocante, cheddar, tomate, cebola roxa e caesar.', 35, 'img/chick-cheddar.jpg', '', 3, false),
  ('frango-coleslaw', 'frango', 'Frango Coleslaw', 'Frango, salada coleslaw, queijo, alface e barbecue.', 35, 'img/frango-top.jpg', '', 4, false),
  ('nashville-picante', 'frango', 'Nashville Picante', 'Frango frito apimentado, picles, alface e maionese.', 36, 'img/c3.jpg', 'Picante', 5, false),
  ('chicken-grill', 'frango', 'Chicken Grill', 'Peito grelhado, tomate, alface e maionese de ervas.', 33, 'img/c2.jpg', '', 6, false),
  ('crispy-picles', 'frango', 'Crispy Picles', 'Frango empanado, picles, tomate, cebola e alface.', 34, 'img/c1.jpg', '', 7, false),
  ('batata-frita', 'acompanhamentos', 'Batata frita', 'Porção individual, crocante e sequinha.', 16, 'img/batata.jpg', '', 1, false),
  ('batata-com-cheddar', 'acompanhamentos', 'Batata com cheddar', 'Porção grande coberta de cheddar cremoso.', 29, 'img/batata.jpg', '', 2, false),
  ('onion-rings', 'acompanhamentos', 'Onion rings', 'Anéis de cebola com barbecue.', 24, 'img/barbecue.jpg', '', 3, false),
  ('milkshake-400ml', 'acompanhamentos', 'Milkshake 400ml', 'Baunilha, chocolate ou morango.', 21, 'img/w1.jpg', '', 4, false),
  ('refrigerante-lata', 'acompanhamentos', 'Refrigerante lata', '350 ml, gelado.', 7, 'img/w1.jpg', '', 5, false),
  ('combo-classico', 'combos', 'Combo Clássico', 'Cheese Salada, batata frita e refrigerante lata.', 46, 'img/w1.jpg', '', 1, false),
  ('combo-brasa', 'combos', 'Combo Brasa', 'Barbecue Onion, onion rings e milkshake de baunilha.', 62, 'img/barbecue.jpg', 'Mais pedido', 2, false),
  ('combo-trio', 'combos', 'Combo Trio', 'Três mini burgers, batata grande e três bebidas.', 98, 'img/combo.jpg', '', 3, false)
on conflict (id) do nothing;
