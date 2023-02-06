// eslint-disable-next-line @typescript-eslint/ban-types
declare type DeepPartial<T> = T extends object
  ? {[Key in keyof T]?: DeepPartial<T[Key]>}
  : T extends Array<infer K>
  ? // eslint-disable-next-line @typescript-eslint/no-unused-vars
    Array<DeepPartial<K>>
  : T
