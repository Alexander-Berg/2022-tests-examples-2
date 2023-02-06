// Copyright 2021 Yandex LLC. All rights reserved.

package com.yandex.launcher.lint.app

import com.android.tools.lint.checks.infrastructure.TestFiles.java
import com.android.tools.lint.checks.infrastructure.TestFiles.kt
import com.android.tools.lint.checks.infrastructure.TestLintTask.lint
import com.yandex.tv.common.lint.LoggerIssueDetector
import org.junit.Test

class LoggerIssuesDetectorTest {

    private val LOGGER_STUB = java("""
        package com.yandex.launcher.logger;

        import com.yandex.launcher.logger.ILogger;

        public class Logger {

            public static ILogger secure(String tag) { return null; }

            public static IErrorLogger report(String tag) { return null; }

            public static void d(String tag, String msg) { ; }
            public static void v(String tag, String msg) { ; }
            public static void i(String tag, String msg) { ; }
            public static void w(String tag, String msg) { ; }
            public static void e(String tag, String msg) { ; }
        }
        """.trimIndent())

    private val KLOGGER_STUB = java("""
        package com.yandex.launcher.logger;

        import com.yandex.launcher.logger.ILogger;

        public class KLogger {

            public static ILogger secure(String tag) { return null; }

            public static IErrorLogger report(String tag) { return null; }

        }
        """.trimIndent())

    private val ILOGGER_STUB = java("""
        package com.yandex.launcher.logger;

        public interface ILogger {

        }
        """.trimIndent())

    private val IERROR_LOGGER_STUB = java("""
        package com.yandex.launcher.logger;

        public interface IErrorLogger {

        }
        """.trimIndent())

    @Test
    fun unsafeLoggingOperationsJavaTest() {
        lint()
            .files(
                java("""
                    package foo;

                    import android.util.Log;

                    public class UnsafeJavaLogging {

                        public static final String TAG = UnsafeLogging.class.getSimpleName();

                        public static void doSomething() {
                            Log.wtf(TAG, "WTF logging with unsafe logger");
                            Log.e(TAG, "Error logging with unsafe logger");
                            Log.d(TAG, "Debug logging with unsafe logger");
                            Log.i(TAG, "Info logging with unsafe logger");
                            Log.v(TAG, "Verbose logging with unsafe logger");

                            try {

                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }

                    }
                    """.trimIndent())
            )
            .issues(LoggerIssueDetector.ISSUE_LOG, LoggerIssueDetector.ISSUE_RAW_PRINTSTACKTRACE)
            .run()
            .expect("""
                src/foo/UnsafeJavaLogging.java:10: Warning: Using android.util.Log instead of com.yandex.launcher.logger.Logger [AndroidDefLogger]
                        Log.wtf(TAG, "WTF logging with unsafe logger");
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                src/foo/UnsafeJavaLogging.java:11: Warning: Using android.util.Log instead of com.yandex.launcher.logger.Logger [AndroidDefLogger]
                        Log.e(TAG, "Error logging with unsafe logger");
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                src/foo/UnsafeJavaLogging.java:12: Warning: Using android.util.Log instead of com.yandex.launcher.logger.Logger [AndroidDefLogger]
                        Log.d(TAG, "Debug logging with unsafe logger");
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                src/foo/UnsafeJavaLogging.java:13: Warning: Using android.util.Log instead of com.yandex.launcher.logger.Logger [AndroidDefLogger]
                        Log.i(TAG, "Info logging with unsafe logger");
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                src/foo/UnsafeJavaLogging.java:14: Warning: Using android.util.Log instead of com.yandex.launcher.logger.Logger [AndroidDefLogger]
                        Log.v(TAG, "Verbose logging with unsafe logger");
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                src/foo/UnsafeJavaLogging.java:19: Warning: Using java.lang.Throwable.printStackTrace() instead of logging with com.yandex.launcher.logger.Logger [AndroidDefLogger]
                            e.printStackTrace();
                            ~~~~~~~~~~~~~~~~~~~
                0 errors, 6 warnings
                """.trimIndent())
    }

    @Test
    fun unsafeLoggingOperationsKtTest() {
        lint()
             .files(
                kt("""
                    package foo

                    import android.util.Log
                    import java.lang.Exception

                    object UnsafeKtLogging {

                        val TAG = UnsafeKtLogging::class.java.simpleName

                        fun doSomething() {
                            Log.wtf(TAG, "WTF logging with unsafe logger")
                            Log.e(TAG, "Error logging with unsafe logger")
                            Log.d(TAG, "Debug logging with unsafe logger")
                            Log.i(TAG, "Info logging with unsafe logger")
                            Log.v(TAG, "Verbose logging with unsafe logger")

                            try {

                            } catch (e : Exception) {
                                e.printStackTrace()
                            }
                        }

                    }
                    """.trimIndent())
                )
                .issues(LoggerIssueDetector.ISSUE_LOG, LoggerIssueDetector.ISSUE_RAW_PRINTSTACKTRACE)
                .run()
                .expect("""
                        src/foo/UnsafeKtLogging.kt:11: Warning: Using android.util.Log instead of com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                Log.wtf(TAG, "WTF logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/UnsafeKtLogging.kt:12: Warning: Using android.util.Log instead of com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                Log.e(TAG, "Error logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/UnsafeKtLogging.kt:13: Warning: Using android.util.Log instead of com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                Log.d(TAG, "Debug logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/UnsafeKtLogging.kt:14: Warning: Using android.util.Log instead of com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                Log.i(TAG, "Info logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/UnsafeKtLogging.kt:15: Warning: Using android.util.Log instead of com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                Log.v(TAG, "Verbose logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/UnsafeKtLogging.kt:20: Warning: Using java.lang.Throwable.printStackTrace() instead of logging with com.yandex.launcher.logger.KLogger [AndroidDefLogger]
                                    e.printStackTrace()
                                    ~~~~~~~~~~~~~~~~~~~
                        0 errors, 6 warnings
                        """.trimIndent())
    }

    @Test
    fun kloggerOperationsKtTest() {
        lint()
            .files(
                LOGGER_STUB,
                kt("""
                    package foo

                    import com.yandex.launcher.logger.Logger
                    import java.lang.Exception

                    object LoggerKtLogging {

                        val TAG = LoggerKtLogging::class.java.simpleName

                        fun doSomething() {
                            Logger.e(TAG, "Error logging with unsafe logger")
                            Logger.d(TAG, "Debug logging with unsafe logger")
                            Logger.i(TAG, "Info logging with unsafe logger")
                            Logger.v(TAG, "Verbose logging with unsafe logger")
                            Logger.w(TAG, "Verbose logging with unsafe logger")
                        }

                    }
                    """.trimIndent())
            )
            .issues(LoggerIssueDetector.ISSUE_KLOGGER)
            .run()
            .expect("""
                        src/foo/LoggerKtLogging.kt:11: Warning: Using com.yandex.launcher.logger.Logger instead of com.yandex.launcher.logger.KLogger [LoggerUsageInKotlin]
                                Logger.e(TAG, "Error logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/LoggerKtLogging.kt:12: Warning: Using com.yandex.launcher.logger.Logger instead of com.yandex.launcher.logger.KLogger [LoggerUsageInKotlin]
                                Logger.d(TAG, "Debug logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/LoggerKtLogging.kt:13: Warning: Using com.yandex.launcher.logger.Logger instead of com.yandex.launcher.logger.KLogger [LoggerUsageInKotlin]
                                Logger.i(TAG, "Info logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/LoggerKtLogging.kt:14: Warning: Using com.yandex.launcher.logger.Logger instead of com.yandex.launcher.logger.KLogger [LoggerUsageInKotlin]
                                Logger.v(TAG, "Verbose logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        src/foo/LoggerKtLogging.kt:15: Warning: Using com.yandex.launcher.logger.Logger instead of com.yandex.launcher.logger.KLogger [LoggerUsageInKotlin]
                                Logger.w(TAG, "Verbose logging with unsafe logger")
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        0 errors, 5 warnings
                        """.trimIndent())
    }

    @Test
    fun assignmentLoggerToVariableJavaTest() {
        lint()
            .files(
                    IERROR_LOGGER_STUB,
                    ILOGGER_STUB,
                    LOGGER_STUB,
                    KLOGGER_STUB,
                    java("""
                    package foo;

                    import com.yandex.launcher.logger.ILogger;
                    import com.yandex.launcher.logger.IErrorLogger;
                    import com.yandex.launcher.logger.KLogger;

                    public class UsageJavaLogger {

                        public static final String TAG = UsageJavaLogger.class.getSimpleName();

                        private ILogger mLogger = null;
                        public IErrorLogger mErrorLogger = null;

                        public static void doSomething() {
                            KLogger.report(TAG);
                            KLogger.secure(TAG);

                            ILogger logger = KLogger.report(TAG);
                            IErrorLogger errorLogger = KLogger.secure(TAG);

                            mErrorLogger = KLogger.report(TAG);
                            mLogger = KLogger.secure(TAG);
                        }
                    }
                    """.trimIndent())
            )
            .issues(LoggerIssueDetector.ISSUE_LOGGER_ASSIGNMENT)
            .run()
            .expect("""
            src/foo/UsageJavaLogger.java:18: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    ILogger logger = KLogger.report(TAG);
                                     ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageJavaLogger.java:19: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    IErrorLogger errorLogger = KLogger.secure(TAG);
                                               ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageJavaLogger.java:21: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    mErrorLogger = KLogger.report(TAG);
                                   ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageJavaLogger.java:22: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    mLogger = KLogger.secure(TAG);
                              ~~~~~~~~~~~~~~~~~~~
            0 errors, 4 warnings
            """.trimIndent())
    }

    @Test
    fun assignmentLoggerToVariableKtTest() {
        lint()
            .files(
                    IERROR_LOGGER_STUB,
                    ILOGGER_STUB,
                    LOGGER_STUB,
                    KLOGGER_STUB,
                    kt("""
                    package foo

                    import com.yandex.launcher.logger.ILogger;
                    import com.yandex.launcher.logger.IErrorLogger;
                    import com.yandex.launcher.logger.KLogger;

                    object UsageKtLogger {

                        val TAG = UsageKtLogger::class.java.simpleName

                        var mLogger: ILogger? = null
                        var mErrorLogger: IErrorLogger? = null

                        fun doSomething() {
                            KLogger.report(TAG)
                            KLogger.secure(TAG)

                            val logger = KLogger.report(TAG)
                            val errorLogger = KLogger.secure(TAG)

                            mErrorLogger = KLogger.report(TAG)
                            mLogger = KLogger.secure(TAG)
                        }

                    }
                    """.trimIndent())
            )
            .issues(LoggerIssueDetector.ISSUE_LOGGER_ASSIGNMENT)
            .run()
            .expect("""
            src/foo/UsageKtLogger.kt:18: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    val logger = KLogger.report(TAG)
                                 ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageKtLogger.kt:19: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    val errorLogger = KLogger.secure(TAG)
                                      ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageKtLogger.kt:21: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    mErrorLogger = KLogger.report(TAG)
                                   ~~~~~~~~~~~~~~~~~~~
            src/foo/UsageKtLogger.kt:22: Warning: The result of the method is assigned to a variable. If you want to create Logger instance, please use Logger.createInstance(TAG) instead. [LoggerAssignment]
                    mLogger = KLogger.secure(TAG)
                              ~~~~~~~~~~~~~~~~~~~
            0 errors, 4 warnings
            """.trimIndent())
    }
}
