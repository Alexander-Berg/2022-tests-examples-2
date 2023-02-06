package ru.yandex.autotests.mordatmplerr.logs;

import org.junit.Test;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.rules.LogsRule;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.List;

import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.03.14
 */
@Aqua.Test(title = "Full Logs")
@Features("Full Logs")
public class TmplErrLogsTest {
    private static final Properties CONFIG = new Properties();

    @Test
    public void logs() {
        LogsRule rule = new LogsRule();
        List<String> errors = rule.getErrors(rule.getLogs());
        rule.attachErrors(errors);
        assertThat("В логах есть ошибки", errors, hasSize(0));
    }
}
