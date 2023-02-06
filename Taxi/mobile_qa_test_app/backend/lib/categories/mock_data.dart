import 'package:models/models.dart';

final categories = [
  Category(
    id: 'c1',
    title: 'Овощи и фрукты',
    imageUrl: 'https://spb.selhozproduct.ru/upload/usl/f_60ae9702075f9.jpg',
    categories: subcategories,
  ),
  Category(
    id: 'c2',
    title: 'Конфеты и шоколад',
    imageUrl:
        'https://mykaleidoscope.ru/uploads/posts/2021-10/1633076878_12-mykaleidoscope-ru-p-rossip-konfet-krasivo-foto-15.jpg',
    categories: subcategories,
  ),
];

final subcategories = [
  Category(
    id: 'sc1',
    title: 'Овощи',
    imageUrl: 'https://traveltimes.ru/wp-content/uploads/2021/08/vege-2.jpg',
    products: products,
  ),
  Category(
    id: 'sc2',
    title: 'Фрукты',
    imageUrl:
        'https://1culinary.ru/wp-content/uploads/2019/06/gf-pRx2-Mt3M-a52w_owoce-wartosci-odzywcze-witaminy-jakie-sa-rodzaje-owocow-1920x1080-nocrop.jpg',
    products: products,
  ),
];

final products = [
  Product(
    id: 'p1',
    name: 'Ананас',
    imageUrl:
        'https://greensotka.ru/wp-content/uploads/2019/10/1-plody-ananasa.jpg',
    priceUnit: PriceUnit.rub,
    price: 123,
    fullName: 'Ананс вкусный',
    count: 5,
    typeCount: CountType.killograms,
    parameters: parametrs,
  ),
  Product(
    id: 'p2',
    name: 'Яблоко',
    imageUrl: 'https://echo-ua.media/wp-content/uploads/2021/09/4778196.jpg',
    priceUnit: PriceUnit.rub,
    price: 345,
    fullName: 'Яблоко вкусное',
    count: 10,
    typeCount: CountType.killograms,
    parameters: parametrs,
  ),
];

final parametrs = [
  const ProductParameter(
    name: 'Цвет',
    value: 'Желто-Красный',
    id: '123',
  ),
];
