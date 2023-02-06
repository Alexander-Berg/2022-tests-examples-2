package ru.yandex.autotests.mordabackend.links;

import org.apache.commons.lang3.StringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.WITHOUT_BANNER_DEBUG;
import static ru.yandex.autotests.mordabackend.links.LinksUtils.getLinksPattern;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "All links")
@Features("Links")
@Stories("All links")
@RunWith(CleanvarsParametrizedRunner.class)
public class AllLinksTest {
    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM, COM_TR)
                    .withUserAgents(FF_34, PDA, TOUCH, ANDROID_HTC_SENS, WP8)
                    .withCleanvarsBlocks(SK);


    private MordaClient mordaClient;
    private UserAgent userAgent;
    private Region region;
    private Client client;

    public AllLinksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, UserAgent userAgent) {
        this.mordaClient = mordaClient;
        this.userAgent = userAgent;
        this.region = region;
        this.client = client;
    }

    @Test
    public void allLinks() {
        Matcher m = getLinksPattern(userAgent).matcher(mordaClient.cleanvarsActions(client).getAsString(userAgent,
                Collections.singletonList(WITHOUT_BANNER_DEBUG)));
        List<String> unexpectedHosts = new ArrayList<>();
        while (m.find()) {
            unexpectedHosts.add(m.group());
        }
        if (!unexpectedHosts.isEmpty()) {
            fail("Find unexpected hosts:\n" + StringUtils.join(unexpectedHosts, ",\n"));
        }
    }
}
