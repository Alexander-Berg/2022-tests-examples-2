package ru.yandex.autotests.morda.restassured.filters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jayway.restassured.filter.Filter;
import com.jayway.restassured.filter.FilterContext;
import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.FilterableRequestSpecification;
import com.jayway.restassured.specification.FilterableResponseSpecification;
import ru.yandex.qatools.allure.annotations.Attachment;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/04/16
 */
public class AllureRestAssuredResponseFilter implements Filter {
    private boolean attachInfo = false;

    public AllureRestAssuredResponseFilter() {
        this(true);
    }

    public AllureRestAssuredResponseFilter(boolean attachInfo) {
        this.attachInfo = attachInfo;
    }

    @Override
    public Response filter(FilterableRequestSpecification requestSpec,
                           FilterableResponseSpecification responseSpec,
                           FilterContext ctx) {

        Response response = ctx.next(requestSpec, responseSpec);
        if (attachInfo) {
            String responseData = new StringBuilder(response.getStatusLine())
                    .append("\n")
                    .append(getHeadersString(response))
                    .append(getBodyString(response))
                    .toString();


            attachResponseData(responseData);
        }
        return response;
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
        if (response.getContentType().contains("application/json")) {
            try {
                JsonNode responseBody = response.body().as(JsonNode.class);
                if (!responseBody.isNull()) {
                    data.append("\nBody:\n")
                            .append(new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(responseBody))
                            .append("\n");
                }
            } catch (Throwable ignore) {
            }
        }

        return data;
    }

    @Attachment(value = "response.info")
    private String attachResponseData(String data) {
        return data;
    }
}
