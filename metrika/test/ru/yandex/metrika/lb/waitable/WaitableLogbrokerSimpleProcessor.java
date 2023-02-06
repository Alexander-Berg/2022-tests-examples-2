package ru.yandex.metrika.lb.waitable;

import java.util.List;
import java.util.concurrent.CompletableFuture;

import ru.yandex.metrika.lb.read.processing.LogbrokerSimpleProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStat;

public class WaitableLogbrokerSimpleProcessor<T> implements LogbrokerSimpleProcessor<T> {

    private final ProcessedMessagesStat stat;

    private final LogbrokerSimpleProcessor<T> delegate;

    public WaitableLogbrokerSimpleProcessor(ProcessedMessagesStat stat, LogbrokerSimpleProcessor<T> delegate) {
        this.stat = stat;
        this.delegate = delegate;
    }


    @Override
    public CompletableFuture<Void> process(List<T> messages) {
        int count = messages.size();
        try {
            delegate.process(messages).join();
        } catch (Exception e) {
            stat.setException(e, messages);
        }
        stat.updateProcessedMessages(count);
        return CompletableFuture.allOf();
    }

}
