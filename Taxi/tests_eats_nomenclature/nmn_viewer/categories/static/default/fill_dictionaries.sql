set search_path to eats_nomenclature;

insert into measure_units (id, value,name)
values
(1, 'GRM','г'),
(2, 'KGRM','кг'),
(3, 'LT','л'),
(4, 'MLT','мл');

insert into volume_units (id, value, name)
values
(1, 'CMQ', 'см3'),
(2, 'DMQ', 'дм3');

insert into shipping_types(id, value)
values
(1, 'all'),
(2, 'delivery'),
(3, 'pickup');

insert into barcode_types (value)
values
('ausreply'),
('ausroute'),
('aztec'),
('c25iata'),
('c25ind'),
('c25inter'),
('c25logic'),
('c25matrix'),
('codabar'),
('codablockf'),
('code11'),
('code100'),
('code128'),
('code128b'),
('code16k'),
('code39'),
('code49'),
('code93'),
('daft'),
('datamatrix'),
('dotcode'),
('dpident'),
('dpleit'),
('ean128'),
('ean13'),
('ean14'),
('eanx'),
('eanx_chk'),
('excode39'),
('fim'),
('flat'),
('hanxin'),
('hibc_128'),
('hibc_39'),
('hibc_aztec'),
('hibc_blockf'),
('hibc_dm'),
('hibc_micpdf'),
('hibc_pdf'),
('hibc_qr'),
('isbnx'),
('itf14'),
('japanpost'),
('kix'),
('koreapost'),
('logmars'),
('mailmark'),
('maxicode'),
('micropdf417'),
('microqr'),
('msi_plessey'),
('nve18'),
('onecode'),
('pdf417'),
('pdf417trunc'),
('pharma'),
('pharma_two'),
('planet'),
('plessey'),
('postnet'),
('pzn'),
('qrcode'),
('rm4scc'),
('rss14'),
('rss14stack'),
('rss14stack_omni'),
('rss_exp'),
('rss_expstack'),
('rss_ltd'),
('telepen'),
('telepen_num'),
('upca'),
('upca_chk'),
('upce'),
('upce_chk'),
('vin');

insert into barcode_weight_encodings (value)
values
('none'),
('ean13-tail-gram-4'),
('ean13-tail-gram-5');

insert into marking_types (value)
values
('tobacco'),
('energy_drink'),
('default'),
('marked_light_industry'),
('marked_shoes'),
('marked_tires'),
('marked_parfume');
