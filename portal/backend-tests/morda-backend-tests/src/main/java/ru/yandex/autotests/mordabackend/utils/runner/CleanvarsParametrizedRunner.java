package ru.yandex.autotests.mordabackend.utils.runner;

import org.junit.Test;
import org.junit.runner.Description;
import org.junit.runner.Runner;
import org.junit.runner.notification.Failure;
import org.junit.runner.notification.RunNotifier;
import org.junit.runners.BlockJUnit4ClassRunner;
import org.junit.runners.model.FrameworkMethod;
import org.junit.runners.model.InitializationError;
import org.junit.runners.model.Statement;
import org.junit.runners.model.TestClass;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.utils.parameters.Parameter;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import static java.util.concurrent.Executors.callable;

/**
 * User: ivannik
 * Date: 08.08.2014
 */
public class CleanvarsParametrizedRunner extends Runner {

    private static final Properties CONFIG = new Properties();

    private static AtomicInteger totalTestCount = new AtomicInteger(0);

    private ExecutorService executorService;
    private Class testClass;
    private ParametersUtils parametersProvider;
    private String namePattern;

    public CleanvarsParametrizedRunner(Class testClass) throws IllegalAccessException {
        this.executorService = Executors.newFixedThreadPool(CONFIG.getThreadCnt());
        this.testClass = testClass;
        for (Field f : testClass.getFields()) {
            if (f.getAnnotation(Parameters.class) != null) {
                this.parametersProvider = (ParametersUtils) f.get(null);
                this.namePattern = f.getAnnotation(Parameters.class).value();
            }
        }
    }

    @Override
    public Description getDescription() {
        return  Description.createTestDescription(testClass, testClass.getName());
    }

    @Override
    public void run(final RunNotifier notifier) {
        List<Callable<Object>> paramTasks = new ArrayList<>();
        for (final Parameter parameter : parametersProvider.getParameters()) {
            paramTasks.add(callable(new Runnable() {
                @Override
                public void run() {
                    try {
                        List<Object[]> paramsList =
                                parameter.build(parametersProvider.getCleanvarsBlocks(),
                                        parametersProvider.getCounters());
                        int currentIndex = totalTestCount.incrementAndGet();
                        for (Object[] params : paramsList) {
                            new TestClassRunnerForParameters(testClass, params,
                                    nameFor(namePattern, currentIndex, params)).run(notifier);
                        }
                    } catch (Exception e) {
                        Thread t = Thread.currentThread();
                        List<Object[]> paramsList = parameter.buildOnlyInitial();
                        int currentIndex = totalTestCount.incrementAndGet();
                        fireTestFailureEvents(testClass, namePattern, currentIndex, paramsList, notifier, e);
                        t.getUncaughtExceptionHandler().uncaughtException(t, e);
                        throw new RuntimeException(e);
                    } finally {
                        parameter.releaseUser();
                    }
                }
            }));
        }
        try {
            executorService.invokeAll(paramTasks);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    private void fireTestFailureEvents(Class testClass, String namePattern, int currentIndex,
                                       List<Object[]> paramsList, RunNotifier notifier, Exception e) {
        for (Object[] params : paramsList) {
            for (FrameworkMethod test : new TestClass(testClass).getAnnotatedMethods(Test.class)){
                Failure f = new Failure(Description.createTestDescription(testClass,
                        failNameFor(test, namePattern, currentIndex, params)), e);
                notifier.fireTestStarted(f.getDescription());
                notifier.fireTestFailure(f);
            }
        }
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.FIELD)
    public static @interface Parameters {
        String value() default "{index}";
    }

    private String nameFor(String namePattern, int index, Object[] parameters) {
        String finalPattern = namePattern.replaceAll("\\{index\\}",
                Integer.toString(index));
        String name = MessageFormat.format(finalPattern, parameters);
        return "[" + name + "]";
    }

    private String failNameFor(FrameworkMethod test, String namePattern, int index, Object[] parameters) {
        String finalPattern = namePattern.replaceAll("\\{index\\}",
                Integer.toString(index));
        List<Object> p = new ArrayList<>(Arrays.asList(null, null, null));
        p.addAll(Arrays.asList(parameters));
        String name = MessageFormat.format(finalPattern, p.toArray());
        return test.getName() + "[" + name + "]";
    }

    private class TestClassRunnerForParameters extends BlockJUnit4ClassRunner {
        private final Object[] fParameters;

        private final String fName;

        TestClassRunnerForParameters(Class<?> type, Object[] parameters,
                                     String name) throws InitializationError {
            super(type);
            fParameters = parameters;
            fName = name;
        }

        @Override
        public Object createTest() throws Exception {
            return createTestUsingConstructorInjection();
        }

        private Object createTestUsingConstructorInjection() throws Exception {
            return getTestClass().getOnlyConstructor().newInstance(fParameters);
        }

        @Override
        protected String getName() {
            return fName;
        }

        @Override
        protected String testName(FrameworkMethod method) {
            return method.getName() + getName();
        }

        @Override
        protected void validateConstructor(List<Throwable> errors) {
            validateOnlyOneConstructor(errors);
        }

        @Override
        protected Statement classBlock(RunNotifier notifier) {
            return childrenInvoker(notifier);
        }

        @Override
        protected Annotation[] getRunnerAnnotations() {
            return new Annotation[0];
        }
    }
}
