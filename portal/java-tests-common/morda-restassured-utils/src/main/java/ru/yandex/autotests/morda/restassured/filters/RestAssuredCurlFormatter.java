package ru.yandex.autotests.morda.restassured.filters;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.jayway.restassured.filter.FilterContext;
import com.jayway.restassured.specification.FilterableRequestSpecification;

import java.util.Spliterator;
import java.util.stream.Collectors;

import static com.jayway.restassured.http.Method.POST;
import static com.jayway.restassured.http.Method.PUT;
import static java.util.Spliterators.spliteratorUnknownSize;
import static java.util.stream.StreamSupport.stream;

public class RestAssuredCurlFormatter {

    public static StringBuilder format(FilterableRequestSpecification requestSpec, FilterContext ctx) {
        StringBuilder data = new StringBuilder();
        try {
            return data.append("curl -v ")
                    .append("-X ").append(requestSpec.getMethod().name()).append(" '")
                    .append(requestSpec.getURI()).append("' ")
                    .append(headersFormat(requestSpec))
                    .append(cookiesFormat(requestSpec))
                    .append(bodyFormat(requestSpec));
        } catch (Throwable t) {
            System.out.println("Can't construct curl string\n" + t.getMessage());
            return data;
        }
    }

    private static String headersFormat(FilterableRequestSpecification requestSpec) {
        if (requestSpec.getHeaders().exist()) {
            return requestSpec.getHeaders().asList().stream()
                    .map(e -> "-H '" + e.getName() + ": " + e.getValue() + "'")
                    .collect(Collectors.joining(" "));
        } else {
            return "";
        }
    }

    private static String cookiesFormat(FilterableRequestSpecification requestSpec) {
        if (requestSpec.getCookies().exist()) {
            return stream(spliteratorUnknownSize(requestSpec.getCookies().iterator(), Spliterator.ORDERED), false)
                    .map(e -> "-b '" + e.getName() + "=" + e.getValue() + "'")
                    .collect(Collectors.joining(" "));
        } else {
            return "";
        }
    }

    private static String bodyFormat(FilterableRequestSpecification requestSpec) throws JsonProcessingException {
        if (requestSpec.getBody() != null && (requestSpec.getMethod().equals(POST) || requestSpec.getMethod().equals(PUT))) {
            return new StringBuilder(" -d '")
                    .append(requestSpec.getBody().toString())
                    .append("'").toString();
        }
        return "";
    }
}