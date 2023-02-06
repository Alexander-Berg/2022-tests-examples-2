package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.List;

import io.qameta.allure.Step;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.schedulerd.steps.SchedulerdSteps;

public class MonitoringSteps extends SchedulerdSteps {
    private static final Logger log = LoggerFactory.getLogger(MonitoringSteps.class);

    private final SchedulerdSteps baseSteps;

    public MonitoringSteps(SchedulerdSteps baseSteps) {
        this.baseSteps = baseSteps;

        this.monitoringTemplate = baseSteps.getMonitoringTemplate();
        this.countersTemplate = baseSteps.getCountersTemplate();
    }


    @Step("Получить все записи мониторинга")
    public List<MonitoringState> getAll() {
        return monitoringTemplate.query(
                "SELECT " + MonitoringState.COLUMNS + " " +
                        "FROM " + MonitoringStateDao.TABLE + " " +
                        "ORDER BY id", MonitoringState.ROW_MAPPER
        );
    }

    @Step("Сравнение результатов")
    public boolean compareMonitoringStates(List<MonitoringState> expected, List<MonitoringState> actual) {
        if (expected.size() != actual.size()) {
            return false;
        }

        MonitoringState[] expectedArr = expected.toArray(new MonitoringState[0]);
        MonitoringState[] actualArr = actual.toArray(new MonitoringState[0]);

        boolean result = true;
        for (int idx = 0; idx < expectedArr.length; idx++) {
            MonitoringState actualItem = actualArr[idx];
            MonitoringState expectedItem = expectedArr[idx];
            result = result && expectedItem.getCounterId() == actualItem.getCounterId() &&
                    expectedItem.getHttpCode() == actualItem.getHttpCode() &&
                    expectedItem.getDomain().equals(actualItem.getDomain()) &&
                    Math.abs(expectedItem.getCheckedTime().getMillis() - actualItem.getCheckedTime().getMillis()) < 1500
            ;
        }

        return result;
    }

    @Step
    public void commit() {
        monitoringTemplate.execute("COMMIT;");
    }

    public void cleanMonitoring(String table) {
        monitoringTemplate.execute("DELETE FROM " + table + ";");
    }

    public void cleanCounters(String table) {
        countersTemplate.execute("DELETE FROM " + table + ";");
    }

}
