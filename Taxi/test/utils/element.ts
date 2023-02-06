import {Nullable} from './types/utils';

interface GetTextTemplate {
    getText(): Promise<Nullable<string>>;
}

export function getText<T extends GetTextTemplate>(
    {getText}: T,
): ReturnType<GetTextTemplate['getText']> {
    return getText();
}
