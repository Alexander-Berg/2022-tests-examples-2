package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import net.sf.cglib.proxy.InvocationHandler;
import ru.yandex.autotests.metrika.appmetrica.steps.AppMetricaBaseSteps;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.List;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.SemaphoresFactory.checkSemaphoreId;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.SemaphoresFactory.getAllSemaphoreIds;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.SemaphoresFactory.semaphoresInstance;

/**
 * Аспект, который запускает тест под семафором если это нужно.
 */
public final class ParallelismControl implements InvocationHandler {

    private static final Class<ParallelExecution> ANNOTATION = ParallelExecution.class;

    /**
     * Если в треде выставлен конкретный semaphore id, то аннотация RESTRICT будет ждать освобождения только его
     * и захватит тоже только его. Если не выставлен, то аннотация потребует все семафоры сразу.
     */
    private static final ThreadLocal<Integer> particularSemaphoreId = new ThreadLocal<>();

    /**
     * Оригинальный инстанс степов, на который мы перенаправляем запрос
     */
    private AppMetricaBaseSteps steps;

    public ParallelismControl(AppMetricaBaseSteps steps) {
        this.steps = steps;
    }

    @Override
    public Object invoke(Object obj, Method method, Object[] args) throws Throwable {
        final Permission parallelPermission = extractOrFail(method);

        switch (parallelPermission) {
            case ALLOW:
                return justRun(method, args);
            case RESTRICT:
                List<Integer> semaphoreIds = getSemaphoreIds();
                return runWithSemaphores(semaphoreIds, method, args);
            default:
                throw new IllegalStateException("Unknown permission value: " + parallelPermission);
        }
    }

    private Object runWithSemaphores(List<Integer> semaphoreIds, Method method, Object[] args) throws Throwable {
        final Semaphores semaphores = semaphoresInstance();
        semaphores.acquire(semaphoreIds);
        try {
            return justRun(method, args);
        } finally {
            semaphores.release(semaphoreIds);
        }
    }

    private Object justRun(Method method, Object[] args) throws Throwable {
        try {
            return method.invoke(steps, args);
        } catch (InvocationTargetException e) {
            // Прокидываем исключения, чтобы отчёт Allure не группировал по InvocationTargetException
            // и использовал читабельные сообщения из assert.
            throw e.getCause() != null ? e.getCause() : e;
        }
    }

    /**
     * Достать аннотацию над методом степов или упасть с ошибкой если ее нет
     */
    private Permission extractOrFail(Method method) {
        if (!method.isAnnotationPresent(ANNOTATION)) {
            throw new IllegalStateException("Every step method should explicitly decide about parallelism permission. " +
                    "Please annotate method " + method.getName() + " with annotation " + ANNOTATION.getSimpleName());
        }

        return method.getAnnotation(ANNOTATION).value();
    }

    public static void setParticularSemaphoreId(Integer semaphoreId) {
        checkSemaphoreId(semaphoreId);
        particularSemaphoreId.set(semaphoreId);
    }

    public static void resetParticularSemaphoreId() {
        particularSemaphoreId.remove();
    }

    /**
     * Семафоры, необходимые для выполнения степа.
     * Либо {@link #particularSemaphoreId}, если задан. Либо все сразу.
     */
    private static List<Integer> getSemaphoreIds() {
        Integer semaphoreId = particularSemaphoreId.get();
        return semaphoreId == null ? getAllSemaphoreIds() : singletonList(semaphoreId);
    }

}
