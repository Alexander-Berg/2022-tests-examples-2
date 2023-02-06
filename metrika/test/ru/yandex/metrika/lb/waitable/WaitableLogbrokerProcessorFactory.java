package ru.yandex.metrika.lb.waitable;

import ru.yandex.metrika.lb.read.processing.LogbrokerMessageProcessor;
import ru.yandex.metrika.lb.read.processing.LogbrokerProcessorDecoratorFactory;
import ru.yandex.metrika.lb.read.processing.LogbrokerSimpleProcessor;
import ru.yandex.metrika.lb.read.processing.ProcessedMessagesStatRegistrator;

public class WaitableLogbrokerProcessorFactory implements LogbrokerProcessorDecoratorFactory {

    private final ProcessedMessagesStatRegistrator processorsStatRegistrator;

    public WaitableLogbrokerProcessorFactory(ProcessedMessagesStatRegistrator processorsStatRegistrator) {
        this.processorsStatRegistrator = processorsStatRegistrator;
    }


    @Override
    public LogbrokerMessageProcessor getDecorator(LogbrokerMessageProcessor delegate) {
        return new WaitableLogbrokerMessageProcessor(processorsStatRegistrator.getStatForProcessor(delegate), delegate);
    }

    @Override
    public LogbrokerSimpleProcessor getDecorator(LogbrokerSimpleProcessor delegate) {
        return new WaitableLogbrokerSimpleProcessor(processorsStatRegistrator.getStatForProcessor(delegate), delegate);
    }
}
