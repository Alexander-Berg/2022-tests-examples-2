// TODO: перенести в общие utils
export function invariant<T>(value: T, message?: string): asserts value {
  if (!value) {
    throw new Error(message)
  }
}
