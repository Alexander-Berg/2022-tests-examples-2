package ru.yandex.autotests.mordabackend.utils.parameters;

import ch.lambdaj.function.convert.Converter;
import org.apache.commons.lang3.SerializationUtils;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.users.UserType;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static ch.lambdaj.Lambda.convert;
import static ch.lambdaj.Lambda.flatten;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class ParametersUtils {
    private static final Properties CONFIG = new Properties();
    private List<Parameter> parameters;
    private List<CleanvarsBlock> cleanvarsBlocks;
    private ExecutorService executorService;
    private boolean counters = false;

    private ParametersUtils(BaseProperties.MordaEnv mordaEnv, List<Region> regions) {
        this.executorService = Executors.newSingleThreadExecutor();
        this.parameters = new ArrayList<>();
        for (Region region : regions) {
            parameters.add(new Parameter(CONFIG.getProtocol(), mordaEnv, region, CONFIG.getCookies()));
        }
    }

    private ParametersUtils(BaseProperties.MordaEnv mordaEnv, List<Domain> domains, boolean notUsed) {
        this.executorService = Executors.newSingleThreadExecutor();
        this.parameters = new ArrayList<>();
        for (Domain domain : domains) {
            parameters.add(new Parameter(CONFIG.getProtocol(), mordaEnv, domain, CONFIG.getCookies()));
        }
    }

    public static ParametersUtils parameters(Region... regions) {
        return new ParametersUtils(CONFIG.getMordaEnv(), Arrays.asList(regions));
    }

    public static ParametersUtils parameters(Domain... domains) {
        return parameters(CONFIG.getMordaEnv(), domains);
    }

    public static ParametersUtils parameters(BaseProperties.MordaEnv mordaEnv, Domain... domains) {
        return new ParametersUtils(mordaEnv, Arrays.asList(domains), false);
    }

    public static ParametersUtils parameters(List<Region> regions) {
        return new ParametersUtils(CONFIG.getMordaEnv(), regions);
    }

    public ParametersUtils withLanguages(final List<Language> languages) {
        parameters = flatten(convert(parameters, new Converter<Parameter, List<Parameter>>() {
            @Override
            public List<Parameter> convert(Parameter from) {
                List<Parameter> result = new ArrayList<>();
                if (from.region.getDomain().equals(COM_TR)) {
                    result.add(from.withLanguage(TR));
                } else {
                    for (Language language : languages) {
                        Parameter cloned = SerializationUtils.clone(from);
                        result.add(cloned.withLanguage(language));
                    }
                }
                return result;
            }
        }));
        return this;
    }

    public ParametersUtils withLanguages(final Language... languages) {
        return withLanguages(Arrays.asList(languages));
    }

    public ParametersUtils withUserAgents(final List<UserAgent> userAgents) {
        parameters = flatten(convert(parameters, new Converter<Parameter, List<Parameter>>() {
            @Override
            public List<Parameter> convert(Parameter from) {
                List<Parameter> result = new ArrayList<>();
                for (UserAgent userAgent : userAgents) {
                    Parameter cloned = SerializationUtils.clone(from);
                    result.add(cloned.withUserAgent(userAgent));
                }
                return result;
            }
        }));
        return this;
    }

    public ParametersUtils withUserAgents(final UserAgent... userAgents) {
        return withUserAgents(Arrays.asList(userAgents));
    }

    public ParametersUtils withUserTypes(final List<UserType> userTypes) {
        parameters = flatten(convert(parameters, new Converter<Parameter, List<Parameter>>() {
            @Override
            public List<Parameter> convert(Parameter from) {
                List<Parameter> result = new ArrayList<>();
                for (UserType userType : userTypes) {
                    Parameter cloned = SerializationUtils.clone(from);
                    result.add(cloned.withUserType(userType));
                }
                return result;
            }
        }));
        return this;
    }

    public ParametersUtils withUserTypes(final UserType ... userTypes) {
        return withUserTypes(Arrays.asList(userTypes));
    }

    public ParametersUtils withParameterProvider(final ParameterProvider parameterProvider) {
        parameters = convert(parameters, new Converter<Parameter, Parameter>() {
            @Override
            public Parameter convert(Parameter from) {
                return from.withProvider(parameterProvider);
            }
        });
        return this;
    }

    public ParametersUtils withCleanvarsBlocks(CleanvarsBlock ... cleanvarsBlocks) {
        this.cleanvarsBlocks = Arrays.asList(cleanvarsBlocks);
        return this;
    }

    public ParametersUtils withCounters() {
        this.counters = true;
        return this;
    }

    public List<Parameter> getParameters() {
        return parameters;
    }

    public List<CleanvarsBlock> getCleanvarsBlocks() {
        return cleanvarsBlocks;
    }

    public boolean getCounters() {
        return counters;
    }

    public List<Object[]> build() {
        final List<Object[]> data = new ArrayList<>();

        for (final Parameter parameter : parameters) {
            executorService.submit(new Runnable() {
                @Override
                public void run() {
                    try {
                        synchronized (data) {
                            data.addAll(parameter.build(cleanvarsBlocks, counters));
                        }
                    } catch (RuntimeException e) {
                        Thread t = Thread.currentThread();
                        t.getUncaughtExceptionHandler().uncaughtException(t, e);
                    }
                }
            });
        }

        executorService.shutdown();
        try {
            executorService.awaitTermination(10, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        return data;
    }

    public List<Object[]> buildOnlyInitial() {
        final List<Object[]> data = new ArrayList<>();

        for (final Parameter parameter : parameters) {
            executorService.submit(new Runnable() {
                @Override
                public void run() {
                    try {
                        synchronized (data) {
                            data.addAll(parameter.buildOnlyInitial());
                        }
                    } catch (RuntimeException e) {
                        Thread t = Thread.currentThread();
                        t.getUncaughtExceptionHandler().uncaughtException(t, e);
                    }
                }
            });
        }

        executorService.shutdown();
        try {
            executorService.awaitTermination(10, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        return data;
    }
}
