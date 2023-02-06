import ru.yandex.gradle.android._class.transform.log.*

object TestLoggingDecorator : LoggingFacade, TransformLogger {
    override val logger = this

    private val logs = ArrayList<String>()
    fun propagateLogs() = logger.logs

    override fun clear() {
        logs.clear()
    }

    override fun append(message: String) {
        logs.add(message)
    }
}