package ru.yandex.metrika.task;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Ignore;

import ru.yandex.bolts.collection.Cf;
import ru.yandex.commune.bazinga.impl.FullJobId;
import ru.yandex.commune.bazinga.impl.JobId;
import ru.yandex.commune.bazinga.impl.OnetimeJob;
import ru.yandex.commune.bazinga.impl.TaskId;
import ru.yandex.commune.bazinga.impl.WorkerState;
import ru.yandex.commune.bazinga.impl.worker.BazingaHostPort;
import ru.yandex.commune.bazinga.scheduler.CronTaskInfo;
import ru.yandex.commune.bazinga.scheduler.OnetimeTaskInfo;
import ru.yandex.commune.bazinga.scheduler.WorkerMeta;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@Ignore
public class WorkerChooserTestUtils {

    public static WorkerMeta createWorker(String host) {
        return createWorkerWithJobs(host, Collections.emptyMap());
    }

    public static WorkerMeta createWorkerWithJobs(String host, Map<String, Integer> jobAmounts) {
        List<FullJobId> fullJobIds = jobAmounts.entrySet().stream()
                .flatMap(entry -> {
                    TaskId taskId = new TaskId(entry.getKey());
                    return IntStream.range(0, entry.getValue())
                            .mapToObj(i -> new FullJobId(taskId, new JobId(UUID.randomUUID())));
                })
                .collect(Collectors.toList());

        WorkerState workerState = mock(WorkerState.class);
        when(workerState.getOnetimeTasks()).thenReturn(Cf.toHashSet(fullJobIds));

        WorkerMeta worker = mock(WorkerMeta.class);
        when(worker.getHostPort()).thenReturn(new BazingaHostPort(host, 42));
        when(worker.getWorkerState()).thenReturn(workerState);

        return worker;
    }

    public static CronTaskInfo createCronTask(String id) {
        CronTaskInfo cronTask = mock(CronTaskInfo.class);
        when(cronTask.getTaskId()).thenReturn(new TaskId(id));
        return cronTask;
    }

    public static OnetimeTaskInfo createOnetimeTask(String id) {
        OnetimeTaskInfo onetimeTask = mock(OnetimeTaskInfo.class);
        when(onetimeTask.getTaskId()).thenReturn(new TaskId(id));
        return onetimeTask;
    }

    public static OnetimeJob createOnetimeJob() {
        return mock(OnetimeJob.class);
    }
}
