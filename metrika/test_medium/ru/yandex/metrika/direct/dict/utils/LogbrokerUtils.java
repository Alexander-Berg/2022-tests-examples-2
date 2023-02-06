package ru.yandex.metrika.direct.dict.utils;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicLong;

import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProvider;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doAnswer;

public abstract class LogbrokerUtils {
    public static CountDownLatch allMessagesIsProcessed(
            LogbrokerMessageProcessor<?> spyingProcessor, long expectedNumberOfMessages
    ) {
        var latch = new CountDownLatch(1);
        var processedMessagesCounter = new AtomicLong(0);
        var resultCallback = new ResultWithCallback<CompletableFuture<Void>>((future, args) -> future.thenRun(() -> {
            long numberOfProcessedMessages = processedMessagesCounter.addAndGet(
                    args.getArgument(1, LogbrokerMessageProvider.class).getMessagesStream().count()
            );
            if (numberOfProcessedMessages == expectedNumberOfMessages) {
                latch.countDown();
            }
        }));
        doAnswer(resultCallback)
                .when(spyingProcessor)
                .process(anyLong(), any(LogbrokerMessageProvider.class));
        return latch;
    }
}
