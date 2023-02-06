package ru.yandex.autotests.morda.tests.set.tune;

import com.jayway.restassured.response.Response;
import org.junit.Rule;
import org.junit.Test;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.set.SetSteps;

import java.util.function.Consumer;

/**
 * User: asamar
 * Date: 07.11.16
 */
public class BaseSetTuneTest {
    private Response response;
    private Morda<?> morda;
    private String param;
    private String value;
    protected SetSteps user;
    protected Consumer<Response> checker;

    @Rule
    public AllureLoggingRule rule = new AllureLoggingRule();

    public BaseSetTuneTest(Morda<?> morda, String param, String value) {
        this.morda = morda;
        this.param = param;
        this.value = value;
        this.user = new SetSteps();
    }

    @Test
    public void check() {
        checker.accept(response);
    }

    protected void setTuneGet() {
        MordaClient mordaClient = new MordaClient();
        MordaCleanvars cleanvars = mordaClient.cleanvars(morda.getUrl()).read();

        this.response = mordaClient
                .set(morda.getUrl())
                .tuneGet(cleanvars.getSk(), param, value, morda.getUrl().toString())
                .readAsResponse();
    }

    protected void setTunePost() {
        MordaClient mordaClient = new MordaClient();
        MordaCleanvars cleanvars = mordaClient.cleanvars(morda.getUrl()).read();

        this.response = mordaClient
                .set(morda.getUrl())
                .tunePost(cleanvars.getSk(), param, value, morda.getUrl().toString())
                .readAsResponse();
    }

}
