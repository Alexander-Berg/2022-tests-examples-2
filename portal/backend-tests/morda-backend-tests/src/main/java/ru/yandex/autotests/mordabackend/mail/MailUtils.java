package ru.yandex.autotests.mordabackend.mail;

import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import ru.yandex.autotests.dictionary.Plural;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.mail.SocialInit;
import ru.yandex.autotests.mordabackend.beans.mail.SocialInitList;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.junitextensions.rules.passportrule.PassportRule;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.dictionary.Plural.MANY;
import static ru.yandex.autotests.dictionary.Plural.ONE;
import static ru.yandex.autotests.dictionary.Plural.SOME;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.UserInfo.info;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_0;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_1;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_2;
import static ru.yandex.autotests.utils.morda.users.UserType.MAIL_5;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsListMatcher.hasSameItemsAsList;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
public class MailUtils {
    private static final Properties CONFIG = new Properties();

    public static final String MAIL_PATTERN = "https://mail.yandex%s/";
    public static final String VISIBLE_SET_PATTERN = CONFIG.getProtocol() + "://" + CONFIG.getMordaEnv().getEnv() +
            ".yandex%s/portal/set/any/?sk=%s&empty=1&mv=%s";

    public static final String VISIBLE_SET_PATTERN_COM_TR = CONFIG.getProtocol() + "://" + CONFIG.getMordaEnv().getEnv() +
            ".yandex%s/portal/set/any/?sk=%s&empty=1&mv=%s";
    public static final String DEFAULT_NO_AUTH_REASON = "no-session";

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT, TR);

    public static final String HOME = "home";
    public static final String MAIL_KEYSET = "mail";

    public static final String USERS_MAIL_DOMAIN = "yandex.ru";

    public static final String HTTPS_PASSPORT_URL_PATTERN = "https://passport.yandex%s/";

    public static Map<Language, List<SocialInit>> KUBR_AUTH_CODES = new HashMap<Language, List<SocialInit>>() {{
        for (Language l :LANGUAGES) {
            put(l, Arrays.asList(
                    buildSocial("vk", 1, getTranslation(HOME, MAIL_KEYSET, "preferences.vk", l), true, true),
                    buildSocial("fb", 2, getTranslation(HOME, MAIL_KEYSET, "preferences.fb", l), true, true),
                    buildSocial("tw", 3, getTranslation(HOME, MAIL_KEYSET, "preferences.tw", l), true, true),
                    buildSocial("mr", 4, "Mail.ru", false, true),
                    buildSocial("gg", 5, "Google", false, true),
                    buildSocial("ok", 6, getTranslation(HOME, MAIL_KEYSET, "preferences.odnokl", l), false, true)
            ));
        }
    }};

    public static final Map<Language, List<SocialInit>> COMTR_AUTH_CODES = new HashMap<Language, List<SocialInit>>() {{
        for (Language l :LANGUAGES) {
            put(l, Arrays.asList(
                    buildSocial("fb", 2, getTranslation(HOME, MAIL_KEYSET, "preferences.fb", l), true, true),
                    buildSocial("tw", 3, getTranslation(HOME, MAIL_KEYSET, "preferences.tw", l), true, true),
                    buildSocial("gg", 5, "Google", true, true)
            ));
        }
    }};
    public static final Map<UserType, UserInfo> USERS_INFO = new HashMap<UserType, UserInfo>() {{
        put(MAIL_0, info(0, MANY));
        put(MAIL_1, info(1, ONE));
        put(MAIL_2, info(2, SOME));
        put(MAIL_5, info(5, MANY));
    }};

    @Step
    public static void shouldHaveSocialInit(SocialInitList socialinit, Domain domain, Language language) {
        List<SocialInit> expectedAuthCodes = getExpectedAuthCodes(domain, language);
        assertThat("Not valid auth set", socialinit.getList(), hasSameItemsAsList(expectedAuthCodes));
    }

    @Step
    public static void login(User user, Client client, Domain domain) {
        try {
            new PassportRule(ApacheConnectorProvider.getHttpClient(client))
                    .onHost(new URL(String.format(HTTPS_PASSPORT_URL_PATTERN, domain)))
                    .withLoginPassword(user.getLogin(), user.getPassword())
                    .login();
        } catch (MalformedURLException e) {
            e.printStackTrace();
            throw new RuntimeException("Can't login", e);
        }
    }

    private static List<SocialInit> getExpectedAuthCodes(Domain domain, Language lang) {
        if (domain.equals(Domain.COM_TR)) {
            return COMTR_AUTH_CODES.get(lang);
        } else if (domain.equals(Domain.KZ) || domain.equals(Domain.UA) ||
                domain.equals(Domain.BY) || domain.equals(Domain.RU)) {
            return KUBR_AUTH_CODES.get(lang);
        }
        return Collections.emptyList();
    }

    public static SocialInit buildSocial(String code, int id, String displayName, boolean primary, boolean enabled) {
        SocialInit ret = new SocialInit();
        ret.setCode(code);
        ret.setId(id);
        ret.setDisplayName(displayName);
        ret.setPrimary(primary);
        ret.setEnabled(enabled);
        return ret;
    }

    public static class UserInfo {
        private int count;
        private Plural plural;

        public UserInfo(int count, Plural plural) {
            this.count = count;
            this.plural = plural;
        }

        public static UserInfo info(int count, Plural plural) {
            return new UserInfo(count, plural);
        }

        public int getCount() {
            return count;
        }

        public String getFullCountAccus(Language language) {
            return getTranslation("home", "main", "new_mail_count", plural, language);
        }

        public String getCountAccus(Language language) {
            return getTranslation("home", "main", "new_mail_count_mobile", plural, language);
        }
    }
}
