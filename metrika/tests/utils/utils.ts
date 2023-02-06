type Options<C> = C extends (options: infer O) => any ? O : never;

export { Options };
