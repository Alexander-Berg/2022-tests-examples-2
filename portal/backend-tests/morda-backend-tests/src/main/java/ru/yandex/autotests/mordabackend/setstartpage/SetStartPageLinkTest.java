package ru.yandex.autotests.mordabackend.setstartpage;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.cookie.YpCookieUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.Collections;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SET_START_PAGE_LINK;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Set Start Page Flag")
@Features("Set Start Page")
@Stories("Set Start Page Flag")
@RunWith(CleanvarsParametrizedRunner.class)
public class SetStartPageLinkTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(SET_START_PAGE_LINK);

    private MordaClient mordaClient;
    private UserAgent userAgent;
    private Region region;
    private Client client;
    private Cleanvars cleanvars;

    public SetStartPageLinkTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, UserAgent userAgent) {
        this.mordaClient = mordaClient;
        this.userAgent = userAgent;
        this.region = region;
        this.client = client;
        this.cleanvars = cleanvars;
    }

    @Test
    public void flagExists() {
        shouldMatchTo(cleanvars.getSetStartPageLink(), equalTo(1));
    }

    @Test
    public void flagNotExistsWithClh() {
        String clhSubcookie = "3147483647.clh.2122758";
        YpCookieUtils.addToYpCookie(client, region, clhSubcookie);
        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client)
                .get(userAgent, Collections.singletonList(SET_START_PAGE_LINK));
        shouldMatchTo(newCleanvars.getSetStartPageLink(), equalTo(0));
    }
}
