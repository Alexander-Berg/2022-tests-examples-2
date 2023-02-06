package ru.yandex.autotests.morda.rules.allure;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.FileAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;
import org.apache.log4j.spi.Filter;
import org.apache.log4j.spi.LoggingEvent;
import org.junit.runner.Description;
import org.junit.runner.notification.Failure;
import org.junit.runner.notification.RunListener;
import ru.yandex.qatools.allure.Allure;
import ru.yandex.qatools.allure.events.MakeAttachmentEvent;

import java.io.File;
import java.io.IOException;

import static java.lang.System.currentTimeMillis;
import static org.apache.commons.lang.RandomStringUtils.random;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13/05/16
 */
public class AllureLoggingListener extends RunListener {
    private static final Logger LOGGER = Logger.getLogger(AllureLoggingListener.class);
    private File logFile;
    private String thread;

    public AllureLoggingListener() {
        try {
            logFile = File.createTempFile(currentTimeMillis() + "_" + random(10, true, false), ".log");
            logFile.deleteOnExit();
        } catch (IOException e) {
            throw new RuntimeException("Failed to create logging file ", e);
        }
        this.thread = Thread.currentThread().getName();
        LOGGER.info("Logging file: " + logFile.getAbsolutePath() + " for thread " + this.thread);
    }

    @Override
    public void testStarted(Description description) throws Exception {
        FileAppender fileAppender = new FileAppender();
        fileAppender.setName("File appender");
        fileAppender.setFile(logFile.getAbsolutePath());
        fileAppender.setLayout(new PatternLayout("%d{ABSOLUTE}\t%4p\t%c{1}\t%m%n"));
        fileAppender.setThreshold(Level.INFO);
        fileAppender.setAppend(true);
        fileAppender.addFilter(new Filter() {
            @Override
            public int decide(LoggingEvent event) {
                if (!Thread.currentThread().getName().equals(thread)) {
                    return Filter.DENY;
                }
                return Filter.NEUTRAL;
            }
        });
        fileAppender.activateOptions();
        Logger.getRootLogger().addAppender(fileAppender);
        LOGGER.info("STARTING " + description.getMethodName());
    }

    @Override
    public void testIgnored(Description description) throws Exception {
        Logger.getRootLogger().warn("Test was ignored");
    }

    @Override
    public void testFailure(Failure failure) throws Exception {
        Logger.getRootLogger().error("Test failed", failure.getException());
    }

    @Override
    public void testAssumptionFailure(Failure failure) {
        Logger.getRootLogger().error("Test failed", failure.getException());
    }

    @Override
    public void testFinished(Description description) throws Exception {
        try {
            LOGGER.info("Attaching logs");
            Allure.LIFECYCLE.fire(new MakeAttachmentEvent(FileUtils.readFileToByteArray(logFile),
                    "testcase.log", "text/plain"));
        } catch (IOException e) {
            throw new RuntimeException("Failed to attach logs", e);
        }
    }
}
