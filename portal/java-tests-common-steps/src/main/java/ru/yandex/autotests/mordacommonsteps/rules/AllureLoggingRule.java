package ru.yandex.autotests.mordacommonsteps.rules;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.FileAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;
import org.apache.log4j.spi.Filter;
import org.apache.log4j.spi.LoggingEvent;
import org.junit.AssumptionViolatedException;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import ru.yandex.qatools.allure.annotations.Attachment;

import java.io.File;
import java.io.IOException;

import static java.lang.System.currentTimeMillis;
import static org.apache.commons.lang.RandomStringUtils.random;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13/05/16
 */
public class AllureLoggingRule extends TestWatcher {
    private static final Logger LOGGER = Logger.getLogger(AllureLoggingRule.class);
    private File logFile;
    private String thread;

    public AllureLoggingRule() {
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
    protected void skipped(AssumptionViolatedException e, Description description) {
        Logger.getRootLogger().warn("Test was skipped", e);
    }

    @Override
    protected void failed(Throwable e, Description description) {
        Logger.getRootLogger().error("Error during test execution", e);
        attachLogs();
    }

    @Override
    protected void succeeded(Description description) {
        attachLogs();
    }

    @Override
    protected void starting(Description description) {
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
    }

    @Attachment(value = "testcase.log", type = "")
    public String attachLogs() {
        try {
            return FileUtils.readFileToString(logFile);
        } catch (IOException e) {
            throw new RuntimeException("Failed to attach logs", e);
        }
    }
}
