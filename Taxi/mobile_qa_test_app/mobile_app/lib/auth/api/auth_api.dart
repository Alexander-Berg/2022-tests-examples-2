//ignore_for_file: avoid-non-null-assertion
import '../../common/api/api_client.dart';
import '../../common/api/api_paths.dart';
import '../models/auth_data.dart';
import '../models/user.dart';

class AuthApi {
  final ApiClient _client;

  AuthApi(ApiClient client) : _client = client;

  Future<User> signIn(AuthDataSignIn data) async {
    final responce = await _client.dio
        .post<Map<String, dynamic>>(ApiPaths.signIn, data: data.phone);

    return User.fromJson(responce.data!);
  }

  Future<User> signUp(AuthDataSignUp data) async {
    final responce = await _client.dio
        .post<Map<String, dynamic>>(ApiPaths.signUp, data: data.toJson());
    final registeredUser = await _client.dio
        .post<Map<String, dynamic>>(ApiPaths.signIn, data: data.toJson());
    if (registeredUser.data != null) {
      throw Exception('Пользователь уже существует');
    }

    return User.fromJson(responce.data!);
  }

  Future<User> auth(AuthData authUser) async => authUser.map(
        signIn: signIn,
        signUp: signUp,
      );

  Future<void> signOut() async {
    await _client.dio.post<Map<String, dynamic>>(ApiPaths.signOut);
  }
}
