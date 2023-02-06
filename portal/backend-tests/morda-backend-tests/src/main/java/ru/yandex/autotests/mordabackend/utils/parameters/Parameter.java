package ru.yandex.autotests.mordabackend.utils.parameters;

import org.apache.http.client.CookieStore;
import org.apache.http.impl.cookie.BasicClientCookie;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.cookie.Cookie;
import ru.yandex.autotests.mordabackend.headers.CookieHeader;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.users.PlainUser;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserManager;
import ru.yandex.autotests.utils.morda.users.UserType;

import javax.ws.rs.client.Client;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordabackend.MordaClient.getRemapHostDnsResolver;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.client.ClientUtils.getCookieStore;
import static ru.yandex.autotests.mordabackend.cookie.CookieName.YANDEX_GID;
import static ru.yandex.autotests.mordabackend.mail.MailUtils.login;
import static ru.yandex.autotests.mordabackend.utils.TuneUtils.setLanguage;
import static ru.yandex.autotests.utils.morda.BaseProperties.MordaEnv;
import static ru.yandex.autotests.utils.morda.url.DomainManager.getMasterDomain;
import static ru.yandex.autotests.utils.morda.users.PlainUser.plainUser;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class Parameter implements Serializable {

    private static ThreadLocal<UserManager> userManager = new ThreadLocal<UserManager>() {
        @Override
        protected UserManager initialValue() {
            return new UserManager();
        }
    };

    public final String protocol;
    public final MordaEnv mordaEnv;
    public final Region region;
    public final Domain domain;
    public final Set<Cookie> cookies;
    public Language language;
    public UserAgent userAgent;
    public UserType userType;
    public ParameterProvider parameterProvider;

    private User user;

    public Parameter(String protocol, MordaEnv mordaEnv, Region region, Set<Cookie> cookies) {
        this.protocol = "https";
        this.mordaEnv = mordaEnv;
        this.region = region;
        this.domain = region.getDomain();
        this.cookies = cookies;
        this.parameterProvider = new EmptyParameterProvider();
    }

    public Parameter(String protocol, MordaEnv mordaEnv, Domain domain, Set<Cookie> cookies) {
        this.protocol = "https";
        this.mordaEnv = mordaEnv;
        this.region = domain.getCapital();
        this.domain = domain;
        this.cookies = cookies;
        this.parameterProvider = new EmptyParameterProvider();
    }

    public Parameter withLanguage(Language language) {
        this.language = language;
        return this;
    }

    public Parameter withUserAgent(UserAgent userAgent) {
        this.userAgent = userAgent;
        return this;
    }

    public Parameter withUserType(UserType userType) {
        this.userType = userType;
        return this;
    }

    public Parameter withProvider(ParameterProvider provider) {
        this.parameterProvider = provider;
        return this;
    }

    public List<Object[]> build(List<CleanvarsBlock> cleanvarsBlocks, boolean withCounters) {
        List<Object> parameters = new ArrayList<>();

        MordaClient mordaClient;
//        if (userAgent != null && userAgent.isMobile() && userAgent.getIsTablet() != 1) {
//            mordaClient = new MordaClient(protocol, mordaEnv, getMasterDomain(this.domain));
//        } else {
        mordaClient = new MordaClient(protocol, mordaEnv, this.domain);
//        }

        Client client = getJsonEnabledClient(getRemapHostDnsResolver());

        if (region != null) {
            cookies.add(new Cookie(YANDEX_GID, region.getRegionId()));
        }
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client)
                .get(new CookieHeader(new ArrayList<>(cookies)), userAgent, Arrays.asList(SK));

        for (Cookie c : cookies) {
            addYandexCookie(client, domain, c);
        }
        user = loginIfNeeded(client, domain, userType, userManager.get(), userAgent);
        setLanguageIfNeeded(mordaClient, client, cleanvars.getSk(), language);

        if (withCounters) {
            cleanvars = mordaClient.cleanvarsActions(client).getWithCounters(userAgent, cleanvarsBlocks);
        } else {
            cleanvars = mordaClient.cleanvarsActions(client).get(userAgent, cleanvarsBlocks);
        }

        parameters.addAll(Arrays.asList(mordaClient, client, cleanvars));
        parameters.addAll(initialParameters());

        return addProvidedParameters(parameters,
                parameterProvider.getParams(mordaClient, client, cleanvars, region, language, userAgent));
    }

    private void addYandexCookie(Client client, Domain domain, Cookie c) {
        CookieStore cs = getCookieStore(client);
        BasicClientCookie yandexDomainCookie = new BasicClientCookie(c.getName(), c.getValue());
        yandexDomainCookie.setDomain(".yandex" + domain);
        cs.addCookie(yandexDomainCookie);
        BasicClientCookie yandexRuCookie = new BasicClientCookie(c.getName(), c.getValue());
        yandexRuCookie.setDomain(".yandex.ru");
        cs.addCookie(yandexRuCookie);
    }

    private User loginIfNeeded(Client client, Domain domain, UserType userType, UserManager userManager, UserAgent userAgent) {
        User user = null;
        if (userType != null) {
            PlainUser uu = plainUser(userType);
            user = userManager.getUser(uu);
            if (userAgent == null) {
                login(user, client, domain);
            } else {
                if (userAgent.isMobile()) {
                    login(user, client, getMasterDomain(domain));
                } else {
                    login(user, client, domain);
                }
            }
        }
        return user;
    }

    public List<Object[]> buildOnlyInitial() {
        List<Object[]> result = new ArrayList<>();
        result.add(initialParameters().toArray());
        return result;
    }

    private void setLanguageIfNeeded(MordaClient mordaClient, Client client, String sk, Language language) {
        if (language != null) {
            setLanguage(mordaClient, client, sk, language);
        }
    }

    private List<Object> initialParameters() {
        List<Object> parameters = new ArrayList<>();
        parameters.add(region);
        if (language != null) {
            parameters.add(language);
        }
        if (userAgent != null) {
            parameters.add(userAgent);
        }
        if (userType != null) {
            parameters.add(userType);
        }
        if (user != null) {
            parameters.add(user);
        }
        return parameters;
    }

    private List<Object[]> addProvidedParameters(List<Object> parameters, List<Object[]> providedParameters) {
        List<Object[]> result = new ArrayList<>();
        if (providedParameters == null) {
            result.add(parameters.toArray());
        } else {
            for (Object[] provided : providedParameters) {
                List<Object> data = new ArrayList<>(parameters);
                data.addAll(Arrays.asList(provided));
                result.add(data.toArray());
            }
        }
        return result;
    }

    @Override
    public String toString() {
        return region + ":" + language + ":" + userAgent;
    }

    public void releaseUser() {
        if (user != null) {
            userManager.get().releaseUser(user);
        }
    }
}
