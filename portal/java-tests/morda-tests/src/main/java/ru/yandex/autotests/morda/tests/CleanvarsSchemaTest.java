package ru.yandex.autotests.morda.tests;

import com.jayway.restassured.response.Response;
import org.junit.Test;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.steps.ValidateSchemaSteps;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/11/16
 */
public class CleanvarsSchemaTest {

    @Test
    public void a() {
        MordaClient client = new MordaClient();
        Response response = client.cleanvars(desktopMain("rc"))
                .readAsResponse();

        ValidateSchemaSteps.validate(response, "/cleanvars/cleanvars-desktop.json");
    }
}
