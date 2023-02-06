package ru.yandex.metrika.lb.read.processing;

public interface LogbrokerProcessorDecoratorFactory {
    LogbrokerMessageProcessor getDecorator(LogbrokerMessageProcessor delegate);

    LogbrokerSimpleProcessor getDecorator(LogbrokerSimpleProcessor delegate);
}
