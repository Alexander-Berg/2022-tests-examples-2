package ru.yandex.quasar.app.auth

import okhttp3.FormBody
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.Protocol
import okhttp3.Request
import okhttp3.Response
import okhttp3.ResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.fail
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.any
import org.mockito.Mockito.`when`
import org.mockito.Mockito.mock
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.utils.HttpClient
import java.io.IOException

@RunWith(RobolectricTestRunner::class)
class AuthUrlProviderTest {

    @Test
    fun getAuthUrlFormsCorrectRequestAndUrlWithTrack() {
        val client = mock(HttpClient::class.java)
        val trackIdUrl = "https://yandex.net"
        val trackId = "TrackId"
        val passportHost = "https://passport.yandex.ru"
        val xtoken = "xtoken"
        val redirectUrl = "https://yandex.ru"
        `when`(client.newRequest()).thenReturn(Request.Builder())
        `when`(client.executeForResult(any(), any() as HttpClient.ResponseFunction<String>?))
            .then { answer ->
                val request = (answer.arguments[0] as Request.Builder).build()
                assertEquals(trackIdUrl.toHttpUrlOrNull()?.host, request.url.host)
                assertEquals("OAuth $xtoken", request.header(AuthUrlProvider.AUTH_TOKEN_HEADER_NAME))
                val body = request.body as FormBody
                assertEquals(2, body.size)
                for (i in 0 until body.size) {
                    when {
                        body.name(i) == AuthUrlProvider.AUTH_TYPE_FIELD ->
                            assertEquals(AuthUrlProvider.AUTH_TYPE, body.value(i))
                        body.name(i) == AuthUrlProvider.REDIRECT_URL_FIELD ->
                            assertEquals(redirectUrl, body.value(i))
                        else -> fail("Unknown body field ${body.name(i)}")
                    }
                }
                val responseFunction = answer.arguments[1] as HttpClient.ResponseFunction<String>
                responseFunction.operate(createResponse(trackIdUrl, trackId, passportHost, true))
            }
        val authUrlProvider = AuthUrlProvider(client, { "DeviceId" }, { trackIdUrl })
        val authUrl = authUrlProvider.getAuthUrl(xtoken, redirectUrl)
        val url = authUrl.toHttpUrlOrNull()!!
        assertEquals(passportHost.toHttpUrlOrNull()?.host, url.host)
        assertEquals(trackId, url.queryParameter(AuthUrlProvider.TRACK_ID_FIELD))
    }

    @Test(expected = RuntimeException::class)
    fun getAuthUrlFailsOnNonOkResponse() {
        val client = mock(HttpClient::class.java)
        val trackIdUrl = "https://yandex.net"
        val trackId = "TrackId"
        val passportHost = "https://passport.yandex.ru"
        val xtoken = "xtoken"
        val redirectUrl = "https://yandex.ru"
        `when`(client.newRequest()).thenReturn(Request.Builder())
        `when`(client.executeForResult(any(), any() as HttpClient.ResponseFunction<String>?))
            .then { answer ->
                val responseFunction = answer.arguments[1] as HttpClient.ResponseFunction<String>
                responseFunction.operate(createResponse(trackIdUrl, trackId, passportHost, false))
            }
        val authUrlProvider = AuthUrlProvider(client, { "DeviceId" }, { trackIdUrl })
        val authUrl = authUrlProvider.getAuthUrl(xtoken, redirectUrl)
    }

    @Test(expected = AuthServerException::class)
    fun getAuthUrlThrowsAuthServerExceptionOnIOException() {
        val client = mock(HttpClient::class.java)
        val trackIdUrl = "https://yandex.net"
        val trackId = "TrackId"
        val passportHost = "https://passport.yandex.ru"
        val xtoken = "xtoken"
        val redirectUrl = "https://yandex.ru"
        `when`(client.newRequest()).thenReturn(Request.Builder())
        `when`(client.executeForResult(any(), any() as HttpClient.ResponseFunction<String>?))
            .then {
                throw IOException()
            }
        val authUrlProvider = AuthUrlProvider(client, { "DeviceId" }, { trackIdUrl })
        val authUrl = authUrlProvider.getAuthUrl(xtoken, redirectUrl)
    }

    @Test(expected = AuthServerException::class)
    fun getAuthUrlThrowsAuthServerExceptionOnServerError() {
        val client = mock(HttpClient::class.java)
        val trackIdUrl = "https://yandex.net"
        val trackId = "TrackId"
        val passportHost = "https://passport.yandex.ru"
        val xtoken = "xtoken"
        val redirectUrl = "https://yandex.ru"
        `when`(client.newRequest()).thenReturn(Request.Builder())
        `when`(client.executeForResult(any(), any() as HttpClient.ResponseFunction<String>?))
            .then { answer ->
                val responseFunction = answer.arguments[1] as HttpClient.ResponseFunction<String>
                responseFunction.operate(createResponse(trackIdUrl, trackId, passportHost,
                    false, 500))
            }
        val authUrlProvider = AuthUrlProvider(client, { "DeviceId" }, { trackIdUrl })
        val authUrl = authUrlProvider.getAuthUrl(xtoken, redirectUrl)
    }

    @Test(expected = RuntimeException::class)
    fun getAuthUrlThrowsRuntimeExceptionOnNonServerError() {
        val client = mock(HttpClient::class.java)
        val trackIdUrl = "https://yandex.net"
        val trackId = "TrackId"
        val passportHost = "https://passport.yandex.ru"
        val xtoken = "xtoken"
        val redirectUrl = "https://yandex.ru"
        `when`(client.newRequest()).thenReturn(Request.Builder())
        `when`(client.executeForResult(any(), any() as HttpClient.ResponseFunction<String>?))
            .then { answer ->
                val responseFunction = answer.arguments[1] as HttpClient.ResponseFunction<String>
                responseFunction.operate(createResponse(trackIdUrl, trackId, passportHost,
                    false, 404))
            }
        val authUrlProvider = AuthUrlProvider(client, { "DeviceId" }, { trackIdUrl })
        val authUrl = authUrlProvider.getAuthUrl(xtoken, redirectUrl)
    }

    private fun createResponse(url: String, trackId: String, passportHost: String,
                               ok: Boolean, code: Int = 200): Response {
        return Response.Builder()
            .code(code)
            .request(Request.Builder().url(url).build())
            .protocol(Protocol.HTTP_2)
            .message("Message")
            .body(ResponseBody.create(null,
                "{" +
                    "\"status\": \"${if (ok) "ok" else "error"}\", " +
                    "\"track_id\": \"$trackId\", " +
                    "\"passport_host\": \"$passportHost\"" +
                    "}"))
            .build()
    }
}
