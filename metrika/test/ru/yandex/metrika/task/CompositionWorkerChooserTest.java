package ru.yandex.metrika.task;

import java.util.Arrays;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.bolts.collection.Cf;
import ru.yandex.bolts.collection.ListF;
import ru.yandex.commune.bazinga.impl.OnetimeJob;
import ru.yandex.commune.bazinga.scheduler.CronTaskInfo;
import ru.yandex.commune.bazinga.scheduler.OnetimeTaskInfo;
import ru.yandex.commune.bazinga.scheduler.WorkerChooser;
import ru.yandex.commune.bazinga.scheduler.WorkerMeta;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createCronTask;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createOnetimeJob;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createOnetimeTask;
import static ru.yandex.metrika.task.WorkerChooserTestUtils.createWorker;

public class CompositionWorkerChooserTest {

    private WorkerChooser workerChooser1;
    private WorkerChooser workerChooser2;
    private CompositionWorkerChooser workerChooser;

    private WorkerMeta worker1 = createWorker("host1");
    private WorkerMeta worker2 = createWorker("host2");
    private WorkerMeta worker3 = createWorker("host3");

    private CronTaskInfo cronTask = createCronTask("cronTask");
    private OnetimeTaskInfo onetimeTask = createOnetimeTask("onetimeTask");
    private OnetimeJob onetimeJob = createOnetimeJob();

    @Before
    public void init() {
        workerChooser1 = mock(WorkerChooser.class);
        when(workerChooser1.choose(any(), any())).thenReturn(Cf.list(worker2, worker3));
        when(workerChooser1.choose(any(), any(), any())).thenReturn(Cf.list(worker2, worker3));

        workerChooser2 = mock(WorkerChooser.class);
        when(workerChooser2.choose(any(), any())).thenReturn(Cf.list(worker3));
        when(workerChooser2.choose(any(), any(), any())).thenReturn(Cf.list(worker3));

        workerChooser = new CompositionWorkerChooser(Arrays.asList(workerChooser1, workerChooser2));
    }

    @Test
    public void cronTask() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(cronTask, Cf.list(worker1, worker2, worker3));

        verify(workerChooser1).choose(eq(cronTask), eq(Cf.list(worker1, worker2, worker3)));
        verify(workerChooser2).choose(eq(cronTask), eq(Cf.list(worker2, worker3)));

        assertThat(chosenWorkers).containsExactly(worker3);
    }

    @Test
    public void onetimeTask() {
        ListF<WorkerMeta> chosenWorkers = workerChooser.choose(onetimeTask, onetimeJob, Cf.list(worker1, worker2, worker3));

        verify(workerChooser1).choose(eq(onetimeTask), eq(onetimeJob), eq(Cf.list(worker1, worker2, worker3)));
        verify(workerChooser2).choose(eq(onetimeTask), eq(onetimeJob), eq(Cf.list(worker2, worker3)));

        assertThat(chosenWorkers).containsExactly(worker3);
    }
}
