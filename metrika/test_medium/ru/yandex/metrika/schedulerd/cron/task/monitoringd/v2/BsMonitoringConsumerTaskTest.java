package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.schedulerd.cron.task.monitoringd.DomainCountersDao;
import ru.yandex.metrika.util.json.ObjectMappersFactory;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.Assert.assertTrue;

@Stories("Monitoring consumer task")
public class BsMonitoringConsumerTaskTest extends MonitoringBaseTest {


    private BsMonitoringConsumerTask task;
    private Set<MonitoringState> states;
    private MonitoringStateDao dao;

    @Before
    public void setUp() throws Exception {
        super.setUp();
        stepsMon.cleanMonitoring(MonitoringStateDao.TABLE);
        dao = new MonitoringStateDao(
                monitoringTemplate
        );
        DomainCountersDao domainCountersDao = new DomainCountersDao();
        domainCountersDao.setJdbcTemplate(countersTemplate);

        task = new BsMonitoringConsumerTask(
                stepsLb.getSubscriber(),
                ObjectMappersFactory.getDefaultMapper(),
                new MonitoringHelper(
                        domainCountersDao
                ),
                dao
        );
        task.setMaxExecutionTimeMinutes(1);
    }

    @After
    public void tearDown() throws Exception {
        task = null;
        states = null;
        dao = null;
        super.tearDown();
    }

    @Override
    public List<byte[]> getLbTopicData() {
        states = new HashSet<>();
        return this.generateLbMessages(10, states);
    }

    @Test
    @Title("Проверка работы консумера")
    public void checkConsumerTask() throws Exception {
        task.execute();
        List<MonitoringState> stateList = dao.readFlapping();
        assertTrue(stateList.stream().allMatch(MonitoringState::isCommited));
        assertTrue(stepsMon.compareMonitoringStates(
                states.stream().sorted(Comparator.comparing(MonitoringState::getCheckedTime)).collect(Collectors.toList()),
                stateList.stream().sorted(Comparator.comparing(MonitoringState::getCheckedTime)).collect(Collectors.toList())
                )
        );
    }
}
