import '../../converters/date_time_converter.dart';

class ValidationRules {
  //Возможно в будущем будет выделен класс ValidationRule
  final bool Function(String) isPhoneValid;
  final bool Function(String) isSmsValid;
  final bool Function(String) isCvvValid;
  final bool Function(String) isCardNumberValid;
  final bool Function(String) isOwnerValid;
  final bool Function(String) isValidityPeriodValid;
  final bool Function(String) isNameValid;
  final bool Function(String) isCodeValid;
  final bool Function(String) isBuildCodeValid;
  final bool Function(String) isCityValid;
  final bool Function(String) isStreetValid;
  final bool Function(String) isHouseValid;
  final bool Function(String) isCorpusValid;
  final bool Function(String) isBuildingValid;

  ValidationRules({
    bool Function(String)? isPhoneValid,
    bool Function(String)? isSmsValid,
    bool Function(String)? isCvvValid,
    bool Function(String)? isCardNumberValid,
    bool Function(String)? isOwnerValid,
    bool Function(String)? isValidityPeriodValid,
    bool Function(String)? isNameValid,
    bool Function(String)? isCodeValid,
    bool Function(String)? isBuildCodeValid,
    bool Function(String)? isCityValid,
    bool Function(String)? isStreetValid,
    bool Function(String)? isHouseValid,
    bool Function(String)? isCorpusValid,
    bool Function(String)? isBuildingValid,
  })  : isPhoneValid = isPhoneValid ?? RightValidationRules.isPhoneValid,
        isSmsValid = isSmsValid ?? RightValidationRules.isSmsValid,
        isCvvValid = isCvvValid ?? RightValidationRules.isCvvValid,
        isCardNumberValid =
            isCardNumberValid ?? RightValidationRules.isCardNumberValid,
        isOwnerValid = isOwnerValid ?? RightValidationRules.isOwnerValid,
        isValidityPeriodValid =
            isValidityPeriodValid ?? RightValidationRules.isValidityPeriodValid,
        isNameValid = isNameValid ?? RightValidationRules.isNameValid,
        isCodeValid = isCodeValid ?? RightValidationRules.isCodeValid,
        isBuildCodeValid =
            isBuildCodeValid ?? RightValidationRules.isBuildCodeValid,
        isCityValid = isCityValid ?? RightValidationRules.isCityValid,
        isStreetValid = isStreetValid ?? RightValidationRules.isStreetValid,
        isHouseValid = isHouseValid ?? RightValidationRules.isHouseValid,
        isCorpusValid = isCorpusValid ?? RightValidationRules.isCorpusValid,
        isBuildingValid =
            isBuildingValid ?? RightValidationRules.isBuildingValid;
}

class BrokenValidationRules {
  //TODO: переделать по аналогии с номером телефона
  static const int kCvvInputLength = 4;
  static bool isCvvValid(String cvv) =>
      RegExp('^\\d{$kCvvInputLength}\$').hasMatch(cvv);
}

class RightValidationRules {
  static String phoneMask = '$phoneCode 900 000-00-00';
  static String smsCodeMask = '00000';
  static String phoneCode = '+7';
  static const int kCvvInputLength = 3;

  static bool combine(List<bool> validators) => !validators.contains(false);

  static bool isNameValid(String name) => name.isNotEmpty;

  static bool isPhoneValid(String phone) {
    if (phone.isEmpty) {
      return false;
    }
    final transformedMask = phoneMask.replaceAll(RegExp(r'\D'), '');
    final transformedPhone = phone.replaceAll(RegExp(r'\D'), '');

    return transformedPhone.length == transformedMask.length;
  }

  static bool isCodeValid(String code) => RegExp(r'[0-9]{5}').hasMatch(code);

  static bool isSmsValid(String sms) => RegExp(r'\d{4}').hasMatch(sms);

  static bool isBuildCodeValid(String code) => RegExp(r'\d+').hasMatch(code);
  static String a = '';
  static bool isCvvValid(String cvv) =>
      RegExp('^\\d{$kCvvInputLength}\$').hasMatch(cvv);

  static bool isCardNumberValid(String cardNumber) =>
      RegExp(r'^\d{16}$').hasMatch(cardNumber);

  static bool isOwnerValid(String owner) => RegExp(r'\w+').hasMatch(owner);

  static bool isValidityPeriodValid(String validityPeriod) =>
      RegExp(r'^0[1-9]\d{2}|1[0-2]\d{2}$').hasMatch(validityPeriod) &&
      DateTime.now().isBefore(validityPeriod.toCardFormattedDateTime());

  static bool isCityValid(String val) => val.isNotEmpty;
  static bool isStreetValid(String val) => val.isNotEmpty;
  static bool isHouseValid(String val) => val.isNotEmpty;
  static bool isCorpusValid(String val) => true;
  static bool isBuildingValid(String val) => true;
}
