import format from 'date-fns/format';

function formatTimestamp() {
    return format(new Date(), 'HH:mm:ss');
}

interface LogMessageParams {
    type?: string;
    requestId: string;
    title: string;
    message: string;
    meta?: Record<string, unknown>;
}

function formatLogMessage({requestId, type, title, message, meta}: LogMessageParams) {
    return `NETWORK ${formatTimestamp()} [${requestId}] ${type} <${title}> ${message} -- ${JSON.stringify(meta || {})}`;
}

export function logMessage(params: LogMessageParams) {
    console.log(formatLogMessage(params));
}
