package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.schedulerd.cron.task.monitoringd.DomainCountersDao;
import ru.yandex.metrika.util.json.ObjectMappersFactory;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Stories("Full test for monitoring")
public class MonitoringCompleteTest extends MonitoringBaseTest {

    private MonitoringStateDao daoMon;
    private ObjectMapper defaultMapper;
    private DomainCountersDao domainCountersDao;
    private MonitoringHelper helperMon;
    private Set<MonitoringState> states;

    private BsMonitoringConsumerTask consumerTask;
    private BsMonitoringFlapReduceTask flapReducerTask;
    private BsMonitoringCleaningTask cleanTask;

    @Before
    public void setUp() throws Exception {
        super.setUp();
        stepsMon.cleanMonitoring(MonitoringStateDao.TABLE);
        defaultMapper = ObjectMappersFactory.getDefaultMapper();
        daoMon = new MonitoringStateDao(monitoringTemplate);
        domainCountersDao = new DomainCountersDao();
        domainCountersDao.setJdbcTemplate(countersTemplate);
        helperMon = new MonitoringHelper(domainCountersDao);

        consumerTask = new BsMonitoringConsumerTask(
                stepsLb.getSubscriber(),
                defaultMapper,
                helperMon,
                daoMon
        );
        consumerTask.setMaxExecutionTimeMinutes(1);

        flapReducerTask = new BsMonitoringFlapReduceTask(daoMon);
        flapReducerTask.setMaxExecutionTimeMinutes(0);

        cleanTask = new BsMonitoringCleaningTask(daoMon);
    }

    @Override
    public List<byte[]> getLbTopicData() {
        states = new HashSet<>();
        return this.generateLbMessages(400, states);
    }

    @Test
    @Title("Проверка работы цепочки из всех тасок мониторинга")
    public void checkTaskChain() throws Exception {
        consumerTask.execute();
        flapReducerTask.execute();
//        cleanTask.execute();
    }
}
