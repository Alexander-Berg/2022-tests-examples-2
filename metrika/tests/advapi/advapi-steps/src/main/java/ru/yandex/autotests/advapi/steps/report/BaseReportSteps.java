package ru.yandex.autotests.advapi.steps.report;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.ISemaphore;
import org.apache.http.HttpEntity;
import org.apache.http.HttpEntityEnclosingRequest;
import org.apache.http.NameValuePair;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.entity.ContentType;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.autotests.advapi.beans.ProfileOnlySchema;
import ru.yandex.autotests.advapi.core.*;
import ru.yandex.autotests.advapi.exceptions.MetrikaApiException;
import ru.yandex.autotests.advapi.hazelcast.HazelcastFactory;
import ru.yandex.autotests.advapi.properties.AdvApiProperties;
import ru.yandex.autotests.advapi.properties.HttpClientProperties;
import ru.yandex.autotests.advapi.threading.CustomThreadFactory;
import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclient.lite.core.exceptions.BackEndClientException;
import ru.yandex.autotests.httpclient.lite.core.steps.BackEndBaseSteps;
import ru.yandex.autotests.irt.testutils.allure.AllureUtils;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.SocketTimeoutException;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.*;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import static com.google.common.base.Throwables.propagate;
import static ru.yandex.autotests.advapi.Utils.isOnAero;
import static ru.yandex.autotests.advapi.core.AdvApiJson.GSON_RESPONSE;
import static ru.yandex.autotests.httpclient.lite.utils.HttpUtils.getMethodParams;
import static ru.yandex.autotests.httpclient.lite.utils.HttpUtils.getURI;
import static ru.yandex.autotests.metrika.commons.text.UnicodeEscape.escapeUnicode;

/**
 * Created by konkov on 26.09.2014.
 */
public abstract class BaseReportSteps extends BackEndBaseSteps {

    private static final Logger log = LogManager.getLogger(BaseReportSteps.class);

    private final ExecutorService executor;
    private final Optional<HazelcastInstance> hazelcastInstance;

    /**
     * общие для каждого запроса параметры:
     * oauth_token
     * pretty
     * internal_token
     * request_source
     * и т.п.
     */
    private IFormParameters commonParameters = FreeFormParameters.EMPTY;
    /**
     * общие для каждого запроса заголовки http запроса: токен
     */
    private IFormParameters commonHeaders = FreeFormParameters.EMPTY;

    public BaseReportSteps() {
        //daemon thread для того, что бы он не препятствовал завершению JVM.
        executor = Executors.newSingleThreadExecutor(new CustomThreadFactory("http-requests", true));

        if (isOnAero()) {
            hazelcastInstance = Optional.of(HazelcastFactory.getInstance());
        } else {
            hazelcastInstance = Optional.empty();
        }
    }

    protected <TResult> TResult executeWithSemaphore(Supplier<TResult> method) {

        if (hazelcastInstance.isPresent()) {

            String semaphoreName = String.format("%s:%s", AdvApiProperties.getInstance().getApiSemaphoreNamePrefix(),
                    AdvApiProperties.getInstance().getApiSemaphorePermits());
            int permits = AdvApiProperties.getInstance().getApiSemaphorePermits();

            log.debug(String.format("Semaphore name: '%s', permits: %s", semaphoreName, permits));

            ISemaphore semaphore = null;
            try {
                log.debug("Create semaphore object");
                semaphore = hazelcastInstance.get().getSemaphore(semaphoreName);
                log.debug("Initialize semaphore");
                semaphore.init(permits);
                log.debug(String.format("acquiring semaphore, available permits: %s", semaphore.availablePermits()));
                semaphore.acquire();
                log.debug(String.format("semaphore acquired, available permits: %s", semaphore.availablePermits()));

                return method.get();

            } catch (InterruptedException e) {
                throw propagate(e);
            } finally {
                if (semaphore != null) {
                    log.debug("Releasing semaphore");
                    semaphore.release();
                    log.debug("Semaphore released");
                }
            }
        } else {
            log.debug("Local launch - no semaphore");

            return method.get();
        }
    }

    protected MetrikaRequestBuilder getRequestBuilder(String path) {
        config.getClientConfig().path(path);
        return ((MetrikaRequestBuilder) config.getRequestBuilder()).withCommonParameters(commonParameters);
    }

    /**
     * Делает тоже самое, что и {@link ru.yandex.autotests.advapi.steps.UserSteps#createStepsWithCommonSettings(Class)}, потому что
     * степы умеют создавать степы и им нужно делится настройками, переданными от {@link ru.yandex.autotests.advapi.steps.UserSteps}
     */
    protected <T extends BaseReportSteps> T createStepsWithCommonSettings(Class<T> stepsClass) {
        return BackEndBaseSteps.getInstance(stepsClass, config)
                .withCommonParameters(commonParameters)
                .withCommonHeaders(commonHeaders);
    }

    public MetrikaJsonResponse executeAsJson(HttpUriRequest method) {
        return execute(MetrikaJsonResponse.class, method);
    }

    /**
     * По-хорошему заголовки должны устанавливаться в {@link MetrikaRequestBuilder}, но он наследуется от
     * {@link ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder}, который ничего не знает о заголовках
     * запроса, а все его методы final. Можно было бы его научить/поменять, но:
     * 1) это выглядит искуссвенно
     * 2) кажется, что правильнее было бы переписать код на подобии более свежих тестов аудиторий/mobmetd,
     * где метод withUser является статическим, фабрикой создающей UsersSteps. Тогда для начала можно было бы
     * токен прописать в default headers http клиента. А потом при желании унифицировать и остальное использование
     * {@link ru.yandex.autotests.advapi.steps.UserSteps}.
     * Также заголовки определяются в {@link MetrikaRequestBuilder}, но там это сделано для двух http методов (post, put).
     * При этом надо точно вызвать нужный метод, потому что другие методы put/post без заголовков никуда не деваются
     * и их можно вызвать. Обычно этого не случается из-за перегрузки по аргументам. Но с get параметрами так
     * не получится.
     */
    private <T> T execute(Class<T> responseClass, HttpUriRequest method) {

        commonHeaders.getParameters().forEach(headerData -> {
            if (method.containsHeader(headerData.getName())) {
                throw new IllegalStateException("Duplicate http header: " + headerData.getName());
            }
            method.addHeader(headerData.getName(), headerData.getValue());
        });

        logRequest(method);
        try {
            return responseClass.getConstructor(BackEndResponse.class).newInstance(executeCoreWithRetry(method));
        } catch (InterruptedException e) {
            throw new MetrikaApiException("Выполнение запроса прервано", e);
        } catch (ExecutionException e) {
            if (e.getCause() != null && e.getCause() instanceof SocketTimeoutException) {
                throw new BackEndClientException(
                        String.format("Сервис не ответил за %s секунд",
                                HttpClientProperties.getInstance().getSocketTimeout() / 1000),
                        e.getCause());
            } else if (e.getCause() != null && e.getCause() instanceof IOException) {
                throw new BackEndClientException(
                        String.format("Ошибка во время исполнения Http-запроса. %s: %s",
                                e.getClass().getSimpleName(), e.getMessage()),
                        e);
            } else {
                throw new MetrikaApiException("Ошибка при выполнении запроса", e);
            }
        } catch (TimeoutException e) {
            throw new BackEndClientException(
                    String.format("Запрос к сервису не был завершен за %s секунд",
                            HttpClientProperties.getInstance().getExecutionTimeout() / 1000),
                    e);
        } catch (NoSuchMethodException |
                InvocationTargetException |
                InstantiationException |
                IllegalAccessException e) {
            throw new MetrikaApiException(
                    String.format("Ошибка при разборе ответа. Класс %s не является классом ответа Метрики.",
                            responseClass.getSimpleName()),
                    e);
        } catch (Exception e) {
            throw propagate(e);
        }
    }

    private BackEndResponse executeCoreWithRetry(HttpUriRequest method) throws Exception {
        log.trace("Start - Execute core with retry");
        final int maxRetry = 3;

        Future<BackEndResponse> futureResult = null;
        BackEndResponse backEndResponse = null;
        Exception lastException = null;

        for (int retryIteration = 1; retryIteration <= maxRetry; retryIteration++) {
            log.trace(String.format("Попытка %s", retryIteration));
            lastException = null;
            try {
                futureResult = executor.submit(() -> executeCore(method));
                backEndResponse = futureResult.get(HttpClientProperties.getInstance()
                        .getExecutionTimeout(), TimeUnit.MILLISECONDS);
            } catch (TimeoutException | ExecutionException e) {
                log.warn("Таймаут при выполнении запроса или иная ошибка", e);
                lastException = e;
            } finally {
                if (futureResult != null) {
                    futureResult.cancel(true);
                }
            }

            if (lastException != null) {
                if (!Retry.isRetryable(lastException)) {
                    break;
                }
            } else {
                if (!shouldRetry(backEndResponse)) {
                    break;
                }
            }

            //ждем, если была не последняя итерация
            if (retryIteration != maxRetry) {
                TimeUnit.SECONDS.sleep(1 + 2 * retryIteration * retryIteration);
            }
        }
        log.trace("Finish - Execute core with retry");
        if (lastException != null) {
            throw lastException;
        }

        return backEndResponse;
    }

    private BackEndResponse executeCore(HttpUriRequest method) throws IOException {
        BackEndResponse result;
        log.trace("Enter execute core");
        try {
            result = (BackEndResponse) config.getHttpClient().execute(method, config.getHandler());
        } catch (IOException e) {
            log.warn("Исключение во время выполнения http-запроса. Пробрасываем.", e);
            throw e;
        } finally {
            log.trace("Leave execute core");
        }
        return result;
    }

    private boolean shouldRetry(BackEndResponse result) {
        try {
            log.trace("Should retry.");
            log.trace(result.getStatusLine().toString());

            if (result.getStatusLine().getStatusCode() < 400) {
                return false;
            }

            if (result.getResponseContent().getType().getMimeType().equals(ContentType.APPLICATION_JSON.getMimeType())) {
                String responseContent = result.getResponseContent().asString();
                log.trace("Analyze json response:");
                log.trace(responseContent);

                ProfileOnlySchema profileOnlySchema = GSON_RESPONSE
                        .fromJson(responseContent, ProfileOnlySchema.class);

                return Retry.isRetryable(profileOnlySchema);
            }

            return false;
        } catch (Throwable e) {
            log.warn("Исключение во время проверки на то, что бы сделать повтор запроса.", e);
            return false;
        }
    }

    protected MetrikaJsonResponse getResponse(String path, IFormParameters... parameters) {
        return execute(MetrikaJsonResponse.class, getRequestBuilder(path).get(parameters));
    }

    private void logRequest(HttpUriRequest request) {
        final String address = getURI(request);
        final List<NameValuePair> methodParams = getMethodParams(request);

        final StringBuilder stringBuilder = new StringBuilder()
                .append(request.toString()).append(System.lineSeparator()).append(System.lineSeparator())
                .append(methodParams.stream().map(nvp -> escapeUnicode(nvp.toString())).collect(Collectors.joining(System.lineSeparator()))).append(System.lineSeparator());

        tryLogHttpEntity(request, stringBuilder);

        final String title = "Request: " + request.getMethod() + " " + address;

        final String message = stringBuilder.toString();

        AllureUtils.addTextAttachment(title, message);

        log.info(title);
        log.info(message);
    }

    private static void tryLogHttpEntity(HttpUriRequest request, StringBuilder stringBuilder) {
        if (request instanceof HttpEntityEnclosingRequest) {
            try {
                HttpEntity entity = ((HttpEntityEnclosingRequest) request).getEntity();

                if (entity != null) {
                    stringBuilder.append(System.lineSeparator());

                    // MultipartFormEntity access is package-local, so ugly checking with reflection
                    // EntityUtils.toString fails on MultipartFormEntity, so handle it specially
                    if (entity.getClass().getName().equals("org.apache.http.entity.mime.MultipartFormEntity")) {
                        if (entity.isRepeatable()) {
                            ByteArrayOutputStream out = new ByteArrayOutputStream();
                            entity.writeTo(out);

                            stringBuilder.append(out.toString());
                        } else {
                            stringBuilder.append("Non-repeatable http entity");
                        }
                    } else {
                        stringBuilder.append(EntityUtils.toString(entity));
                    }
                }
            } catch (IOException e) {
                stringBuilder.append(e.toString());
            }
        }
    }

    @SuppressWarnings("unchecked")
    public <T extends BaseReportSteps> T withCommonParameters(IFormParameters commonParameters) {
        this.commonParameters = commonParameters;
        return (T) this;
    }

    @SuppressWarnings("unchecked")
    public <T extends BaseReportSteps> T withCommonHeaders(IFormParameters commonHeaders) {
        this.commonHeaders = commonHeaders;
        return (T) this;
    }
}
