package ru.yandex.autotests.mordatmplerr.rules;

import ch.lambdaj.function.matcher.Predicate;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.hamcrest.Matcher;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.qatools.allure.annotations.Attachment;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.Response;
import java.net.URI;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.filter;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.junit.Assert.assertThat;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21.03.14
 */
public class LogsRule extends TestWatcher {
    private static final Logger LOG = Logger.getLogger(LogsRule.class);
    private static final Properties CONFIG = new Properties();
    private static final String LOGS_URL_PATTERN = "http://%s.yandex.ru/morda-kitty.error_log";
    private static final String TMPL_ERROR = "[tmplerror]";
    private YandexUidRecorderAction yandexUidRecorderAction;
    private String logsUrl;

    public LogsRule() {
        this.logsUrl = String.format(LOGS_URL_PATTERN, CONFIG.getMordaEnv());
    }

    public LogsRule(YandexUidRecorderAction yandexUidRecorderAction) {
        this.logsUrl = String.format(LOGS_URL_PATTERN, CONFIG.getMordaEnv());
        this.yandexUidRecorderAction = yandexUidRecorderAction;
    }

    @Override
    protected void finished(Description description) {
        List<String> logs = getLogs(yandexUidRecorderAction.getAllYandexUids());
        LOG.info("yandexuids: " + yandexUidRecorderAction.getAllYandexUids());
        List<String> errors = getErrors(logs, yandexUidRecorderAction.getAllYandexUids());
        attachLogs(logs);
        attachErrors(errors);
        LOG.info(this.toString() + " " + yandexUidRecorderAction.toString() + " " +
                yandexUidRecorderAction.getAllYandexUids());
        assertThat("В логах есть ошибки", errors, hasSize(0));
    }

    public List<String> getLogs() {
        Client client = MordaClient.getJsonEnabledClient();
        Response response = client.target(URI.create(logsUrl)).request().buildGet().invoke();
        List<String> res = Arrays.asList(response.readEntity(String.class).split("\n"));
        return res;
    }

    public List<String> getLogs(final Collection<String> uids) {
        List<String> logs = getLogs();
        return filter(hasUidMatcher(uids), logs);
    }

    public List<String> getErrors(List<String> logs) {
        return filter(containsString(TMPL_ERROR), logs);
    }

    public List<String> getErrors(List<String> logs, final Collection<String> uids) {
        return filter(hasUidMatcher(uids), getErrors(logs));
    }

    private Matcher<String> hasUidMatcher(final Collection<String> uids) {
        return new Predicate<String>() {
            @Override
            public boolean apply(String item) {
                for (String uid : uids) {
                    if (item.contains(uid)) {
                        return true;
                    }
                }
                return false;
            }
        };
    }

    @Attachment("{0}")
    public String attach(String name, String string) {
        LOG.info(string);
        return string;
    }

    @Attachment("logs")
    public String attachLogs(List<String> logs) {
        String l = StringUtils.join(logs, "\n");
        return l;
    }

    @Attachment("errors")
    public String attachErrors(List<String> errors) {
        String err;
        if (errors.isEmpty()) {
            err = "No errors!";
        } else {
            err = StringUtils.join(errors, "\n");
        }
        return err;
    }
}
