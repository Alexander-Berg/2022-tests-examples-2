package ru.yandex.metrika.lb.waitable;

import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.LogbrokerRichMessage;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStat;

public class WaitableLogbrokerMessageProcessor<T> implements LogbrokerMessageProcessor<T> {

    private final ProcessedMessagesStat stat;

    private final LogbrokerMessageProcessor<T> delegate;

    public WaitableLogbrokerMessageProcessor(ProcessedMessagesStat stat, LogbrokerMessageProcessor<T> delegate) {
        this.stat = stat;
        this.delegate = delegate;
    }

    @Override
    public CompletableFuture<Void> process(long cookie, Stream<LogbrokerRichMessage<T>> richMessages) {
        var messagesList = richMessages.collect(Collectors.toList());
        int count = messagesList.size();
        try {
            delegate.process(cookie, messagesList.stream()).join();
        } catch (Exception e) {
            stat.setException(e, messagesList);
        }
        stat.updateProcessedMessages(count);
        return CompletableFuture.allOf();
    }
}
