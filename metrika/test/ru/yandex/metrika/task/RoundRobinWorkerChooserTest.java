package ru.yandex.metrika.task;

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

public class RoundRobinWorkerChooserTest {

    private RoundRobinWorkerChooser workerChooser = new RoundRobinWorkerChooser();

    private WorkerMeta worker1 = createWorker("host1");
    private WorkerMeta worker2 = createWorker("host2");

    private CronTaskInfo cronTask1 = createCronTask("cronTask1");
    private CronTaskInfo cronTask2 = createCronTask("cronTask2");

    private OnetimeTaskInfo onetimeTask1 = createOnetimeTask("onetimeTask1");
    private OnetimeTaskInfo onetimeTask2 = createOnetimeTask("onetimeTask2");

    private OnetimeJob onetimeJob = createOnetimeJob();

    @Test
    public void cronTask() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(cronTask1, Cf.list(worker1, worker2));
        assertThat(chosenWorkers).containsExactly(worker1);
    }

    @Test
    public void cronTaskNoWorkers() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(cronTask1, Cf.list());
        assertThat(chosenWorkers).isEmpty();
    }

    @Test
    public void differentCronTasks() {
        ListF<ListF<WorkerMeta>> chosenWorkersList = Cf.list(
                workerChooser.choose(cronTask1, Cf.list(worker1, worker2)),
                workerChooser.choose(cronTask2, Cf.list(worker1, worker2))
        );
        assertThat(chosenWorkersList).containsExactly(Cf.list(worker1), Cf.list(worker1));
    }

    @Test
    public void onetimeTask() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2));
        assertThat(chosenWorkers).containsExactly(worker1);
    }

    @Test
    public void onetimeTaskNoWorkers() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask1, onetimeJob, Cf.list());
        assertThat(chosenWorkers).isEmpty();
    }

    @Test
    public void differentOnetimeTasks() {
        ListF<ListF<WorkerMeta>> chosenWorkersList = Cf.list(
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2)),
                workerChooser.choose(onetimeTask2, onetimeJob, Cf.list(worker1, worker2))
        );
        assertThat(chosenWorkersList).containsExactly(Cf.list(worker1), Cf.list(worker1));
    }

    @Test
    public void second() {
        ListF<ListF<WorkerMeta>> chosenWorkersList = Cf.list(
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2)),
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2))
        );
        assertThat(chosenWorkersList).containsExactly(Cf.list(worker1), Cf.list(worker2));
    }

    @Test
    public void overflow() {
        ListF<ListF<WorkerMeta>> chosenWorkersList = Cf.list(
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2)),
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2)),
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1, worker2))
        );
        assertThat(chosenWorkersList).containsExactly(Cf.list(worker1), Cf.list(worker2), Cf.list(worker1));
    }

    @Test
    public void differentWorkers() {
        ListF<ListF<WorkerMeta>> chosenWorkersList = Cf.list(
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker1)),
                workerChooser.choose(onetimeTask1, onetimeJob, Cf.list(worker2))
        );
        assertThat(chosenWorkersList).containsExactly(Cf.list(worker1), Cf.list(worker2));
    }
}
