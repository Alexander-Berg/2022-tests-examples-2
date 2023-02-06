extension DateTimConverter on String {
  /// Если строчка редставляет из себя
  /// 0123 , где 01 - месяц, а 23 - год
  DateTime toCardFormattedDateTime() => DateTime(
        int.parse('20${substring(2, 4)}'),
        int.parse(substring(0, 2)),
      );
}

extension StringConverter on DateTime {
  /// Превращает день в январе 2017 года в строчку
  /// 0117 , где 01 - месяц, а 17 - год
  String toCardPageFormattedString() =>
      '${month < 10 ? '0$month' : month}${year % 100}';
}
