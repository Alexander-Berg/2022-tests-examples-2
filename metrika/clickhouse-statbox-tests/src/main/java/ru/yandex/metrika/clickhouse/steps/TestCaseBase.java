package ru.yandex.metrika.clickhouse.steps;

import io.qameta.allure.Allure;
import io.qameta.allure.okhttp3.AllureOkHttp3;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.logging.HttpLoggingInterceptor;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.junit.jupiter.api.function.Executable;

import java.io.IOException;
import java.net.URL;
import java.util.concurrent.TimeUnit;

public abstract class TestCaseBase implements Executable {
    private static final Logger LOG = LogManager.getLogger(TestCase.class);
    private static final OkHttpClient CLIENT = new OkHttpClient.Builder()
            .readTimeout(120L, TimeUnit.SECONDS)
            .writeTimeout(5L, TimeUnit.SECONDS)
            .connectTimeout(10L, TimeUnit.SECONDS)
            .addInterceptor(new AllureOkHttp3())
            .addInterceptor(new HttpLoggingInterceptor(message -> LOG.info(message)).setLevel(HttpLoggingInterceptor.Level.BASIC))
            .build();

    private final URL test;
    private final URL ref;
    private final String query;

    public TestCaseBase(URL test, URL ref, String query) {
        this.test = test;
        this.ref = ref;
        this.query = query;
    }

    protected abstract void assertOnDifferenceDescriptor(DifferenceDescriptor differenceDescriptor);

    @Override
    public void execute() throws Throwable {

        /*
        1. Выполнить запрос на test и ref
            Приаттачить запрос и ответ для каждого.
            Если нет ответа - исключение или сообщение из объекта-ответа
        2. Проанализировать результат
            2.1 Оба должны быть успешны.
            2.2 сравнить тело ответа с помощью diffutils
            2.3 сформировать аттач с помощью freemarker
         */

        DifferenceDescriptor differenceDescriptor = new DifferenceDescriptor(
                Allure.step("Запрос на stable-полустенд", () -> executeRequest(getRequestTo(ref))),
                Allure.step("Запрос на test-полустенд", () -> executeRequest(getRequestTo(test))));

        if (differenceDescriptor.isHasDiff()) {
            Allure.addAttachment("HTML Diff", "text/html", differenceDescriptor.getHtmlDiff(), ".html");
            Allure.addAttachment("Annotated Console Diff", differenceDescriptor.getConsoleDiff());
        }

        assertOnDifferenceDescriptor(differenceDescriptor);
    }

    private ResponseDescriptor executeRequest(Request request) {
        LOG.debug(request.toString());
        ResponseDescriptor.Builder builder = ResponseDescriptor.builer();
        try {
            builder.withResponse(CLIENT.newCall(request).execute());
        } catch (IOException e) {
            builder.withException(e);
        }
        return builder.build();
    }

    private Request getRequestTo(URL host) {
        return new Request.Builder().post(RequestBody.create(null, query)).url(host).build();
    }
}
