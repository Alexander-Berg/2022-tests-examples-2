package ru.yandex.autotests.mordalinks;

import org.apache.http.HttpHost;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.apache.http.protocol.HttpCoreContext;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.Logger;
import org.glassfish.jersey.client.ClientProperties;
import org.glassfish.jersey.client.ClientResponse;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.actions.TuneActions;
import ru.yandex.autotests.mordabackend.client.ClientUtils;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordalinks.beans.MordaConditions;
import ru.yandex.autotests.mordalinks.beans.MordaLink;
import ru.yandex.autotests.mordalinks.beans.Url;
import ru.yandex.autotests.mordalinks.utils.MordaHttpClient;
import ru.yandex.autotests.mordalinks.utils.MordaLinkUtils;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.DomainManager;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserManager;
import ru.yandex.junitextensions.rules.passportrule.PassportRule;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.Invocation;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.lang.reflect.Field;
import java.net.URI;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.mordalinks.utils.NormalizeUtils.normalizeOnCheck;
import static ru.yandex.autotests.mordalinks.utils.NormalizeUtils.normalizeOnCompare;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getSecretKey;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.CHANGE_LANG_PATTERN;
import static ru.yandex.autotests.utils.morda.users.PlainUser.plainUser;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03.06.14
 */
public class CheckLinkTask implements Runnable {
    private static final Logger LOG = Logger.getLogger(CheckLinkTask.class);
    private final MordaLink link;
    private User user;
    private final List<MordaLink> linksWithErrors;

    public CheckLinkTask(MordaLink link, List<MordaLink> linksWithErrors) {
        this.link = link;
        this.linksWithErrors = linksWithErrors;
    }

    private static final Map<Language, String> MY_COOKIE_MAP = new HashMap<Language, String>() {{
        put(Language.RU, "YycCAAEA");
        put(Language.UK, "YycCAAIA");
        put(Language.TT, "YycCAAYA");
        put(Language.KK, "YycCAAQA");
        put(Language.BE, "YycCAAUA");
    }};

    @Override
    public void run() {
        try {
            ThreadLocal<Client> client = new ThreadLocal<Client>();
            Client cl = MordaClient.getJsonEnabledClient();
            cl.property(ClientProperties.CONNECT_TIMEOUT, 2000);
            cl.property(ClientProperties.READ_TIMEOUT,    2000);

            client.set(cl);

            Region region = getRegion(link.getCond().getGid());

            String yandexGidCookie = "yandex_gid=" + link.getCond().getGid();

            Invocation.Builder init;

            if (region.getDomain().equals(Domain.COM_TR) || region.getDomain().equals(Domain.COM)) {
                init = client.get()
                        .target(URI.create("http://www.yandex" + region.getDomain()))
                        .request();
            } else {
                if (link.getCond().getUa() != null) {
                    UserAgent ua = UserAgent.valueOf(link.getCond().getUa().getId());
                    if (ua.isMobile()) {
                        init = client.get()
                                .target(URI.create("http://www.yandex.ru"))
                                .request();
                    } else {
                        init = client.get()
                                .target(URI.create("http://www.yandex" + region.getDomain()))
                                .request();
                    }
                } else {
                    init = client.get()
                            .target(URI.create("http://www.yandex" + region.getDomain()))
                            .request();
                }
            }
            init.header("Cookie", yandexGidCookie)
                    .get()
                    .close();

            TuneActions tuneActions = new TuneActions(null, client.get());
            tuneActions.setRegion(region);

            Invocation.Builder request = client.get()
                    .target(URI.create(link.getHref()))
                    .request();

            if (link.getCond().getLang() != null) {
                String my = MY_COOKIE_MAP.get(Language.getLanguage(link.getCond().getLang()));
                BasicClientCookie cookie = new BasicClientCookie("my", my);
                cookie.setDomain(".yandex.ru");
                BasicClientCookie cookie2 = new BasicClientCookie("my", my);
                cookie2.setDomain(".yandex" + DomainManager.getMasterDomain(region.getDomain()));
                ClientUtils.getCookieStore(client.get()).addCookie(cookie);
                ClientUtils.getCookieStore(client.get()).addCookie(cookie2);
            }

            if (link.getCond().getUa() != null) {
                request = request.header("User-Agent", link.getCond().getUa().getValue());
            }

            Response response = request.get();

            Field context = response.getClass().getDeclaredField("context");
            context.setAccessible(true);
            Object c = context.get(response);

            if (c instanceof ClientResponse) {
                ClientResponse r = (ClientResponse) context.get(response);
                Field resolvedUri = r.getClass().getDeclaredField("resolvedUri");
                resolvedUri.setAccessible(true);
                System.out.println(link.getHref() + " -> " + resolvedUri.get(r));
                MordaLinkUtils.updateLink(link.getId(), new Url().withCandidate(normalizeOnCompare(((URI) resolvedUri.get(r)).toString())));
            }

            client.get().close();
        } catch (Throwable e) {
            linksWithErrors.add(link);
            e.printStackTrace();
        }
//        MordaHttpClient client = link.getCond().getUa() == null ?
//                new MordaHttpClient() : new MordaHttpClient(link.getCond().getUa().getValue());
//        try {
//
//            String newUrl = getTargetUrl(client, link);
//            MordaLinkUtils.updateLink(link.getId(), new Url().withCandidate(normalizeOnCompare(newUrl)));
//        } catch (Exception e) {
//            LOG.error("Error during link check", e);
//            synchronized (linksWithErrors) {
//                linksWithErrors.add(link);
//            }
//        } finally {
//            HttpClientUtils.closeQuietly(client.getHttpClient());
//            if (user != null) {
//                new UserManager().releaseUser(user);
//            }
//        }
    }

    private void prepareHttpClient(MordaHttpClient client, MordaConditions conditions) {
        HttpGet mordaGet = new HttpGet();
        executeGet(client, "http://www.yandex" + getRegion(conditions.getGid()).getDomain());

        if (conditions.isAuth()) {
            user = new UserManager().getUser(plainUser(DEFAULT));
            new PassportRule(client.getHttpClient()).withLoginPassword(user.getLogin(), user.getPassword()).login();
        }
        for (Domain d : Domain.values()) {
            BasicClientCookie cookie = new BasicClientCookie("yandex_gid", String.valueOf(conditions.getGid()));
            cookie.setDomain(".yandex" + d.toString());
            client.getCookieStore().addCookie(cookie);
        }
        if (conditions.getLang() != null) {
            String url = String.format(CHANGE_LANG_PATTERN,
                    conditions.getLang(), "", getSecretKey(client.getCookieStore())
            );
            executeGet(client, url);
        }
    }

    private Region getRegion(int gid) {
        for (Region r : Region.values()) {
            if (r.getRegionIdInt() == gid) {
                return r;
            }
        }
        throw new RuntimeException("Region with gid " + gid + " not found");
    }

    private void executeGet(MordaHttpClient client, String url) {
        try {
            EntityUtils.consume(client.executeGet(url).getEntity());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public String getTargetUrl(MordaLink link) {
        return getTargetUrl(
                link.getCond().getUa() == null ?
                        new MordaHttpClient() : new MordaHttpClient(link.getCond().getUa().getValue()),
                link
        );
    }

    public String getTargetUrl(MordaHttpClient client, MordaLink link) {
        prepareHttpClient(client, link.getCond());

        executeGet(client, normalizeOnCheck(link.getHref(), client.getCookieStore()));

        HttpUriRequest currentReq = (HttpUriRequest) client.getHttpContext().getAttribute(HttpCoreContext.HTTP_REQUEST);
        HttpHost currentHost = (HttpHost) client.getHttpContext().getAttribute(HttpCoreContext.HTTP_TARGET_HOST);

        String targetUrl = (currentReq.getURI().isAbsolute()) ? currentReq.getURI().toString()
                : (currentHost.toURI() + currentReq.getURI());
        return targetUrl;
    }
}
