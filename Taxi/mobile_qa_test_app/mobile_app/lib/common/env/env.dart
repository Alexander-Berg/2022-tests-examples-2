enum Env {
  dev,
  prod,
}

extension EntityConverter on Env {
  T when<T>({required T prod, required T dev}) {
    switch (this) {
      case Env.prod:
        return prod;
      case Env.dev:
        return dev;
    }
  }
}
