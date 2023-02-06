import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';

const supportedLocals = [
  Locale.fromSubtags(
    languageCode: 'ru',
    countryCode: 'RU',
  ),
];

const localizationsDelegates = AppLocalizations.localizationsDelegates;

class Strings {
  static AppLocalizations of(BuildContext context) =>
      // ignore: avoid-non-null-assertion
      AppLocalizations.of(context)!;
}
