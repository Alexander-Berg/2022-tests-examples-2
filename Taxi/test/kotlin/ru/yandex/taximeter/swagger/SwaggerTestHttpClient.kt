package ru.yandex.taximeter.swagger

import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import ru.yandex.taximeter.swagger.client.HttpClient
import ru.yandex.taximeter.swagger.client.RequestResult
import java.io.IOException
import java.net.SocketTimeoutException
import java.util.concurrent.TimeoutException

class SwaggerTestHttpClient(
    private val okHttpClient: OkHttpClient,
    private val hostProvider: () -> String
) : HttpClient {
    private companion object {
        private val JSON_MEDIA_TYPE = "application/json".toMediaType()
    }

    override fun <T, U> makeRequest(
        url: String,
        httpMethod: String,
        body: String?,
        queryParams: Map<String, String>,
        headerParams: Map<String, String>
    ): HttpClient.Result<T, U> {
        val requestUrlBuilder = hostProvider()
            .toHttpUrlOrNull()!!
            .newBuilder()
            .addPathSegments(url)

        queryParams.forEach { (param, value) ->
            requestUrlBuilder.addQueryParameter(param, value)
        }

        val requestUrl = requestUrlBuilder.build()

        val requestBuilder = Request
            .Builder()
            .url(requestUrl)
            .method(
                httpMethod,
                body?.toRequestBody(JSON_MEDIA_TYPE)
            )

        headerParams.forEach { (key, value) -> requestBuilder.header(key, value) }

        return makeRequest(requestBuilder.build())
    }

    private fun <T, U> makeRequest(request: Request): HttpClient.Result<T, U> {
        return try {
            val response = okHttpClient.newCall(request).execute()
            HttpClient.Result.Response(
                response.code,
                response.body?.charStream(),
                response.headers.toMultimap()
            )
        } catch (error: IOException) {
            when (error) {
                is SocketTimeoutException, is TimeoutException -> HttpClient.Result.IoError(
                    RequestResult.IoError.TimeoutError(error)
                )
                else -> HttpClient.Result.IoError(RequestResult.IoError.OtherIoError(error))
            }
        }
    }
}