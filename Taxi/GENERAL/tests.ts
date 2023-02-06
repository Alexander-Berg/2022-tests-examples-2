export type SelectorTestDataType<T = unknown> = {
    store: GlobalStateType;
    result: T;
};

export type ConvertersTestDataType<F extends (...args: any) => any> = {
    payload: Parameters<F>;
    result: ReturnType<F>;
    error?: string;
};
