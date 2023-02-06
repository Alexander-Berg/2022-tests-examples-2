package ru.yandex.autotests.morda.rules.errorcollector;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/04/15
 */
public class HierarchicalErrorCollectorStage implements Runnable {
    private static final long DEFAULT_TIMEOUT = 30;
    private HierarchicalErrorCollectorChecks checks;
    private final List<HierarchicalErrorCollectorStage> stages;
    private final List<Throwable> errors;

    public HierarchicalErrorCollectorStage() {
        checks = new HierarchicalErrorCollectorChecks();
        stages = new ArrayList<>();
        errors = new ArrayList<>();
    }

    public static HierarchicalErrorCollectorStage stage() {
        return new HierarchicalErrorCollectorStage();
    }

    @Override
    public void run() {
        ExecutorService executorService = Executors.newCachedThreadPool();

        errors.addAll(checks.run().getErrors());

        if (errors.size() > 0) {
            return;
        }

        stages.stream().forEach((stage) -> executorService.execute(stage::run));

        try {
            executorService.shutdown();
            executorService.awaitTermination(DEFAULT_TIMEOUT, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            stages.stream().forEachOrdered((stage) -> errors.addAll(stage.getErrors()));
        }
    }

    public List<Throwable> getErrors() {
        return errors;
    }

    public HierarchicalErrorCollectorStage withChecks(HierarchicalErrorCollectorChecks checks) {
        this.checks = checks;
        return this;
    }
}
