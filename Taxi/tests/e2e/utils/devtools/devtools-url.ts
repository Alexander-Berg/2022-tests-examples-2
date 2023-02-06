export interface FormatDevtoolsUrlOptions {
    sessionId: string;
    selenoidHost?: string;
}

export function formatDevtoolsUrl({sessionId, selenoidHost}: FormatDevtoolsUrlOptions) {
    return `ws://${selenoidHost || '127.0.0.1:4444'}/devtools/${sessionId}/page`;
}
