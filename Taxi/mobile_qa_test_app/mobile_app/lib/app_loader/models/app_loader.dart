abstract class AppLoader {}

class AppLoaderInProgress extends AppLoader {}

class AppLoaderCompleted extends AppLoader {}

class AppLoaderFailured extends AppLoader {
  final String message;

  AppLoaderFailured(this.message);
}
