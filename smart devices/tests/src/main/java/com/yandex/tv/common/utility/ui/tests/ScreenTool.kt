package com.yandex.tv.common.utility.ui.tests

import android.app.Activity
import android.os.Environment
import android.util.Log
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.ESPRESSO_LOG_TAG
import java.io.File
import java.util.regex.Pattern

object ScreenTool {
    private const val SPOON_SCREENSHOTS = "spoon-screenshots"
    private const val NAME_SEPARATOR = "_"
    private const val TEST_CASE_CLASS_JUNIT_4 = "org.junit.runners.model.FrameworkMethod$1"
    private const val TEST_CASE_METHOD_JUNIT_4 = "runReflectiveCall"
    private const val EXTENSION = ".png"
    private val LOCK = Any()
    private val TAG_VALIDATION = Pattern.compile("[a-zA-Z0-9_-]+")

    /**
     * Holds a set of directories that have been cleared for this test
     */
    private val clearedOutputDirectories: MutableSet<String> = HashSet()

    /**
     * Take a screenshot with the specified tag.
     *
     * @param activity Activity with which to capture a screenshot.
     * @param tag      Unique tag to further identify the screenshot. Must match [a-zA-Z0-9_-]+.
     * @return the image file that was created
     */
    fun screenshot(activity: Activity, tag: String): File {
        val testClass = findTestClassTraceElement(Thread.currentThread().stackTrace)
        val classNameRegex = "[^A-Za-z0-9._-]".toRegex()
        var className = "NoClassName"
        var methodName = "NoMethodName"
        if (testClass != null) {
            className = testClass.className.replace(classNameRegex, "_")
            methodName = testClass.methodName
        }
        return screenshot(activity, tag, className, methodName)
    }

    /**
     * Take a screenshot with the specified tag.  This version allows the caller to manually specify
     * the test class name and method name.  This is necessary when the screenshot is not called in
     * the traditional manner.
     *
     * @param activity Activity with which to capture a screenshot.
     * @param tag      Unique tag to further identify the screenshot. Must match [a-zA-Z0-9_-]+.
     * @return the image file that was created
     */
    private fun screenshot(
        activity: Activity, tag: String, testClassName: String,
        testMethodName: String
    ): File {
        require(TAG_VALIDATION.matcher(tag).matches()) { "Tag must match " + TAG_VALIDATION.pattern() + "." }
        return try {
            val screenshotDirectory = obtainScreenshotDirectory(testClassName, testMethodName)
            val screenshotName = System.currentTimeMillis().toString() + NAME_SEPARATOR + tag + EXTENSION
            val screenshotFile = File(screenshotDirectory, screenshotName)
            takeScreenshot(screenshotFile, activity)
            screenshotFile
        } catch (e: Exception) {
            throw RuntimeException("Unable to capture screenshot.", e)
        }
    }

    @Throws(IllegalAccessException::class)
    private fun obtainScreenshotDirectory(testClassName: String, testMethodName: String): File {
        return filesDirectory(SPOON_SCREENSHOTS, testClassName, testMethodName)
    }

    @Throws(IllegalAccessException::class)
    private fun filesDirectory(directoryType: String, testClassName: String, testMethodName: String): File {
        // Use external storage.
        val directory = File(Environment.getExternalStorageDirectory(), "app_$directoryType")
        if (directory.isDirectory) {
            clearedOutputDirectories.add(directoryType)
        }
        synchronized(LOCK) {
            if (!clearedOutputDirectories.contains(directoryType)) {
                deletePath(directory, false)
                clearedOutputDirectories.add(directoryType)
            }
        }
        val dirClass = File(directory, testClassName)
        val dirMethod = File(dirClass, testMethodName)
        createDir(dirMethod)
        return dirMethod
    }

    @Throws(IllegalAccessException::class)
    private fun createDir(dir: File) {
        val parent = dir.parentFile
        if (!parent.exists()) {
            createDir(parent)
        }
        if (!dir.exists() && !dir.mkdirs()) {
            throw IllegalAccessException("Unable to create output dir: " + dir.absolutePath)
        }
        chmodPlusRWX(dir)
    }

    private fun deletePath(path: File, inclusive: Boolean) {
        if (path.isDirectory) {
            val children = path.listFiles()
            if (children != null) {
                for (child in children) {
                    deletePath(child, true)
                }
            }
        }
        if (inclusive) {
            path.delete()
        }
    }

    private fun takeScreenshot(toFile: File?, activity: Activity?) {
        requireNotNull(activity) { "Parameter activity cannot be null." }
        requireNotNull(toFile) { "Parameter toFile cannot be null." }
        try {
            UiObjectHelpers.sDevice.takeScreenshot(toFile)
        } catch (e: Exception) {
            val message = ("Unable to take screenshot to file " + toFile.absolutePath
                    + " of activity " + activity.javaClass.name)
            Log.e(ESPRESSO_LOG_TAG, message, e)
            throw UnableToTakeScreenshotException(message, e)
        }
        Log.d(ESPRESSO_LOG_TAG, "Screenshot captured to " + toFile.absolutePath)
    }

    /**
     * Returns the test class element by looking at the method InstrumentationTestCase invokes.
     */
    private fun findTestClassTraceElement(trace: Array<StackTraceElement>): StackTraceElement? {
        return try {
            for (i in trace.indices.reversed()) {
                val element = trace[i]
                if (TEST_CASE_CLASS_JUNIT_4 == element.className && TEST_CASE_METHOD_JUNIT_4 == element.methodName) {
                    return trace[i - 2]
                }
            }
            null
        } catch (e: IllegalArgumentException) {
            null
        }
    }

    private fun chmodPlusRWX(file: File) {
        file.setReadable(true, false)
        file.setWritable(true, false)
        file.setExecutable(true, false)
    }

    private class UnableToTakeScreenshotException(detailMessage: String, exception: Exception) :
        RuntimeException(detailMessage, extractException(exception)) {
        companion object {
            /**
             * Method to avoid multiple wrapping. If there is already our exception,
             * just wrap the cause again
             */
            private fun extractException(ex: Exception): Throwable? {
                return if (ex is UnableToTakeScreenshotException) {
                    ex.cause
                } else ex
            }
        }
    }
}