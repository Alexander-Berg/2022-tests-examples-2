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

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MAIL;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MAILINFO;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
@Aqua.Test(title = "Mail Not Logged")
@Features("Mail")
@Stories("Mail Not Logged")
@RunWith(CleanvarsParametrizedRunner.class)
public class NotLoggedMailTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(MAIL, MAILINFO);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;

    public NotLoggedMailTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getShow(), equalTo(1)));
    }

    @Test
    public void loggedFlag() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getLogged(), equalTo(0)));
//        shouldHaveParameter(cleanvars.getMailInfo(), having(on(MailInfo.class).getLogged(), equalTo(0)));
    }

    @Test
    public void liteUser() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getLiteUser(), nullValue()));
    }

    @Test
    public void banner() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getBanner(), nullValue()));
    }

    @Test
    public void href() throws IOException {
        assumeFalse("Нет ссылки на десктопной COM.TR", region.getDomain().equals(COM_TR));
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getHref(),
                equalTo(String.format(MAIL_PATTERN, region.getDomain()))));
        addLink(cleanvars.getMail().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMail().getHref(), userAgent, equalTo(200));
    }

    @Test
    public void nomailbox() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getNomailbox(), nullValue()));
    }

    @Test
    public void showsetup() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getShowsetup(), nullValue()));
//        shouldHaveParameter(cleanvars.getMailInfo(), having(on(MailInfo.class).getShowsetup(), nullValue()));
    }

//    @Test
    public void socialinit() {
        shouldHaveSocialInit(cleanvars.getMail().getSocialinit(), region.getDomain(), language);
    }

    @Test
    public void noAuthReason() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getNoAuthReason(),
                equalTo(DEFAULT_NO_AUTH_REASON)));
//        shouldHaveParameter(cleanvars.getMailInfo(), having(on(MailInfo.class).getNoAuthReason(),
//                equalTo(DEFAULT_NO_AUTH_REASON)));
    }
}
