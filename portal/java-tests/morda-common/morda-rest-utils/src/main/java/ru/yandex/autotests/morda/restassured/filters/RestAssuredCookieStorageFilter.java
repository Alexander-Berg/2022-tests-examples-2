package ru.yandex.autotests.morda.restassured.filters;

import com.jayway.restassured.filter.Filter;
import com.jayway.restassured.filter.FilterContext;
import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.FilterableRequestSpecification;
import com.jayway.restassured.specification.FilterableResponseSpecification;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/04/16
 */
public class RestAssuredCookieStorageFilter implements Filter {

    private Map<String, String> cookies = new HashMap<>();

    @Override
    public Response filter(FilterableRequestSpecification requestSpec,
                           FilterableResponseSpecification responseSpec,
                           FilterContext ctx) {

        requestSpec.getCookies().forEach(c -> cookies.put(c.getName(), c.getValue()));

        clearCookies();

        cookies.entrySet().stream()
                .filter(c -> !requestSpec.getCookies().hasCookieWithName(c.getKey()))
                .forEach(c -> requestSpec.cookie(c.getKey(), c.getValue()));

        Response response = ctx.next(requestSpec, responseSpec);
        cookies.putAll(response.getCookies());

        clearCookies();

        return response;
    }

    private void clearCookies() {
        Iterator<Map.Entry<String, String>> iterator = cookies.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, String> cookie = iterator.next();
            if (cookie.getValue() == null || cookie.getValue().isEmpty()) {
                iterator.remove();
            }
        }
    }

    public Map<String, String> getCookies() {
        return cookies;
    }
}
