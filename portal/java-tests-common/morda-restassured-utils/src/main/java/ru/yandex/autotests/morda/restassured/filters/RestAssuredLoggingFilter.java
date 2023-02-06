package ru.yandex.autotests.morda.restassured.filters;

import com.jayway.restassured.filter.FilterContext;
import com.jayway.restassured.filter.log.ResponseLoggingFilter;
import com.jayway.restassured.response.Response;
import com.jayway.restassured.specification.FilterableRequestSpecification;
import com.jayway.restassured.specification.FilterableResponseSpecification;
import org.apache.log4j.Logger;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/04/16
 */
public class RestAssuredLoggingFilter extends ResponseLoggingFilter {

    private static final Logger LOGGER = Logger.getLogger(RestAssuredLoggingFilter.class);

    @Override
    public Response filter(FilterableRequestSpecification requestSpec,
                           FilterableResponseSpecification responseSpec,
                           FilterContext ctx) {

        Response response = ctx.next(requestSpec, responseSpec);

        String requestData = new StringBuilder(">> ")
                .append(RestAssuredCurlFormatter.format(requestSpec, ctx))
                .toString();
        String responseData = new StringBuilder("<< ")
                .append(response.getStatusLine())
                .toString();

        LOGGER.info(requestData);
        LOGGER.info(responseData);

        return response;
    }
}
