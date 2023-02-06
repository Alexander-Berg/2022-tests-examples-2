type Copy<T> = {
  [Key in keyof T]: T[Key]
}

declare type RequiredByKeys<T, K = keyof T> = Copy<
  Omit<T, K extends keyof T ? K : never> &
    {
      [Key in keyof T as K extends Key ? Key : never]-?: T[Key]
    }
>
