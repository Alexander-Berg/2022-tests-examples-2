package ru.yandex.autotests.mordabackend.mail;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.mail.Mail;
import ru.yandex.autotests.mordabackend.beans.mail.MailUser;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.junitextensions.rules.passportrule.PassportRule;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.MAIL;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.MAIL_PATTERN;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.USERS_INFO;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_0;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_1;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_2;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_5;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
//@Aqua.Test(title = "Mail Logged")
//@Features("Mail")
//@Stories("Mail Logged")
//@RunWith(CleanvarsParametrizedRunner.class)
public class LoggedMailTest {

//    @Rule
    public PassportRule passportRule;

//    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.KK, Language.TT, Language.BE)
                    .withUserAgents(FF_34, TOUCH, PDA)
                    .withUserTypes(MAIL_0, MAIL_1, MAIL_2, MAIL_5)
                    .withCleanvarsBlocks(MAIL);//, MAILINFO);


    private final Language language;
    private final Client client;
    private final Region region;
    private final UserAgent userAgent;
    private final UserType userType;
    private User user;
    private Cleanvars cleanvars;

    public LoggedMailTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                          Region region, Language language, UserAgent userAgent, UserType userType, User user) {
        this.client = client;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.userType = userType;
        this.user = user;
        this.cleanvars = cleanvars;
    }

//    @Test
    public void loggedFlag() {
        shouldHaveParameter(cleanvars.getMail().getLogged(), equalTo(1));
    }

//    @Test
    public void login() {

        for(MailUser mailUser: cleanvars.getMail().getUsers()){
            shouldHaveParameter("Failed with user: " + mailUser.getEmail(),
                    mailUser.getUserName().getStr(),
                    equalTo(user.getLogin()));
        }

        shouldHaveParameter(cleanvars.getMail().getEmail().replace("<wbr/>", ""),
                equalTo(user.getLogin()));
    }

//    @Test
    public void email(){
        shouldHaveParameter(cleanvars.getMail().getUsers().get(0).getEmail(),
                equalTo(user.getLogin() + "@yandex.ru"));
    }

//    @Test
    public void unreadMail() {
        shouldHaveParameter(cleanvars.getMail(),
                having(on(Mail.class).getCount(),
                        equalTo(USERS_INFO.get(userType).getCount()))
        );

        MailUser mailUser = cleanvars.getMail().getUsers().get(0);

        shouldHaveParameter(
                mailUser.getMailInfo().getUnread(),
                        equalTo(USERS_INFO.get(userType).getCount())
        );

    }

//    @Test
    public void mailFullCountAccus() {
        String fullCountAccus = USERS_INFO.get(userType).getFullCountAccus(language);
        shouldHaveParameter("Failed with user: " + user.getLogin(),
                cleanvars.getMail(), having(on(Mail.class).getFullcountaccus(), equalTo(fullCountAccus)));
    }

//    @Test
    public void mailCountAccus() {
        String countAccus = USERS_INFO.get(userType).getCountAccus(language);
        shouldHaveParameter("Failed with user: " + user.getLogin(),
                cleanvars.getMail(), having(on(Mail.class).getCountaccus(), equalTo(countAccus)));
    }

//    @Test
    public void noAuthReason() {
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getNoAuthReason(), nullValue()));
    }

//    @Test
    public void href() throws IOException {
        assumeFalse("Нет ссылки на десктопной COM.TR", region.getDomain().equals(COM_TR));
        shouldHaveParameter(cleanvars.getMail(), having(on(Mail.class).getHref(),
                equalTo(String.format(MAIL_PATTERN, region.getDomain()))));
        addLink(cleanvars.getMail().getHref(), region, true, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getMail().getHref(), userAgent, equalTo(200));
    }
}
