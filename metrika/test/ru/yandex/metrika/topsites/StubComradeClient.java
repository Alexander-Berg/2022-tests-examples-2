package ru.yandex.metrika.topsites;

import java.util.Map;

import ru.yandex.qe.hitman.comrade.script.model.ComradeClient;
import ru.yandex.qe.hitman.comrade.script.model.Storage;
import ru.yandex.qe.hitman.comrade.script.model.logger.Logger;
import ru.yandex.qe.hitman.comrade.script.model.operation.Operation;

public class StubComradeClient implements ComradeClient {

    private final Logger logger = new StubLogger();
    private final Storage storage;

    public StubComradeClient(Map<String, Object> storage) {
        this.storage = new StubStorage(storage);
    }

    @Override
    public void enqueueOperation(Operation operation) {
        System.out.println("enqueue operation: " + operation);
    }

    @Override
    public Logger getLogger() {
        return logger;
    }

    @Override
    public Storage getStorage() {
        return storage;
    }
}
