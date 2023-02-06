package ru.yandex.autotests.morda.rules.proxy.actions.webdriver;

import org.apache.http.Header;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.proxy.actions.CookieAction;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

import static java.util.stream.Collectors.joining;
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

        rule.getProxyServer().addRequestFilter((request, contents, messageInfo) -> {

            String cookieHeader = request.headers().get("Cookie");
            String newCookieHeader = overrideCookieInRequest(cookieHeader);

            if (newCookieHeader != null && !newCookieHeader.isEmpty()) {
                request.headers().set("Cookie", newCookieHeader);
            }

            return null;
        });


        rule.getProxyServer().addResponseFilter((response, contents, messageInfo) -> {
            List<String> setCookie = response.headers().getAll("Set-Cookie")
                    .stream()
                    .filter(e -> !cookiesToAdd.keySet().contains(e.split("=")[0]))
                    .filter(e -> !cookiesToDelete.contains(e.split("=")[0]))
                    .collect(toList());

            cookiesToAdd.values().forEach(e -> setCookie.add(e.name + "=" + e.value));

//            List<String> toOverride = setCookie.stream()
//                    .filter(e -> cookiesToOverride.keySet().contains(e.split("=")[0]))
//                    .collect(toList());

            response.headers().remove("Set-Cookie");

            for (String set : setCookie) {
                response.headers().add("Set-Cookie", set);
            }
        });
    }


    private String overrideCookieInRequest(String header) {
        if (header == null || header.isEmpty()) {
            return cookiesToAdd.values().stream()
                    .map(e -> e.name + "=" + e.value)
                    .collect(joining("; "));
        } else {
            Map<String, String> parsed = new HashMap<>();
            Stream.of(header.split(";"))
                    .map(e -> e.split("="))
                    .forEach(e -> parsed.put(e[0], e[1]));

            cookiesToAdd.values().forEach(e -> parsed.put(e.name, e.value));
            cookiesToOverride.values().forEach(e -> {
                if (parsed.containsKey(e.name)) {
                    parsed.put(e.name, e.value);
                }
            });
            cookiesToDelete.forEach(parsed::remove);
            return parsed.entrySet().stream()
                    .map(e -> e.getKey() + "=" + e.getValue())
                    .collect(joining("; "));
        }
    }

    private boolean deleteSetCookiesHeader(Header header) {
        return !(header.getName().equals(SET_COOKIE_HEADER) &&
                cookiesToDelete.contains(header.getElements()[0].getName()));
    }
}
