package ru.yandex.metrika.topsites;

import ru.yandex.qe.hitman.comrade.script.model.logger.LogLevel;
import ru.yandex.qe.hitman.comrade.script.model.logger.Logger;

public class StubLogger implements Logger {

    @Override
    public void log(LogLevel logLevel, String message, Object... params) {
        int paramsStartIdx= 0;
        Throwable throwable = null;
        if (params.length > 0 && params[0] instanceof Throwable) {
            throwable = (Throwable) params[0];
            paramsStartIdx = 1;
        }

        for (int i = paramsStartIdx; i < params.length; i++) {
            message = message.replaceFirst("\\{}", String.valueOf(params[i]));
        }

        System.out.println(message);

        if (throwable != null) {
            System.out.println(throwable.getMessage());
            throwable.printStackTrace(System.out);
        }
    }

    @Override
    public void log(LogLevel logLevel, String s, Throwable throwable) {
        log(logLevel, s, (Object) throwable);
    }

    @Override
    public void trace(String s, Object... objects) {
        log(LogLevel.TRACE, s, objects);
    }

    @Override
    public void trace(String s, Throwable throwable) {
        log(LogLevel.TRACE, s, throwable);
    }

    @Override
    public void debug(String s, Object... objects) {
        log(LogLevel.DEBUG, s, objects);
    }

    @Override
    public void debug(String s, Throwable throwable) {
        log(LogLevel.DEBUG, s, throwable);
    }

    @Override
    public void info(String s, Object... objects) {
        log(LogLevel.INFO, s, objects);
    }

    @Override
    public void info(String s, Throwable throwable) {
        log(LogLevel.INFO, s, throwable);
    }

    @Override
    public void warn(String s, Object... objects) {
        log(LogLevel.WARN, s, objects);
    }

    @Override
    public void warn(String s, Throwable throwable) {
        log(LogLevel.WARN, s, throwable);
    }

    @Override
    public void error(String s, Object... objects) {
        log(LogLevel.ERROR, s, objects);
    }

    @Override
    public void error(String s, Throwable throwable) {
        log(LogLevel.ERROR, s, throwable);
    }
}
