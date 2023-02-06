package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import net.lightbody.bmp.proxy.http.RequestCallback;
import org.apache.http.Header;
import org.apache.http.StatusLine;
import org.apache.http.message.BasicHeader;
import ru.yandex.autotests.morda.rules.proxy.actions.CookieAction;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;

import java.util.List;

import static java.util.Arrays.stream;
import static java.util.stream.Collectors.toList;


/**
 * User: asamar
 * Date: 04.09.2015.
 */
public class WebDriverCookieAction extends CookieAction<MordaBaseWebDriverRule> {

    private static final String SET_COOKIE_HEADER = "Set-Cookie";

    public WebDriverCookieAction(MordaBaseWebDriverRule rule) {
        super(rule);
        rule.register(this);
    }

    public static WebDriverCookieAction webDriverCookieAction(MordaBaseWebDriverRule rule) {
        return new WebDriverCookieAction(rule);
    }

    @Override
    public void perform() {
        if (!isEnabled()) {
            return;
        }
        super.perform();
        rule.getProxyServer().addRequestInterceptor((BrowserMobHttpRequest request, Har har) -> {
            final RequestCallback callback = request.getRequestCallback();

            request.setRequestCallback(new RequestCallback() {

                @Override
                public void handleStatusLine(StatusLine statusLine) {
                    callback.handleStatusLine(statusLine);
                }

                @Override
                public void handleHeaders(Header[] headers) {
                    List<Header> headersList = stream(headers)
//                            .filter(WebDriverCookieAction.this::deleteSetCookiesHeader)
                            .filter(e -> deleteSetCookiesHeader(e))
//                            .map(WebDriverCookieAction.this::overrideCookie)
                            .map(it -> overrideCookie(it))
                            .collect(toList());

                    cookiesToAdd.entrySet().forEach(
                            e -> headersList.add(new BasicHeader(SET_COOKIE_HEADER, e.getValue().toString()))
                    );

                    callback.handleHeaders(headersList.stream().toArray(Header[]::new));
                }

                @Override
                public boolean reportHeader(Header header) {
                    return callback.reportHeader(header);
                }

                @Override
                public void reportError(Exception e) {
                    callback.reportError(e);
                }
            });
        });
    }

    private Header overrideCookie(Header header) {
        if (header.getName().equals(SET_COOKIE_HEADER) &&
                cookiesToOverride.containsKey(header.getElements()[0].getName())) {

            CookieData overrideData = cookiesToOverride.get(header.getElements()[0].getName());

            return new BasicHeader(
                    header.getName(),
                    header.getValue().replaceAll("(?<=^\\Q" + overrideData.name + "\\E=)[^;]+(?=;.*)", overrideData.value)
            );
        }
        return header;
    }

    private boolean deleteSetCookiesHeader(Header header) {
        return !(header.getName().equals(SET_COOKIE_HEADER) &&
                cookiesToDelete.contains(header.getElements()[0].getName()));
    }
}
