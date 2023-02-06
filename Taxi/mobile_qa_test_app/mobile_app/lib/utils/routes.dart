import 'package:flutter/material.dart';
import 'package:models/models.dart';

import '../address/ui/page.dart';
import '../app_loader/ui/page.dart';
import '../auth/ui/auth/page.dart';
import '../auth/ui/code/ui/page.dart';
import '../auth/ui/phone/ui/page.dart';
import '../auth/ui/sign_up/ui/page.dart';
import '../build/ui/page.dart';
import '../card/ui/page.dart';
import '../cart/ui/page.dart';
import '../payment/ui/page.dart';
import '../payment_result/ui/page.dart';
import '../profile/ui/page.dart';
import '../shop/ui/category/page.dart';
import '../shop/ui/main/ui/page.dart';
import '../shop/ui/product/page.dart';
import '../support/ui/answer/page.dart';
import '../support/ui/questions/page.dart';

class AppRoutes {
  static const appLoader = '/';
  static const auth = '/auth';
  static const build = '/build';
  static const signUp = '/signUp';
  static const code = '/code';
  static const phone = '/phone';
  static const supportQuestions = '/supportQuestions';
  static const supportAnswer = '/supportAnswer';
  static const shop = '/shop';
  static const card = '/card';
  static const address = '/address';
  static const product = '/product';
  static const cart = '/cart';
  static const paymentResult = '/paymentResult';
  static const payment = '/payment';
  static const profile = '/profile';
  static const category = '/category';
}

Route<dynamic>? onGenerateRoutes(RouteSettings settings) {
  final args = settings.arguments;
  final Widget page;
  switch (settings.name) {
    case AppRoutes.appLoader:
      page = const AppLoaderPage();
      break;
    case AppRoutes.build:
      page = const BuildPage();
      break;
    case AppRoutes.auth:
      page = const AuthPage();
      break;
    case AppRoutes.signUp:
      page = const SignUpPage();
      break;
    case AppRoutes.supportAnswer:
      page = const AnswerPage();
      break;
    case AppRoutes.code:
      page = const CodePage();
      break;
    case AppRoutes.phone:
      page = const PhonePage();
      break;
    case AppRoutes.supportQuestions:
      page = QuestionsPage();
      break;
    case AppRoutes.shop:
      page = const ShopMainPage();
      break;
    case AppRoutes.address:
      page = const AddressPage();
      break;
    case AppRoutes.product:
      page = args == null
          ? const ShopMainPage()
          // ignore: cast_nullable_to_non_nullable
          : ProductPage(args as Product);
      break;
    case AppRoutes.cart:
      page = const CartPage();
      break;
    case AppRoutes.category:
      page = args == null
          ? const ShopMainPage()
          : ShopCategoryPage(args as Category);
      break;
    case AppRoutes.card:
      page = const CardPage();
      break;
    case AppRoutes.paymentResult:
      page = const PaymentResultPage();
      break;
    case AppRoutes.payment:
      page = const PaymentPage();
      break;
    case AppRoutes.profile:
      page = const ProfilePage();
      break;
    default:
      page = Container();
  }

  return MaterialPageRoute<void>(
    builder: (_) => page,
  );
}
