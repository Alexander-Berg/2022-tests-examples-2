package ru.yandex.metrika.lb.read.processing;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ProcessedMessagesStatRegistrator {
    private final Map<LogbrokerMessageProcessor, ProcessedMessagesStat> stats;

    public ProcessedMessagesStatRegistrator(List<LogbrokerMessageProcessor> processors) {
        stats = new ConcurrentHashMap<>();
        processors.forEach(this::registerProcessor);
    }

    public void registerProcessor(LogbrokerMessageProcessor processor) {
        stats.put(processor, new ProcessedMessagesStat());
    }

    public ProcessedMessagesStat getStatForProcessor(LogbrokerMessageProcessor processor) {
        if (!stats.containsKey(processor)) {
            throw new IllegalArgumentException("Processor wasn't registered yet");
        }
        return stats.get(processor);
    }
}
