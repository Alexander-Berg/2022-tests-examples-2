declare type DeepPartial<T> = T extends object
  ? {[Key in keyof T]?: DeepPartial<T[Key]>}
  : T extends Array<infer K>
  ? Array<DeepPartial<K>>
  : T
