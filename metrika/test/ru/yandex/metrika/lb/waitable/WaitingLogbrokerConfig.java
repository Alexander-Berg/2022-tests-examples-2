package ru.yandex.metrika.lb.waitable;

import java.util.List;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

import ru.yandex.metrika.lb.read.processing.DecorateProcessorAspect;
import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.LogbrokerProcessorDecoratorFactory;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;

@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class WaitingLogbrokerConfig {

    @Bean
    public ProcessedMessagesStatRegistrator processedMessagesStatRegistrator(List<LogbrokerMessageProcessor> processors) {
        return new ProcessedMessagesStatRegistrator(processors);
    }

    @Bean
    public DecorateProcessorAspect decorateProcessorAspect(LogbrokerProcessorDecoratorFactory decoratorFactory) {
        return new DecorateProcessorAspect(decoratorFactory);
    }

    @Bean
    public LogbrokerProcessorDecoratorFactory waitableLogbrokerProcessorDecoratorFactory(ProcessedMessagesStatRegistrator processedMessagesStatRegistrator) {
        return new WaitableLogbrokerProcessorFactory(processedMessagesStatRegistrator);
    }
}
