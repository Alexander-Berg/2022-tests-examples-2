import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.MockRequestHandler
import io.ktor.client.engine.mock.respond
import io.ktor.client.request.HttpRequestData
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import org.junit.jupiter.api.fail

internal class RequestsHelper {
    private val handlers: MutableList<MockRequestHandler> = mutableListOf()

    fun addResponse(
        content: String = "{}",
        status: HttpStatusCode = HttpStatusCode.OK,
        block: HttpRequestData.() -> Unit = {},
    ) {
        handlers.add { request ->
            request.block()
            respond(
                content,
                status,
                headersOf(HttpHeaders.ContentType, "application/json"),
            )
        }
    }

    fun engine(): HttpClientEngine {
        if (handlers.isEmpty()) {
            addResponse { fail { "Shouldn't make any requests, $url" } }
        }
        return MockEngine.create {
            reuseHandlers = false
            requestHandlers.addAll(handlers)
        }
    }

    fun clear() {
        handlers.clear()
    }
}
