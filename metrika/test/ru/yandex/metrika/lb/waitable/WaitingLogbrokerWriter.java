package ru.yandex.metrika.lb.waitable;

import java.util.List;
import java.util.concurrent.CompletableFuture;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStat;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.write.LogbrokerWriter;

// Класс для тестов. Пишет переданные ему данные в топик и умеет ждать, пока их обработают
public class WaitingLogbrokerWriter<T> implements LogbrokerWriter<T> {

    private static final Logger log = LoggerFactory.getLogger(WaitingLogbrokerWriter.class);

    private final LogbrokerWriter<T> delegateDownstream;
    private final ProcessedMessagesStat processedMessagesStat;

    // выбрасывать ли ошибку, если при обработке записанного произошла ошибка
    private final boolean failOnException;

    public WaitingLogbrokerWriter(LogbrokerWriter<T> delegateDownstream, LogbrokerMessageProcessor<T> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        this.delegateDownstream = delegateDownstream;
        this.processedMessagesStat = processedMessagesStatRegistrator.getStatForProcessor(processor);
        failOnException = true;
    }

    public WaitingLogbrokerWriter(LogbrokerWriter<T> delegateDownstream, ProcessedMessagesStat processedMessagesStat, boolean failOnException) {
        this.delegateDownstream = delegateDownstream;
        this.processedMessagesStat = processedMessagesStat;
        this.failOnException = failOnException;
    }

    @Override
    public CompletableFuture<Void> writeBatchAsync(List<T> list) {
        delegateDownstream.writeBatchAsync(list).join();
        processedMessagesStat.updateWrittenMessages(list.size());

        return CompletableFuture.allOf();
    }

    @Override
    public void close() {
        delegateDownstream.close();
    }

    public void waitProcessing() throws InterruptedException {
        processedMessagesStat.waitProcessing();

        if (processedMessagesStat.getException() != null) {
            if (failOnException) {
                throw new RuntimeException("Fail to process message: " + processedMessagesStat.getFailedMessage(), processedMessagesStat.getException());
            } else {
                log.error("Exception occurred while processing message: {}", processedMessagesStat.getFailedMessage(), processedMessagesStat.getException());
            }
        }
    }

    public void clear() {
        processedMessagesStat.clear();
    }
}
