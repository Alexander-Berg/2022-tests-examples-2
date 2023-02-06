import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';
import '../../build/providers.dart';

import 'models/validation_rules.dart';

final validationRulesProvider = Provider(
  (ref) {
    final cardCvvInputLength4 = ref.watch(
      isBrokenProvider(BugIds.cardCvvInputLength4),
    );

    return ValidationRules(
      isCvvValid: cardCvvInputLength4 ? BrokenValidationRules.isCvvValid : null,
    );
  },
);
