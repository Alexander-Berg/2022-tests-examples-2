package ru.yandex.autotests.mordabackend.cookie;

import ru.yandex.autotests.mordabackend.client.ClientUtils;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import javax.ws.rs.client.Client;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class YpCookieUtils {

    public static void addToYpCookie(Client client, Region region, String subCookie) {
        addToYpInDomain(client, ".yandex" + region.getDomain(), subCookie);
        if (!region.getDomain().equals(Domain.RU)) {
            addToYpInDomain(client, ".yandex.ru", subCookie);
        }
    }

    private static void addToYpInDomain(Client client, String domain, String subCookie) {
        String domainValue = ClientUtils.getCookieValue(client, "yp", domain);
        int a = subCookie.indexOf('.');
        int b = subCookie.indexOf('.', a + 1);
        String subCookieName = subCookie.substring(a + 1, b);
        if (domainValue == null || domainValue.equals("")) {
            domainValue = subCookie;
        } else if (domainValue.contains("." + subCookieName + ".")) {
            domainValue = domainValue.replaceAll("(?<=^|#)[^#]+" + subCookieName + "[^#]+(?=$|#)", subCookie);
        } else {
            domainValue = domainValue + "#" + subCookie;
        }
        ClientUtils.addCookie(client, "yp", domainValue, domain);
    }
}
