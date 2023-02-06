import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import 'package:unpub/src/auth/other_roles_auth_validator.dart';
import 'package:unpub/src/auth/pub_auth_validator.dart';
import 'package:unpub/src/packages/update/package_downloader.dart';
import 'package:unpub/src/packages/update/update_package_repository.dart';
import 'package:unpub/src/permission/package_permission_repository.dart';
import 'package:unpub/src/server_config.dart';
import 'package:unpub/src/system/check_user_repository.dart';
import 'package:unpub/src/system/system_auth_validator.dart';
import 'package:unpub/src/migrations/mongo/utils.dart';
import 'package:unpub/src/packages/mirror/mirror_legacy_forks_resolver.dart';
import 'package:unpub/src/packages/mirror/mirror_package_resolver.dart';
import 'package:unpub/src/packages/mongo_package_versions_store.dart';
import 'package:unpub/src/packages/update/package_uploader.dart';
import 'package:unpub/src/settings/settings_repository.dart';
import 'package:unpub/src/settings/settings_store.dart';
import 'package:unpub/src/system/system_controller.dart';
import 'package:unpub/src/ui/static_web_provider.dart';
import 'package:unpub/src/yandex/idm/idm_controller.dart';
import 'package:unpub/src/yandex/idm/idm_network_client.dart';
import 'package:unpub/src/yandex/idm/model/idm_response_factory.dart';
import 'package:unpub/src/yandex/idm/idm_packages_repository.dart';
import 'package:unpub/src/yandex/tvm/tvm_repository.dart';
import 'package:unpub/src/yandex/ya_auth_repository.dart';
import 'package:unpub/src/data/ttl_storage.dart';
import 'package:unpub/src/mongo_db_provider.dart';
import 'package:unpub/src/role/data/user_repository.dart';
import 'package:unpub/src/role/data/user_store.dart';
import 'package:unpub/src/role/user_role_mapper.dart';
import 'package:unpub/unpub.dart' as unpub;

final notExistingPacakge = 'not_existing_package';
final pubHostedUrl = 'http://0.0.0.0:4000';
final baseUri = Uri.parse(pubHostedUrl);

final package0 = 'package_0';
final package1 = 'package_1';
final email0 = 'email0@example.com';
final email1 = 'email1@example.com';
final email2 = 'email2@example.com';
final email3 = 'email3@example.com';

createServer(String opEmail) async {
  return await startServer('0.0.0.0', 4000, 1, () => _createApp(opEmail));
}

Future<http.Response> getVersions(String package) {
  package = Uri.encodeComponent(package);
  return http.get(baseUri.resolve('/api/packages/$package'));
}

Future<http.Response> getSpecificVersion(String package, String version) {
  package = Uri.encodeComponent(package);
  version = Uri.encodeComponent(version);
  return http.get(baseUri.resolve('/api/packages/$package/versions/$version'));
}

var pubCommand = Platform.isWindows ? 'pub.bat' : 'pub';

Future<ProcessResult> pubPublish(String name, String version) {
  return Process.run(pubCommand, ['publish', '--force'],
      workingDirectory: path.absolute('test/fixtures', name, version),
      environment: {'PUB_HOSTED_URL': pubHostedUrl});
}

Future<ProcessResult> pubUploader(String name, String operation, String email) {
  assert(['add', 'remove'].contains(operation), 'operation error');

  return Process.run(pubCommand, ['uploader', operation, email],
      workingDirectory: path.absolute('test/fixtures', name, '0.0.1'),
      environment: {'PUB_HOSTED_URL': pubHostedUrl});
}

unpub.App _createApp(String opEmail) {
  final dbProvider = MongoDbProvider('mongodb://localhost:27017/dart_pub_test');
  final mongoStore = unpub.InternalMetaStore(dbProvider);
  final versionsStore = MongoPackageVersionsStore(dbProvider, TTLStorage(Duration(hours: 1)));

  final packageStore = unpub.FileStore.withCredentials('s3.mdst.yandex.net', 'main', '<stub keyId>', '<stub secret key>');

  final packagesRepository = IdmPackagesRepository(mongoStore);
  final tvmRepository = TvmRepository(
      TTLStorage(Duration(minutes: 10)),
      TTLStorage(Duration(hours: 12))
  );
  final userRepository = UserRepository(UserStore(dbProvider), UserRoleMapper());
  final yaAuhRepository = YaAuthRepository(tvmRepository);
  final checkUserRepository = CheckUserRepository(yaAuhRepository, userRepository);
  final pubAuthValidator = PubAuthValidator(checkUserRepository, PackagePermissionRepository());
  final upstreamUrl = 'https://pub.dev';
  final settingsRepository = SettingsRepository(SettingsStore(dbProvider));
  final packageDownloader = PackageDownloader(versionsStore, upstreamUrl);
  final packageUploader = PackageUploader(
      mongoStore,
      pubAuthValidator,
      versionsStore,
      packageStore,
      IdmNetworkClient(tvmRepository, 'unpub-test'),
      opEmail,
      upstreamUrl
  );
  return unpub.App(
      metaStore: mongoStore,
      versionsStore: versionsStore,
      packageStore: packageStore,
      overrideUploaderEmail: opEmail,
      idmController: IdmController(userRepository, packagesRepository, IdmNodeFactory(), tvmRepository),
      pubAuthValidator: pubAuthValidator,
      mirrorPackageResolver: MirrorPackageResolver(upstreamUrl, MirrorLegacyForksResolver(versionsStore), settingsRepository, packageDownloader),
      packageUploader: packageUploader,
      systemController: SystemController(
          SystemAuthValidator(checkUserRepository),
          OtherRolesAuthValidator(checkUserRepository),
          createMongoMigrationRepository(dbProvider, 'http://0.0.0.0:4000'),
          checkUserRepository,
          mongoStore,
          versionsStore,
          packageStore,
          userRepository,
          settingsRepository,
          UpdatePackageRepository(packageDownloader, packageUploader)
      ),
      webProvider: StaticWebProvider()
  );
}
