package ru.yandex.metrika.task;

import com.google.common.collect.ImmutableMap;
import org.junit.Test;

import ru.yandex.bolts.collection.Cf;
import ru.yandex.bolts.collection.ListF;
import ru.yandex.commune.bazinga.impl.OnetimeJob;
import ru.yandex.commune.bazinga.scheduler.CronTaskInfo;
import ru.yandex.commune.bazinga.scheduler.OnetimeTaskInfo;
import ru.yandex.commune.bazinga.scheduler.WorkerMeta;

import static org.assertj.core.api.Assertions.assertThat;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createCronTask;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createOnetimeJob;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createOnetimeTask;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createWorker;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createWorkerWithJobs;

public class MinJobsWorkerChooserTest {

    private MinJobsWorkerChooser workerChooser = new MinJobsWorkerChooser();

    private CronTaskInfo cronTask = createCronTask("cronTask");
    private OnetimeTaskInfo onetimeTask = createOnetimeTask("onetimeTask");
    private OnetimeJob onetimeJob = createOnetimeJob();

    @Test
    public void cronTask() {
        WorkerMeta worker1WithNoJobs = createWorker("host1");
        WorkerMeta worker2WithNoJobs = createWorker("host2");

        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(cronTask, Cf.list(worker1WithNoJobs, worker2WithNoJobs));
        assertThat(chosenWorkers).containsExactly(worker1WithNoJobs, worker2WithNoJobs);
    }

    @Test
    public void onetimeTaskNoJobs() {
        WorkerMeta worker1WithNoJobs = createWorker("host1");
        WorkerMeta worker2WithNoJobs = createWorker("host2");

        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask, onetimeJob, Cf.list(worker1WithNoJobs, worker2WithNoJobs));
        assertThat(chosenWorkers).containsExactly(worker1WithNoJobs, worker2WithNoJobs);
    }

    @Test
    public void onetimeTaskNoWorkers() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask, onetimeJob, Cf.list());
        assertThat(chosenWorkers).isEmpty();
    }

    @Test
    public void oneTimeTaskOneJob() {
        WorkerMeta worker1WithOneJob = createWorkerWithJobs("host1", ImmutableMap.of("onetimeTask", 1));
        WorkerMeta worker2WithNoJobs = createWorker("host2");

        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask, onetimeJob, Cf.list(worker1WithOneJob, worker2WithNoJobs));
        assertThat(chosenWorkers).containsExactly(worker2WithNoJobs);
    }

    @Test
    public void oneTimeTaskMultipleMinJobs() {
        WorkerMeta worker1WithOneJob = createWorkerWithJobs("host1", ImmutableMap.of("onetimeTask", 1));
        WorkerMeta worker2WithTwoJobs = createWorkerWithJobs("host2", ImmutableMap.of("onetimeTask", 2));
        WorkerMeta worker3WithOneJob = createWorkerWithJobs("host3", ImmutableMap.of("onetimeTask", 1));

        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask, onetimeJob, Cf.list(worker1WithOneJob, worker2WithTwoJobs, worker3WithOneJob));
        assertThat(chosenWorkers).containsExactly(worker1WithOneJob, worker3WithOneJob);
    }
}
