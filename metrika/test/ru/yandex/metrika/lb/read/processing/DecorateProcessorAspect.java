package ru.yandex.metrika.lb.read.processing;


import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;

import ru.yandex.metrika.lb.read.AbstractLogbrokerConsumerConfig;
import ru.yandex.metrika.lb.serialization.BatchSerializer;
import ru.yandex.metrika.lb.serialization.Serializer;

/**
 * Аспект ловит методы класса {@link ru.yandex.metrika.lb.read.LogbrokerConsumerFactory}
 * используемые для создания консьюмера
 * и подменяет переданный в них процессор на задекорированный
 */
@Aspect
public class DecorateProcessorAspect {

    private final LogbrokerProcessorDecoratorFactory decoratorFactory;

    public DecorateProcessorAspect(LogbrokerProcessorDecoratorFactory decoratorFactory) {
        this.decoratorFactory = decoratorFactory;
    }

    @Pointcut("execution(* ru.yandex.metrika.lb.read.LogbrokerConsumerFactory.*rocessing*Consumer(..))")
    public void processingConsumer() {
    }

    @Around(value = "processingConsumer() && args(config, listenerBuilder))", argNames = "jp,config,listenerBuilder")
    public Object decorateProcessor(ProceedingJoinPoint jp, AbstractLogbrokerConsumerConfig config,
                                    ProcessingStreamListener.Builder listenerBuilder) throws Throwable {
        var processorField = listenerBuilder.getClass().getDeclaredField("messageProcessor");
        processorField.setAccessible(true);

        var processor = (LogbrokerMessageProcessor) processorField.get(listenerBuilder);

        var decorated = decoratorFactory.getDecorator(processor);
        listenerBuilder.withProcessor(decorated);
        return jp.proceed(new Object[]{config, listenerBuilder.withProcessor(decorated)});
    }

    @Around(value = "processingConsumer() && args(config, processor, serializer)", argNames = "jp,config,processor,serializer")
    public Object decorateProcessor(ProceedingJoinPoint jp, AbstractLogbrokerConsumerConfig config, LogbrokerSimpleProcessor processor, Serializer serializer) throws Throwable {
        var decorated = decoratorFactory.getDecorator(processor);
        return jp.proceed(new Object[]{config, decorated, serializer});
    }

    @Around(value = "processingConsumer() && args(config, processor, serializer)", argNames = "jp,config,processor,serializer")
    public Object decorateProcessor(ProceedingJoinPoint jp, AbstractLogbrokerConsumerConfig config, LogbrokerSimpleProcessor processor, BatchSerializer serializer) throws Throwable {
        var decorated = decoratorFactory.getDecorator(processor);
        return jp.proceed(new Object[]{config, decorated, serializer});
    }

}
