package ru.yandex.autotests.morda.tests.web.utils;

import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isOneOf;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;

/**
 * User: asamar
 * Date: 31.08.2015.
 */
public class UrlValidator {

    private static UrlMatcher yaRuValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host("suggest.yandex.ru")
                .path("/suggest-ya.cgi")
                .urlParams(
                        urlParam("html", "1"),
                        urlParam("hl", "1"),
                        //urlParam("lr", ""),
                        urlParam("uil", morda.getLanguage().toString())

                )
                .build();
    }


    private static UrlMatcher yandexComValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host("yandex.com")
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("html", "1"),
                        urlParam("hl", "1"),
                        //urlParam("lr", searchForm.getLr().getAttribute("value"))
                        urlParam("uil", isOneOf("en", "id"))
                )
                .build();
    }


    private static UrlMatcher firefoxValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host(anyOf(
                        equalTo("suggest.yandex.ru"),
                        equalTo("yandex.com.tr"),
                        equalTo("yandex.ua")
                        )
                )
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("html", "1"),
                        urlParam("hl", "1"),
                        urlParam("lr", morda.getRegion().getRegionId()),
                        urlParam("uil", morda.getLanguage().toString())
                )
                .build();
    }


    private static UrlMatcher comTrValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host(endsWith("yandex.com.tr"))
                .path(anyOf(
                        startsWith("/suggest"),
                        startsWith("/search")
                        )
                )
                .urlParams(
                        //urlParam("html", "1"),
                        urlParam("hl", "1"),
                        //urlParam("lr", morda.getRegion().getRegionId()),
                        urlParam("uil", "tr")
                )
                .build();
    }

    private static UrlMatcher touchValidator(Morda morda) {
        String domain = morda.getRegion().getDomain().getValue().replace(".", "");
        String srv = "morda_" + domain + "_touch";

        return urlMatcher()
                .scheme("https")
                .host(startsWith("yandex."))
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("srv", anyOf(
                                equalTo(srv),
                                equalTo(srv + "_msuggest_exp_inline"),
                                equalTo(srv + "_msuggest_exp_async")
                        )),
                        urlParam("yu", notNullValue()),
                        urlParam("lr", morda.getRegion().getRegionId()),
                        urlParam("uil", morda.getLanguage().toString())
                )
                .build();
    }

    private static UrlMatcher touchComTrWpValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host(startsWith("suggest.yandex."))
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("lr", morda.getRegion().getRegionId()),
                        urlParam("uil", morda.getLanguage().getValue())
                )
                .build();
    }

    private static UrlMatcher touchRuWpValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host(startsWith("suggest.yandex."))
                .path(startsWith("/suggest"))
                .build();
    }

    private static UrlMatcher mainValidator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host(anyOf(
                        equalTo("suggest.yandex.ru"),
                        equalTo("yandex" + morda.getRegion().getDomain())
                        )
                )
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("html", "1"),
                        urlParam("hl", "1"),
                        urlParam("lr", morda.getRegion().getRegionId()),
                        urlParam("uil", morda.getLanguage().getValue())
                )
                .build();
    }

    private static UrlMatcher com404Validator(Morda morda) {
        return urlMatcher()
                .scheme("https")
                .host("yandex.com")
                .path(startsWith("/suggest"))
                .urlParams(
                        urlParam("html", "1"),
                        urlParam("hl", "1"),
                        urlParam("uil", isOneOf("en", "id"))
                )

                .build();
    }


    public static UrlMatcher getUrlMatcher(Morda morda) {

        switch (morda.getMordaType()) {

            case D_COM:
                return yandexComValidator(morda);
            case D_COMTR:
                return comTrValidator(morda);
            case D_COMTRFOOTBALL:
                return comTrValidator(morda);
            case D_FIREFOX:
                return firefoxValidator(morda);

            case D_PAGE404:
                return com404Validator(morda);

            case D_YARU:
                return yaRuValidator(morda);
            case D_MAIN:
                return mainValidator(morda);

            case T_COMTR:
                return touchValidator(morda);
            case T_COMTRWP:
                return touchComTrWpValidator(morda);
            case T_RU:
                return touchValidator(morda);
            case T_RUWP:
                return touchRuWpValidator(morda);
            case D_COM_404:
                return com404Validator(morda);

        }
        return null;
    }
}
