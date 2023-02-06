package ru.yandex.metrika.lb.waitable;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

import org.awaitility.core.ConditionTimeoutException;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import ru.yandex.metrika.lb.read.processing.LogbrokerProcessorDecoratorFactory;
import ru.yandex.metrika.lb.read.processing.LogbrokerSimpleProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterStub;

import static java.util.concurrent.CompletableFuture.allOf;
import static org.awaitility.Awaitility.await;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

@RunWith(SpringJUnit4ClassRunner.class)
public class WaitingLogbrokerWriterTest {

    @Autowired
    private WaitingLogbrokerWriter<String> waitingLogbrokerWriter;

    @Autowired
    private LogbrokerWriterStub<String> writerStub;

    @Autowired
    private DummyProcessor dummyProcessor;

    @Autowired
    private LogbrokerProcessorDecoratorFactory decoratorFactory;

    private static final List<String> processedMessages = new ArrayList<>();

    private static final List<String> messages = List.of("ipa", "stout", "porter");

    @Before
    public void setup() {
        waitingLogbrokerWriter.clear();
        processedMessages.clear();
    }

    @Test
    public void correctlyWritesMessages() {
        waitingLogbrokerWriter.writeBatchAsync(messages).join();

        writerStub.assertHaveOnlyMessagesInOrder(messages);
    }

    @Test
    public void correctlyWaitsIfNoMessagesWritten() {
        try {
            await().atMost(1000, TimeUnit.MILLISECONDS).until(() -> {
                waitingLogbrokerWriter.waitProcessing();
                return true;
            });
        } catch (ConditionTimeoutException e) {
            fail();
        }
    }

    @Test
    public void correctlyWaitsMessagesProcessing() {
        waitingLogbrokerWriter.writeBatchAsync(messages).join();

        CompletableFuture<Void> waitProcessing = CompletableFuture.runAsync(() -> {
            try {
                waitingLogbrokerWriter.waitProcessing();
            } catch (InterruptedException ignored) {
            }
            assertEquals(processedMessages, messages);
        });


        CompletableFuture<Void> processing = CompletableFuture.runAsync(() -> {
            var processor = decoratorFactory.getDecorator(dummyProcessor);
            processor.process(messages).join();
        });

        allOf(waitProcessing, processing).join();
    }


    private static class DummyProcessor implements LogbrokerSimpleProcessor<String> {
        @Override
        public CompletableFuture<Void> process(List<String> messages) {
            processedMessages.addAll(messages);
            return allOf();
        }
    }

    @Configuration
    @Import(WaitingLogbrokerConfig.class)
    public static class Config {

        @Bean
        public WaitingLogbrokerWriter<String> waitingLogbrokerWriter(LogbrokerWriter<String> delegate, LogbrokerSimpleProcessor<String> processor, ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
            return new WaitingLogbrokerWriter<>(delegate, processor, processedMessagesStatRegistrator);

        }

        @Bean
        public DummyProcessor processor() {
            return new DummyProcessor();
        }

        @Bean
        public LogbrokerWriterStub<String> logbrokerWriterStub() {
            return new LogbrokerWriterStub<>();
        }
    }

}
