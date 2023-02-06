package ru.yandex.autotests.morda.restassured.filters;

import java.io.IOException;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jayway.restassured.filter.Filter;
import com.jayway.restassured.filter.FilterContext;
import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.FilterableRequestSpecification;
import com.jayway.restassured.specification.FilterableResponseSpecification;

import ru.yandex.qatools.allure.annotations.Attachment;

import static com.jayway.restassured.http.Method.POST;
import static com.jayway.restassured.http.Method.PUT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/04/16
 */
public class AllureRestAssuredRequestFilter implements Filter {

    protected boolean silent;

    public AllureRestAssuredRequestFilter() {
        this(false);
    }

    public AllureRestAssuredRequestFilter(boolean silent) {
        this.silent = silent;
    }

    @Override
    public Response filter(
            FilterableRequestSpecification requestSpec,
            FilterableResponseSpecification responseSpec,
            FilterContext ctx)
    {
        if (!silent) {
            StringBuilder curl = getCurlString(requestSpec, ctx);

            StringBuilder requestData = new StringBuilder(requestSpec.getMethod().name())
                    .append(" ")
                    .append(requestSpec.getURI())
                    .append("\n")
                    .append(getQueryString(requestSpec))
                    .append(getCookiesString(requestSpec))
                    .append(getHeadersString(requestSpec))
                    .append(getBodyString(requestSpec))
                    .append("\n-------------------\n\n")
                    .append(curl);

            requestData.append("\n\n======================================\n\n");

            Response response = ctx.next(requestSpec, responseSpec);

            requestData.append(response.getStatusLine())
                    .append("\n")
                    .append(getHeadersString(response))
                    .append(getBodyString(response));

            attachRequestData(requestData.toString());
            return response;
        } else {
            return ctx.next(requestSpec, responseSpec);
        }
    }

    private StringBuilder getQueryString(FilterableRequestSpecification requestSpec) {
        StringBuilder data = new StringBuilder();
        if (requestSpec.getQueryParams().size() > 0) {
            data.append("\nQuery:\n");

            requestSpec.getQueryParams().entrySet().stream().forEach(c ->
                    data.append("    ")
                            .append(c.getKey())
                            .append("=")
                            .append(String.valueOf(c.getValue()))
                            .append("\n")

            );
        }
        return data;
    }

    private StringBuilder getCookiesString(FilterableRequestSpecification requestSpec) {
        StringBuilder data = new StringBuilder();
        if (requestSpec.getCookies().size() > 0) {
            data.append("\nCookies:\n");

            requestSpec.getCookies().forEach(c ->
                    data.append("    ")
                            .append(c.getName())
                            .append("=")
                            .append(c.getValue())
                            .append("\n")
            );

        }
        return data;
    }

    private StringBuilder getHeadersString(FilterableRequestSpecification requestSpec) {
        StringBuilder data = new StringBuilder();

        if (requestSpec.getHeaders().size() > 0) {
            data.append("\nHeaders:\n");

            requestSpec.getHeaders().forEach(c ->
                    data.append("    ")
                            .append(c.getName())
                            .append(": ")
                            .append(c.getValue())
                            .append("\n")
            );
        }

        return data;
    }

    private StringBuilder getBodyString(FilterableRequestSpecification requestSpec) {
        StringBuilder data = new StringBuilder();

        if (requestSpec.getBody() != null &&
                (requestSpec.getMethod().equals(POST) || requestSpec.getMethod().equals(PUT)))
        {
            String responseBody = requestSpec.getBody();
            if (responseBody != null) {
                data.append("\nBody:\n");
                try {
                    ObjectMapper objectMapper = new ObjectMapper();
                    JsonNode json = objectMapper.readValue(requestSpec.getBody().toString(), JsonNode.class);
                    data.append(objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(json));
                } catch (IOException e) {
                    data.append(responseBody);
                }
                data.append("\n");
            }
        }

        return data;
    }

    private StringBuilder getCurlString(FilterableRequestSpecification requestSpec, FilterContext ctx) {
        return RestAssuredCurlFormatter.format(requestSpec, ctx);
    }

    @Attachment(value = "request.info")
    private String attachRequestData(String data) {
        return data;
    }

    private StringBuilder getHeadersString(Response response) {
        StringBuilder data = new StringBuilder();
        if (response.getHeaders().size() > 0) {
            data.append("\nHeaders:\n");

            response.getHeaders().forEach(c ->
                    data.append("    ")
                            .append(c.getName())
                            .append(": ")
                            .append(c.getValue())
                            .append("\n")
            );
        }
        return data;
    }


    private StringBuilder getBodyString(Response response) {
        StringBuilder data = new StringBuilder();
        try {
            JsonNode responseBody = response.body().as(JsonNode.class);
            if (!responseBody.isNull()) {
                data.append("\nBody:\n")
                        .append(new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(responseBody))
                        .append("\n");
            }
        } catch (Throwable ignore) {
        }
        return data;
    }
}
