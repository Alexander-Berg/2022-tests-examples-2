package ru.yandex.metrika.lb.read.processing;

// хранит статистику использования конкретной пары WaitingLogbrokerWriter и WaitableLogbrokerProcessor
public class ProcessedMessagesStat {

    private int writtenMessagesCount;

    private int processedMessagesCount;

    private Exception exceptionHolder;

    private Object failedMessage;

    public ProcessedMessagesStat() {
        processedMessagesCount = 0;
        writtenMessagesCount = 0;
    }

    public int getWrittenMessagesCount() {
        return writtenMessagesCount;
    }

    public void setWrittenMessagesCount(int writtenMessagesCount) {
        this.writtenMessagesCount = writtenMessagesCount;
    }

    public Exception getException() {
        return exceptionHolder;
    }

    public Object getFailedMessage() {
        return failedMessage;
    }

    public void setException(Exception e, Object failedMessage) {
        this.exceptionHolder = e;
        this.failedMessage = failedMessage;
    }

    public int getProcessedMessagesCount() {
        return processedMessagesCount;
    }

    public synchronized void updateProcessedMessages(int delta) {
        processedMessagesCount += delta;

        if (processedMessagesCount >= writtenMessagesCount) {
            this.notifyAll();
        }
    }

    public void updateWrittenMessages(int delta) {
        writtenMessagesCount += delta;
    }

    public synchronized void waitProcessing() throws InterruptedException {
        while (processedMessagesCount < writtenMessagesCount) {
            this.wait();
        }
    }

    public void clear() {
        exceptionHolder = null;
        failedMessage = null;
        processedMessagesCount = 0;
        writtenMessagesCount = 0;
    }
}
