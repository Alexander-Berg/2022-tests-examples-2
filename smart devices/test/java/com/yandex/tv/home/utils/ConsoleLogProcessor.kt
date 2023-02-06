package com.yandex.tv.home.utils

import android.util.Log
import android.util.SparseArray
import com.yandex.launcher.logger.processor.ILogProcessor
import java.util.Locale

class ConsoleLogProcessor : ILogProcessor {

    private val androidPriorityMap = SparseArray<String>()

    init {
        androidPriorityMap.put(
            ILogProcessor.Priority.V, "V"
        )
        androidPriorityMap.put(
            ILogProcessor.Priority.D, "D"
        )
        androidPriorityMap.put(
            ILogProcessor.Priority.I, "I"
        )
        androidPriorityMap.put(
            ILogProcessor.Priority.W, "W"
        )
        androidPriorityMap.put(
            ILogProcessor.Priority.E, "E"
        )
        androidPriorityMap.put(
            ILogProcessor.Priority.A, "ASSERT"
        )
    }

    override fun process(
        priority: Int,
        secure: Boolean,
        tag: String,
        fmt: String,
        args: Any?,
        reason: Throwable?,
        report: Boolean
    ) {
        var msg = formatMessage(fmt, args)

        if (reason != null) {
            msg = msg + '\n' + Log.getStackTraceString(reason)
        }

        println("${androidPriorityMap[priority]} $tag: $msg");
    }

    private fun formatMessage(fmt: String, args: Any?): String {
        return try {
            when (args) {
                null -> {
                    fmt
                }
                is Array<*> -> {
                    String.format(Locale.ENGLISH, fmt, *args)
                }
                else -> {
                    String.format(Locale.ENGLISH, fmt, args)
                }
            }
        } catch (e: Throwable) {
            "$fmt ($e)"
        }
    }
}
