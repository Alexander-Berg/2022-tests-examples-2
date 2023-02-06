
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ru.dart';

/// Callers can lookup localized strings with an instance of AppLocalizations returned
/// by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// localizationDelegates list, and the locales they support in the app's
/// supportedLocales list. For example:
///
/// ```
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ru')
  ];

  /// No description provided for @app_name.
  ///
  /// In ru, this message translates to:
  /// **'Магазин'**
  String get app_name;

  /// No description provided for @sign_in.
  ///
  /// In ru, this message translates to:
  /// **'Вход'**
  String get sign_in;

  /// No description provided for @sign_up.
  ///
  /// In ru, this message translates to:
  /// **'Регистрация'**
  String get sign_up;

  /// No description provided for @enter_agreement.
  ///
  /// In ru, this message translates to:
  /// **'Нажимая «Вход или регистрация», вы принимаете [соглашение](_).'**
  String get enter_agreement;

  /// No description provided for @buildTitle.
  ///
  /// In ru, this message translates to:
  /// **'Вход'**
  String get buildTitle;

  /// No description provided for @signUpTitle.
  ///
  /// In ru, this message translates to:
  /// **'Регистрация'**
  String get signUpTitle;

  /// No description provided for @signUpBody.
  ///
  /// In ru, this message translates to:
  /// **'Вы принимаете соглашение, нажимая кнопку «Далее»'**
  String get signUpBody;

  /// No description provided for @next.
  ///
  /// In ru, this message translates to:
  /// **'Далее'**
  String get next;

  /// No description provided for @surnameInputHint.
  ///
  /// In ru, this message translates to:
  /// **'Фамилия'**
  String get surnameInputHint;

  /// No description provided for @nameInputHint.
  ///
  /// In ru, this message translates to:
  /// **'Имя'**
  String get nameInputHint;

  /// No description provided for @patronymicInputHint.
  ///
  /// In ru, this message translates to:
  /// **'Отчество'**
  String get patronymicInputHint;

  /// No description provided for @supportPageTitle.
  ///
  /// In ru, this message translates to:
  /// **'Поддержка'**
  String get supportPageTitle;

  /// No description provided for @supportPageBody.
  ///
  /// In ru, this message translates to:
  /// **'Какой у вас вопрос?'**
  String get supportPageBody;

  /// No description provided for @buildBody.
  ///
  /// In ru, this message translates to:
  /// **'Для начала теста введите код сборки'**
  String get buildBody;

  /// No description provided for @buildInputHint.
  ///
  /// In ru, this message translates to:
  /// **'Код'**
  String get buildInputHint;

  /// No description provided for @start.
  ///
  /// In ru, this message translates to:
  /// **'Начать'**
  String get start;

  /// No description provided for @loading.
  ///
  /// In ru, this message translates to:
  /// **'Загрузка'**
  String get loading;

  /// No description provided for @retry_text.
  ///
  /// In ru, this message translates to:
  /// **'Попробовать снова'**
  String get retry_text;

  /// No description provided for @codeTitle.
  ///
  /// In ru, this message translates to:
  /// **'Код в сообщении'**
  String get codeTitle;

  /// No description provided for @codeBody.
  ///
  /// In ru, this message translates to:
  /// **'Мы отправили проверочный код на номер'**
  String get codeBody;

  /// No description provided for @codeInputHint.
  ///
  /// In ru, this message translates to:
  /// **'00000'**
  String get codeInputHint;

  /// No description provided for @askSupport.
  ///
  /// In ru, this message translates to:
  /// **'Обратиться в поддержку'**
  String get askSupport;

  /// No description provided for @submit.
  ///
  /// In ru, this message translates to:
  /// **'Готово'**
  String get submit;

  /// No description provided for @phoneInputHint.
  ///
  /// In ru, this message translates to:
  /// **'+7 (900) 000-00-00'**
  String get phoneInputHint;

  /// No description provided for @phoneInputPlacaholder.
  ///
  /// In ru, this message translates to:
  /// **'Телефон'**
  String get phoneInputPlacaholder;

  /// No description provided for @phoneBody.
  ///
  /// In ru, this message translates to:
  /// **'Введите номер, мы отправим вам код для входа'**
  String get phoneBody;

  /// No description provided for @phoneTitle.
  ///
  /// In ru, this message translates to:
  /// **'Ваш телефон'**
  String get phoneTitle;

  /// No description provided for @sendCode.
  ///
  /// In ru, this message translates to:
  /// **'Отправить код'**
  String get sendCode;

  /// No description provided for @cardTitle.
  ///
  /// In ru, this message translates to:
  /// **'Привязать карту'**
  String get cardTitle;

  /// No description provided for @cardBody.
  ///
  /// In ru, this message translates to:
  /// **'Вписывайте данные в точности, как указаны на вашей карте'**
  String get cardBody;

  /// No description provided for @cardInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Карта'**
  String get cardInputPlaceholder;

  /// No description provided for @cvvInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Код'**
  String get cvvInputPlaceholder;

  /// No description provided for @validityPeriodInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Срок'**
  String get validityPeriodInputPlaceholder;

  /// No description provided for @ownerInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Владелец'**
  String get ownerInputPlaceholder;

  /// No description provided for @cardButtonTitle.
  ///
  /// In ru, this message translates to:
  /// **'Привязать'**
  String get cardButtonTitle;

  /// No description provided for @addressTitle.
  ///
  /// In ru, this message translates to:
  /// **'Адрес'**
  String get addressTitle;

  /// No description provided for @cityInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Город'**
  String get cityInputPlaceholder;

  /// No description provided for @streetInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Улица'**
  String get streetInputPlaceholder;

  /// No description provided for @houseInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Дом'**
  String get houseInputPlaceholder;

  /// No description provided for @corpusInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Корпус'**
  String get corpusInputPlaceholder;

  /// No description provided for @buildingInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Cтроение'**
  String get buildingInputPlaceholder;

  /// No description provided for @addressButtonTitle.
  ///
  /// In ru, this message translates to:
  /// **'К оплате'**
  String get addressButtonTitle;

  /// No description provided for @commentInputPlaceholder.
  ///
  /// In ru, this message translates to:
  /// **'Комментарий'**
  String get commentInputPlaceholder;

  /// No description provided for @rubleSign.
  ///
  /// In ru, this message translates to:
  /// **'₽'**
  String get rubleSign;

  /// No description provided for @shop.
  ///
  /// In ru, this message translates to:
  /// **'Магазин'**
  String get shop;

  /// No description provided for @addToCard.
  ///
  /// In ru, this message translates to:
  /// **'В корзину'**
  String get addToCard;

  /// No description provided for @categories.
  ///
  /// In ru, this message translates to:
  /// **'Категории'**
  String get categories;

  /// No description provided for @findInShop.
  ///
  /// In ru, this message translates to:
  /// **'Найти в Магазине'**
  String get findInShop;

  /// No description provided for @youWillLikeIt.
  ///
  /// In ru, this message translates to:
  /// **'Вам понравится'**
  String get youWillLikeIt;

  /// No description provided for @paymentResultTitle.
  ///
  /// In ru, this message translates to:
  /// **'Ваш заказ успешно создан!'**
  String get paymentResultTitle;

  /// No description provided for @paymentResultButtonTitle.
  ///
  /// In ru, this message translates to:
  /// **'Создать еще заказ'**
  String get paymentResultButtonTitle;

  /// No description provided for @paymentTitle.
  ///
  /// In ru, this message translates to:
  /// **'Оплата'**
  String get paymentTitle;

  /// No description provided for @paymentButtonTitle.
  ///
  /// In ru, this message translates to:
  /// **'Завершить заказ'**
  String get paymentButtonTitle;

  /// No description provided for @paymentCardOption.
  ///
  /// In ru, this message translates to:
  /// **'Картой'**
  String get paymentCardOption;

  /// No description provided for @paymentCashOption.
  ///
  /// In ru, this message translates to:
  /// **'Наличными'**
  String get paymentCashOption;

  /// No description provided for @shortDescription.
  ///
  /// In ru, this message translates to:
  /// **'Краткие характеристики'**
  String get shortDescription;

  /// No description provided for @fullname.
  ///
  /// In ru, this message translates to:
  /// **'Полное название'**
  String get fullname;

  /// No description provided for @aboutProduct.
  ///
  /// In ru, this message translates to:
  /// **'О товаре'**
  String get aboutProduct;

  /// No description provided for @profile.
  ///
  /// In ru, this message translates to:
  /// **'Профиль'**
  String get profile;

  /// No description provided for @linkCard.
  ///
  /// In ru, this message translates to:
  /// **'Привязать карту'**
  String get linkCard;

  /// No description provided for @saveChanges.
  ///
  /// In ru, this message translates to:
  /// **'Сохранить изменения'**
  String get saveChanges;

  /// No description provided for @exit.
  ///
  /// In ru, this message translates to:
  /// **'Выйти'**
  String get exit;

  /// No description provided for @cart.
  ///
  /// In ru, this message translates to:
  /// **'Корзина'**
  String get cart;

  /// No description provided for @maybeSomethingElse.
  ///
  /// In ru, this message translates to:
  /// **'Может, что-то ещё?'**
  String get maybeSomethingElse;

  /// No description provided for @selectDeliveryAddress.
  ///
  /// In ru, this message translates to:
  /// **'Выберите адрес доставки'**
  String get selectDeliveryAddress;

  /// No description provided for @afterYouCanPayment.
  ///
  /// In ru, this message translates to:
  /// **'После вы сможете перейти к оплате'**
  String get afterYouCanPayment;

  /// No description provided for @toBePaid.
  ///
  /// In ru, this message translates to:
  /// **'К оплате'**
  String get toBePaid;

  /// No description provided for @wrongFormat.
  ///
  /// In ru, this message translates to:
  /// **'Неверный формат'**
  String get wrongFormat;

  /// No description provided for @fillFields.
  ///
  /// In ru, this message translates to:
  /// **'Заполните все поля'**
  String get fillFields;

  /// No description provided for @userNotFound.
  ///
  /// In ru, this message translates to:
  /// **'Пользователь не найден'**
  String get userNotFound;

  /// No description provided for @saved.
  ///
  /// In ru, this message translates to:
  /// **'Сохранено'**
  String get saved;

  /// No description provided for @unknowedError.
  ///
  /// In ru, this message translates to:
  /// **'Неизвестная ошибка'**
  String get unknowedError;

  /// No description provided for @killograms.
  ///
  /// In ru, this message translates to:
  /// **'кг'**
  String get killograms;

  /// No description provided for @nightMode.
  ///
  /// In ru, this message translates to:
  /// **'Ночной режим'**
  String get nightMode;

  /// No description provided for @deleteProfile.
  ///
  /// In ru, this message translates to:
  /// **'Удалить профиль'**
  String get deleteProfile;

  /// No description provided for @profileDeleted.
  ///
  /// In ru, this message translates to:
  /// **'Профиль удалён 😔'**
  String get profileDeleted;

  /// No description provided for @yes.
  ///
  /// In ru, this message translates to:
  /// **'Да'**
  String get yes;

  /// No description provided for @no.
  ///
  /// In ru, this message translates to:
  /// **'Нет'**
  String get no;

  /// No description provided for @areYouSureYouWantDeleteAccount.
  ///
  /// In ru, this message translates to:
  /// **'Вы уверены, что хотите удалить аккаунт?'**
  String get areYouSureYouWantDeleteAccount;

  /// No description provided for @deleteAccountAttention.
  ///
  /// In ru, this message translates to:
  /// **'После удаления нельзя будет войти в аккаунт'**
  String get deleteAccountAttention;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {


  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ru': return AppLocalizationsRu();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.'
  );
}
