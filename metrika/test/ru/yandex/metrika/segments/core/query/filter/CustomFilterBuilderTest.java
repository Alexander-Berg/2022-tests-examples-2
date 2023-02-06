package ru.yandex.metrika.segments.core.query.filter;

import org.junit.BeforeClass;
import org.junit.Ignore;

import ru.yandex.metrika.segments.ApiUtilsTests;
import ru.yandex.metrika.segments.core.ApiUtils;

/**
 * Created by orantius on 10/17/15.
 */
@Ignore
public class CustomFilterBuilderTest {

    private static ApiUtils apiUtils;

    @BeforeClass
    public static void setUp() throws Exception {
        ApiUtilsTests.setUp();
        apiUtils = ApiUtilsTests.apiUtils;
    }
}
