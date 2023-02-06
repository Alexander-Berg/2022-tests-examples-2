package ru.yandex.metrika.schedulerd.steps;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.kikimr.persqueue.LogbrokerClientFactory;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.qatools.allure.annotations.Step;


@Component
public class SchedulerdSteps {
    private static final Logger log = LoggerFactory.getLogger(SchedulerdSteps.class);

    @Autowired
    protected MySqlJdbcTemplate countersTemplate;

    @Autowired
    protected MySqlJdbcTemplate monitoringTemplate;

    @Autowired
    protected LogbrokerClientFactory logbrokerClientFactory;

    @Step("Подготовка")
    public void prepare() {
        log.debug("Подготовка");

    }

    public MySqlJdbcTemplate getCountersTemplate() {
        return countersTemplate;
    }

    public MySqlJdbcTemplate getMonitoringTemplate() {
        return monitoringTemplate;
    }

    public LogbrokerClientFactory getLogbrokerClientFactory() {
        return logbrokerClientFactory;
    }
}
