package ru.yandex.metrika.lambda.steps.bazinga;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import io.qameta.allure.Allure;
import io.qameta.allure.Step;
import org.apache.commons.lang3.tuple.Pair;
import org.joda.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.bolts.collection.ListF;
import ru.yandex.bolts.collection.Option;
import ru.yandex.bolts.collection.impl.ArrayListF;
import ru.yandex.commune.bazinga.impl.FullJobId;
import ru.yandex.commune.bazinga.impl.JobId;
import ru.yandex.commune.bazinga.impl.OnetimeJob;
import ru.yandex.commune.bazinga.impl.TaskId;
import ru.yandex.commune.bazinga.impl.storage.BazingaStorage;
import ru.yandex.commune.bazinga.scheduler.ExecutionContext;
import ru.yandex.commune.bazinga.scheduler.OnetimeTask;
import ru.yandex.commune.bazinga.scheduler.TaskCategory;
import ru.yandex.metrika.bazinga.TaskScheduleParams;
import ru.yandex.metrika.bazinga.WorkerTaskManager;
import ru.yandex.metrika.lambda.steps.LogMonitor;
import ru.yandex.misc.db.q.SqlLimits;

public class WorkerTaskManagerSelfServiceImpl implements WorkerTaskManager, SelfService {

    private static final Logger log = LoggerFactory.getLogger(WorkerTaskManagerSelfServiceImpl.class);

    private Map<FullJobId, Pair<OnetimeTask, TaskScheduleParams>> tasks = new ConcurrentHashMap<>();

    @Autowired
    private BazingaStorage bazingaStorage;

    @Override
    public FullJobId schedule(OnetimeTask task, TaskScheduleParams scheduleParams) {
        FullJobId id = new FullJobId(task.id(), new JobId(new Instant(tasks.size() + 1), Option.empty()));
        tasks.put(id, Pair.of(task.makeCopy(), scheduleParams));
        log.info("==> Schedule one time task: {}", id.toString());
        return id;
    }

    @Override
    public FullJobId schedule(OnetimeTask task) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, Instant date) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, TaskCategory category, Instant date) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, TaskCategory category, Instant date, int priority) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, TaskCategory category, Instant date, int priority, boolean forceRandomInId) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, TaskCategory category, Instant date, int priority, boolean forceRandomInId, Option<String> group) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public FullJobId schedule(OnetimeTask task, TaskCategory category, Instant date, int priority, boolean forceRandomInId, Option<String> group, JobId jobId) {
        throw new RuntimeException("Not implemented");
    }

    @Override
    public Option<OnetimeJob> getOnetimeJob(FullJobId id) {
        return Option.empty();
    }

    @Override
    public boolean isJobActive(OnetimeTask task) {
        return false;
    }

    @Override
    public ListF<? extends OnetimeTask> getActiveTasks(ListF<? extends OnetimeTask> tasks) {
        return new ArrayListF<>();
    }

    @Override
    public ListF<OnetimeJob> getActiveJobs(TaskId taskId, SqlLimits limits) {
        return new ArrayListF<>();
    }

    @Override
    public ListF<OnetimeJob> getFailedJobs(TaskId taskId, SqlLimits limits) {
        return new ArrayListF<>();
    }

    @Override
    public ListF<OnetimeJob> getJobsByGroup(String group, SqlLimits limits) {
        return new ArrayListF<>();
    }

    @Override
    public void executeScheduledTasks() {
        log.info("====> Start execute scheduled tasks. {} total tasks", tasks.size());

        executeScheduledTasksOnce();

        log.info("====> Finish execute scheduled tasks");
    }

    @Step
    private void executeScheduledTasksOnce() {
        for (Map.Entry<FullJobId, Pair<OnetimeTask, TaskScheduleParams>> entry : tasks.entrySet()) {
            FullJobId fullJobId = entry.getKey();
            try {
                log.info("==> Execute one time task {}", fullJobId.toString());
                Allure.step(entry.getKey().toString(), () -> {
                    try(LogMonitor logMonitor = new LogMonitor("Консольный лог")) {
                        OnetimeTask task = entry.getValue().getLeft();
                        Object taskParameters = entry.getValue().getRight().getTaskParameters();
                        task.setParameters(taskParameters);
                        task.execute(new ExecutionContext(bazingaStorage, true, fullJobId, Option.empty()));
                    }
                });
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
            finally {
                log.info("==> Finish Execute one time task {}", fullJobId.toString());
            }
        }

        tasks.clear();
    }

}
