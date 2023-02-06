import 'package:flutter/foundation.dart';

@immutable
class Country implements Comparable<Country> {
  const Country({
    required this.name,
    required this.countryCode,
    required this.defaultLocale,
    required this.phoneCode,
    required this.phoneFormat,
    required this.phoneMask,
  });

  factory Country.fromJson(Map<String, dynamic> json) => Country(
        name: json['name'] as String,
        countryCode: json['countryCode'] as String,
        defaultLocale: json['defaultLocale'] as String,
        phoneCode: json['phoneCode'] as String,
        phoneFormat: json['phoneFormat'] as String,
        phoneMask: json['phoneMask'] as String,
      );

  final String name;

  final String countryCode;

  final String defaultLocale;

  final String phoneCode;

  final String phoneFormat;

  final String phoneMask;

  static const List<Country> supportedCountries = <Country>[
    Country(
      name: 'Азербайджан',
      countryCode: 'AZ',
      defaultLocale: 'az',
      phoneCode: '+994',
      phoneMask: '[00] [000]-[0000]',
      phoneFormat: '90 000-0000',
    ),
    Country(
      name: 'Армения',
      countryCode: 'AM',
      defaultLocale: 'hy',
      phoneCode: '+374',
      phoneMask: '[00] [000]-[000]',
      phoneFormat: '90 000-000',
    ),
    Country(
      name: 'Беларусь',
      countryCode: 'BY',
      defaultLocale: 'ru',
      phoneCode: '+375',
      phoneMask: '[00] [000]-[00]-[00]',
      phoneFormat: '90 000-00-00',
    ),
    Country(
      name: 'Великобритания',
      countryCode: 'GB',
      defaultLocale: 'en',
      phoneCode: '+44',
      phoneMask: '[00]-[00]-[00]-[00]-[00]',
      phoneFormat: '(00)-00-00-00-00',
    ),
    Country(
      name: 'Гана',
      countryCode: 'GH',
      defaultLocale: 'en',
      phoneCode: '+223',
      phoneMask: '[00] [00]-[00]-[009]',
      phoneFormat: '90 00-00-000',
    ),
    Country(
      name: 'Германия',
      countryCode: 'DE',
      defaultLocale: 'en',
      phoneCode: '+7',
      phoneMask: '([00]) [0000]-[0009999]',
      phoneFormat: '(00) 0000-0009999',
    ),
    Country(
      name: 'Грузия',
      countryCode: 'GE',
      defaultLocale: 'ka',
      phoneCode: '+995',
      phoneMask: '[000] [00]-[00]-[00]',
      phoneFormat: '900 00-00-00',
    ),
    Country(
      name: 'Израиль',
      countryCode: 'IL',
      defaultLocale: 'he',
      phoneCode: '+972',
      phoneMask: '([00]) [000]-[00]-[00]',
      phoneFormat: '(90) 000-00-00',
    ),
    Country(
      name: 'Казахстан',
      countryCode: 'KZ',
      defaultLocale: 'kk',
      phoneCode: '+7',
      phoneMask: '[000] [000]-[00]-[00]',
      phoneFormat: '900 000-00-00',
    ),
    Country(
      name: 'Камерун',
      countryCode: 'CM',
      defaultLocale: 'fr',
      phoneCode: '+237',
      phoneMask: '[0] [00]-[00]-[00]-[00]',
      phoneFormat: '0 00-00-00-00',
    ),
    Country(
      name: 'Киргизия',
      countryCode: 'KG',
      defaultLocale: 'ky',
      phoneCode: '+996',
      phoneMask: '[000] [000]-[000]',
      phoneFormat: '900 000-000',
    ),
    Country(
      name: 'Кот-д’Ивуар',
      countryCode: 'CI',
      defaultLocale: 'fr',
      phoneCode: '+225',
      phoneMask: '[00] [00]-[00]-[00]-[09]',
      phoneFormat: '90 00-00-00-00',
    ),
    Country(
      name: 'Латвия',
      countryCode: 'LV',
      defaultLocale: 'lv',
      phoneCode: '+371',
      phoneMask: '[000] [000]-[00]',
      phoneFormat: '900 000-00',
    ),
    Country(
      name: 'Литва',
      countryCode: 'LT',
      defaultLocale: 'lt',
      phoneCode: '+370',
      phoneMask: '([000]) 00-000',
      phoneFormat: '(000) 00 000',
    ),
    Country(
      name: 'Молдавия',
      countryCode: 'MD',
      defaultLocale: 'ro',
      phoneCode: '+373',
      phoneMask: '[00] [000]-[000]',
      phoneFormat: '90 000-000',
    ),
    Country(
      name: 'Норвегия',
      countryCode: 'NO',
      defaultLocale: 'no',
      phoneCode: '+47',
      phoneMask: '([00]) [00]-[00]-[00]',
      phoneFormat: '(00) 00-00-00',
    ),
    Country(
      name: 'Оман',
      countryCode: 'OM',
      defaultLocale: 'ar',
      phoneCode: '+968',
      phoneMask: '[0000]-[0000]',
      phoneFormat: '0000-0000',
    ),
    Country(
      name: 'Россия',
      countryCode: 'RU',
      defaultLocale: 'ru',
      phoneCode: '+7',
      phoneMask: '[000] [000]-[00]-[00]',
      phoneFormat: '+7 900 000-00-00',
    ),
    Country(
      name: 'Румыния',
      countryCode: 'RO',
      defaultLocale: 'ro',
      phoneCode: '+40',
      phoneMask: '[000] [000] [000]',
      phoneFormat: '(000) 000 000',
    ),
    Country(
      name: 'Сенегал',
      countryCode: 'SN',
      defaultLocale: 'fr',
      phoneCode: '+221',
      phoneMask: '[000] [00]-[00]-[00]',
      phoneFormat: '000 00-00-00',
    ),
    Country(
      name: 'Сербия',
      countryCode: 'RS',
      defaultLocale: 'sr',
      phoneCode: '+381',
      phoneMask: '[00] [000]-[00]-[09]',
      phoneFormat: '90 000-00-00',
    ),
    Country(
      name: 'Узбекистан',
      countryCode: 'UZ',
      defaultLocale: 'uz',
      phoneCode: '+998',
      phoneMask: '[00] [000]-[00]-[00]',
      phoneFormat: '99 000-00-00',
    ),
    Country(
      name: 'Украина',
      countryCode: 'UA',
      defaultLocale: 'uk',
      phoneCode: '+380',
      phoneMask: '[00] [000]-[00]-[00]',
      phoneFormat: '90 000-00-00',
    ),
    Country(
      name: 'Финляндия',
      countryCode: 'FI',
      defaultLocale: 'fi',
      phoneCode: '+358',
      phoneMask: '([00]) [000]-[00]-[00]',
      phoneFormat: '(40) 000-00-00',
    ),
    Country(
      name: 'Франция',
      countryCode: 'FR',
      defaultLocale: 'fr',
      phoneCode: '+33',
      phoneMask: '[00]-[00]-[00]-[00]-[00]',
      phoneFormat: '00-00-00-00-00',
    ),
    Country(
      name: 'Чили',
      countryCode: 'CL',
      defaultLocale: 'en',
      phoneCode: '+7',
      phoneMask: '[000] [000]-[00]-[00]',
      phoneFormat: '900 000-00-00',
    ),
    Country(
      name: 'Эстония',
      countryCode: 'EE',
      defaultLocale: 'et',
      phoneCode: '+372',
      phoneMask: '[00] [00]-[00]-[09]',
      phoneFormat: '90 00-00-00',
    ),
    Country(
      name: 'Южно-Африканская Республика',
      countryCode: 'ZA',
      defaultLocale: 'en',
      phoneCode: '+27',
      phoneMask: '[00] [00]-[00]-[009]',
      phoneFormat: '90 00-00-000',
    ),
  ];

  @override
  int get hashCode =>
      name.hashCode ^
      countryCode.hashCode ^
      defaultLocale.hashCode ^
      phoneCode.hashCode ^
      phoneFormat.hashCode ^
      phoneMask.hashCode;
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Country &&
          runtimeType == other.runtimeType &&
          name == other.name &&
          countryCode == other.countryCode &&
          defaultLocale == other.defaultLocale &&
          phoneCode == other.phoneCode &&
          phoneFormat == other.phoneFormat &&
          phoneMask == other.phoneMask;
  @override
  int compareTo(Country other) => defaultLocale.compareTo(other.defaultLocale);
  Country copyWith({
    String? name,
    String? countryCode,
    String? defaultLocale,
    String? phoneCode,
    String? phoneFormat,
    String? phoneMask,
  }) =>
      Country(
        name: name ?? this.name,
        countryCode: countryCode ?? this.countryCode,
        defaultLocale: defaultLocale ?? this.defaultLocale,
        phoneCode: phoneCode ?? this.phoneCode,
        phoneFormat: phoneFormat ?? this.phoneFormat,
        phoneMask: phoneMask ?? this.phoneMask,
      );
  Map<String, dynamic> toJson() => <String, dynamic>{
        'name': name,
        'countryCode': countryCode,
        'defaultLocale': defaultLocale,
        'phoneCode': phoneCode,
        'phoneFormat': phoneFormat,
        'phoneMask': phoneMask,
      };
}
