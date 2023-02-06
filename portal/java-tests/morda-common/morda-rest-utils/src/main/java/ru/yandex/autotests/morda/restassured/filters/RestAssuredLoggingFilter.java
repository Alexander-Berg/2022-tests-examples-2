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
    private boolean silent;

    public RestAssuredLoggingFilter() {
        this(false);
    }

    public RestAssuredLoggingFilter(boolean silent) {
        this.silent = silent;
    }

    @Override
    public Response filter(FilterableRequestSpecification requestSpec,
                           FilterableResponseSpecification responseSpec,
                           FilterContext ctx) {
            try {
                Response response = ctx.next(requestSpec, responseSpec);

//                if (!silent) {
                    String requestInfo = new StringBuilder(RestAssuredCurlFormatter.format(requestSpec, ctx))
                            .append(" >> ")
                            .append(response.getStatusLine())
                            .toString();
                    LOGGER.info(requestInfo);
//                }

                return response;
            } catch (Throwable e) {
                String requestInfo = new StringBuilder(RestAssuredCurlFormatter.format(requestSpec, ctx))
                        .toString();

                LOGGER.error(requestInfo);
                LOGGER.error(e.getMessage(), e);
                throw e;
            }
    }
}
