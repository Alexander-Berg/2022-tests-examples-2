import 'package:dio/dio.dart';
import 'package:yx_network/yx_network.dart';

class ApiClient {
  late final Dio dio;
  late final bool isSetuped;

  ApiClient(Dio dio, YXNetwork config) {
    this.dio = dio..applyConfig(config);
  }
}
