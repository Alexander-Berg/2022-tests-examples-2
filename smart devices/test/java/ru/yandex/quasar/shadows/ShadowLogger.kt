package ru.yandex.quasar.shadows

import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements
import ru.yandex.quasar.core.utils.Logger

@Implements(Logger::class)
@Suppress("unused", "MemberVisibilityCanBePrivate") // NOTE: because this is a shadow class
object ShadowLogger {

    data class LoggedItem(val level: String, val tag: String, val message: String, val throwable: Throwable?)

    var logged: ArrayList<LoggedItem> = ArrayList()

    @Implementation
    @JvmStatic
    fun d(tag: Any, msg: String) {
        d(tag.javaClass.name, msg)
    }

    @Implementation
    @JvmStatic
    fun d(tag: String, msg: String) {
        logged.add(LoggedItem("d", tag, msg, null))
    }

    @Implementation
    @JvmStatic
    fun d(tag: String, msg: String, thr: Throwable) {
        logged.add(LoggedItem("d", tag, msg, thr))
    }

    @Implementation
    @JvmStatic
    fun i(tag: String, msg: String) {
        logged.add(LoggedItem("i", tag, msg, null))
    }

    @Implementation
    @JvmStatic
    fun full(tag: String, msg: String) {
        val maxLogSize = 1000
        for (i in 0..msg.length / maxLogSize) {
            val start = i * maxLogSize
            var end = (i + 1) * maxLogSize
            end = if (end > msg.length) msg.length else end
            i(tag, msg.substring(start, end))
        }
    }

    @Implementation
    @JvmStatic
    fun printStackForDebug(tag: Any) {
        val stackTrace = Throwable().stackTrace
        for (element in stackTrace) {
            d(tag.toString(), "method: $element")
        }
    }

    @Implementation
    @JvmStatic
    fun method(tag: Any) {
        val stackTrace = Throwable().stackTrace
        val i = getSelfElementIndex(stackTrace, tag.javaClass)
        if (i < 0) return
        val caller = stackTrace[i]
        d(tag.javaClass.name, "method: " + caller.methodName)
    }

    @Implementation
    @JvmStatic
    fun methodForDebug(tag: Any) {
        method(tag)
    }

    @Implementation
    @JvmStatic
    fun e(tag: String, errMessage: String, thr: Throwable) {
        logged.add(LoggedItem("e", tag, errMessage, thr))
    }

    @Implementation
    @JvmStatic
    fun e(tag: String, errMessage: String) {
        logged.add(LoggedItem("e", tag, errMessage, null))
    }

    @Implementation
    @JvmStatic
    fun w(tag: String, errMessage: String, thr: Throwable) {
        logged.add(LoggedItem("w", tag, errMessage, thr))
    }

    @Implementation
    @JvmStatic
    fun w(tag: String, errMessage: String) {
        logged.add(LoggedItem("w", tag, errMessage, null))
    }

    @Implementation
    @JvmStatic
    fun e(tag: String, thr: Throwable) {
        logged.add(LoggedItem("e", tag, "", thr))
    }

    private fun getSelfElementIndex(stackTrace: Array<StackTraceElement>, cls: Class<*>): Int {
        for (i in stackTrace.indices) {
            val el = stackTrace[i]
            // We don't need to check method name, our logger has only one method.
            if (el.className == cls.name) {
                return i
            }
        }
        return -1
    }
}
