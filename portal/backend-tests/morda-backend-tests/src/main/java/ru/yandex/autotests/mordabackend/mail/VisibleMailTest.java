package ru.yandex.autotests.mordabackend.mail;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.mail.Mail;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.Arrays;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MAIL;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.VISIBLE_SET_PATTERN;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.VISIBLE_SET_PATTERN_COM_TR;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
@Aqua.Test(title = "Mail Visibility")
@Features("Mail")
@Stories("Mail Visibility")
@RunWith(CleanvarsParametrizedRunner.class)
public class VisibleMailTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE, Language.TR)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(MAIL, SK);

    private final Client client;
    private final MordaClient mordaClient;
    private final Cleanvars cleanvars;
    private final UserAgent userAgent;
    private final Region region;

    public VisibleMailTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.client = client;
        this.mordaClient = mordaClient;
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
    }

    @Test
    public void defaultVisibleFlag() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getShow(), equalTo(1)));
    }

    @Test
    public void visibleSettingOff() throws IOException {
        String pattern = COM_TR.equals(region.getDomain()) ?
                VISIBLE_SET_PATTERN_COM_TR : VISIBLE_SET_PATTERN;

        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getVisibleSetOff(),
                equalTo(String.format(pattern, region.getDomain(),
//                        getExpectedDomain(region.getDomain(), userAgent).getValue().substring(1),
                        cleanvars.getSk(), 1))));
        shouldHaveResponseCode(client, cleanvars.getMail().getVisibleSetOff(), userAgent, equalTo(200));

        shouldHaveParameter(mordaClient.cleanvarsActions(client).get(userAgent, Arrays.asList(MAIL)).getMail(),
                having(on(Mail.class).getVisible(), equalTo(0)));
    }

    @Test
    public void visibleSettingOffThenOn() throws IOException {
        String pattern = COM_TR.equals(region.getDomain()) ?
                VISIBLE_SET_PATTERN_COM_TR : VISIBLE_SET_PATTERN;

        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getVisibleSetOff(),
                equalTo(String.format(pattern, region.getDomain(),
//                        getExpectedDomain(region.getDomain(), userAgent).getValue().substring(1),
                        cleanvars.getSk(), 1))));
        shouldHaveResponseCode(client, cleanvars.getMail().getVisibleSetOff(), userAgent, equalTo(200));

        Cleanvars intermediateCleanvars = mordaClient.cleanvarsActions(client).get(userAgent, Arrays.asList(MAIL, SK));
        shouldHaveParameter(intermediateCleanvars.getMail(), having(on(Mail.class).getVisible(), equalTo(0)));

        shouldHaveParameter(intermediateCleanvars.getMail(), having(on(Mail.class).getVisibleSetOn(),
                equalTo(String.format(pattern, region.getDomain(),
//                        userAgent.isMobile() ?
//                                getMasterDomain(region.getDomain()).getValue().substring(1) :
//                                region.getDomain().getValue().substring(1),
                        intermediateCleanvars.getSk(), 0))));
        shouldHaveResponseCode(client, intermediateCleanvars.getMail().getVisibleSetOn(), userAgent, equalTo(200));

        shouldHaveParameter(mordaClient.cleanvarsActions(client).get(userAgent, Arrays.asList(MAIL)).getMail(),
                having(on(Mail.class).getVisible(), equalTo(1)));
    }
}
