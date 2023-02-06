export type Nullable<T = unknown> = T | null;
export type Undefinable<T = unknown> = T | undefined;
export type Empty<T = unknown> = Nullable<T> | Undefinable<T>;
