package ru.yandex.taximeter.swagger

import com.google.gson.GsonBuilder
import com.google.gson.reflect.TypeToken
import okhttp3.OkHttpClient
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.AfterClass
import org.junit.Assert
import org.junit.BeforeClass
import org.junit.Test
import ru.yandex.taxi.swagger.test.additionalpropertiestrueallof.api.TestAddpropsApiImpl
import ru.yandex.taxi.swagger.test.common.api.TestCommonApi
import ru.yandex.taxi.swagger.test.common.api.TestCommonApiImpl
import ru.yandex.taxi.swagger.test.common.model.CommonRequestImpl
import ru.yandex.taxi.swagger.test.common.model.CommonResponse
import ru.yandex.taxi.swagger.test.inlinebuiltintypes.api.TestInlineBuiltinAlloffApiImpl
import ru.yandex.taxi.swagger.test.inlinebuiltintypes.api.TestInlineBuiltinApiImpl
import ru.yandex.taxi.swagger.test.inlinebuiltintypes.model.BuiltInResponse
import ru.yandex.taxi.swagger.test.refadditionalprops.api.TestRefAddpropsApiImpl
import ru.yandex.taxi.swagger.test.refadditionalprops.model.CheckResults
import ru.yandex.taxi.swagger.test.refadditionalprops.model.RefAdditionalPropsResponse
import ru.yandex.taxi.swagger.test.refenumdiscriminator.api.RefEnumApiImpl
import ru.yandex.taxi.swagger.test.refenumdiscriminator.model.CommonEnum
import ru.yandex.taxi.swagger.test.refenumdiscriminator.model.CommonEnumVarOneOfResponse
import ru.yandex.taxi.swagger.test.sealedclass.api.TestSealedApiImpl
import ru.yandex.taxi.swagger.test.sealedclass.model.CheckResult
import ru.yandex.taxi.swagger.test.sealedclassbydiscriminator.api.TestSealedByDiscriminatorApiImpl
import ru.yandex.taxi.swagger.test.sealedclassbydiscriminator.model.CheckResultByDiscriminator
import ru.yandex.taximeter.swagger.client.RequestResult
import ru.yandex.taximeter.swagger.client.RequestResult.Response.HttpError
import ru.yandex.taximeter.swagger.client.RequestResult.Response.Success
import ru.yandex.taximeter.swagger.utils.CheckResultsJsonDeserializer
import ru.yandex.taximeter.swagger.utils.Utils

class SwaggerCodegenTest {

    companion object {
        private val gson = GsonBuilder()
            .registerTypeAdapter(
                object : TypeToken<Map<String, CheckResults>>() {}.type,
                CheckResultsJsonDeserializer(GsonBuilder().create())
            )
            .create()

        private val client = SwaggerTestHttpClient(
            okHttpClient = OkHttpClient(),
            hostProvider = { "http://localhost:1080" }
        )

        private lateinit var mockWebServer: MockWebServer

        @JvmStatic
        @BeforeClass
        fun beforeClass() {
            mockWebServer = MockWebServer()
            mockWebServer.start(1080)
        }

        @AfterClass
        fun afterClass() {
            mockWebServer.shutdown()
        }
    }

    @Test
    fun `additionalProperties true and allOf`() {
        val api = TestAddpropsApiImpl(gson, client)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testOneResponseJson))
        val responseOne = api.blockingtestAddpropsOneGet()

        Assert.assertTrue(responseOne is Success<*, *>)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testTwoResponseJson))
        val responseTwo = api.blockingtestAddpropsTwoGet()

        Assert.assertTrue(responseTwo is Success<*, *>)
    }

    @Test
    fun `oneOf produces sealed class`() {
        fun assert(requestResult: RequestResult<CheckResult, String>) {
            when (requestResult) {
                is Success -> {
                    when (requestResult.data) {
                        is CheckResult.SuccessResultVariant -> Assert.assertEquals(requestResult.data.type, "success")
                        is CheckResult.FailureResultVariant -> Assert.assertEquals(requestResult.data.type, "failure")
                    }
                }
                else -> throw IllegalStateException("not handled")
            }
        }

        val api = TestSealedApiImpl(gson, client)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testSealedSuccessJson))
        val responseOne = api.blockingtestSealedSuccessGet()

        Assert.assertTrue(responseOne is Success<*, *>)
        assert(responseOne)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testSealedFailureJson))
        val responseTwo = api.blockingtestSealedFailureGet()

        Assert.assertTrue(responseTwo is Success<*, *>)
        assert(responseTwo)
    }

    @Test
    fun `oneOf resolved by discriminator mapping`() {
        fun assert(requestResult: RequestResult<CheckResultByDiscriminator, String>) {
            when (requestResult) {
                is Success -> {
                    when (requestResult.data) {
                        is CheckResultByDiscriminator.SuccessResultByDiscriminatorVariant -> Assert.assertEquals(
                            requestResult.data.type,
                            "success"
                        )
                        is CheckResultByDiscriminator.FailureResultByDiscriminatorVariant -> Assert.assertEquals(
                            requestResult.data.type,
                            "failure"
                        )
                    }
                }
                else -> throw IllegalStateException("not handled")
            }
        }

        val api = TestSealedByDiscriminatorApiImpl(gson, client)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testSealedByDiscriminatorSuccessJson))
        val responseOne = api.blockingtestSealedSuccessGet()

        Assert.assertTrue(responseOne is Success<*, *>)
        assert(responseOne)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testSealedByDiscriminatorFailureJson))
        val responseTwo = api.blockingtestSealedFailureGet()

        Assert.assertTrue(responseTwo is Success<*, *>)
        assert(responseTwo)
    }

    @Test
    fun `ref discriminator enum type resolved correctly`() {
        val api = RefEnumApiImpl(gson, client)

        mockWebServer.enqueue(MockResponse().setBody(Utils.testSealedByRefEnumDiscriminatorSuccessJson))
        val responseOne = api.blockingtestCommonGet()

        Assert.assertTrue(responseOne is Success<*, *>)
        Assert.assertEquals((responseOne as Success<CommonEnumVarOneOfResponse, *>).data.type, CommonEnum.SUCCESSSTATUS)
    }

    @Test
    fun `built-in definition types are inlined`() {
        val api = TestInlineBuiltinApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setBody(Utils.testBuiltInJson))
        val response = api.blockingtestInlinebuiltinGet() as Success<BuiltInResponse, *>

        Assert.assertEquals(response.data.payload, "builtin")
    }

    @Test
    fun `built-in definition types are inlined in allOf object`() {
        val api = TestInlineBuiltinAlloffApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setBody(Utils.testBuiltInAllOfJson))
        val response = api.blockingtestAtolGet()

        Assert.assertTrue(response is Success<*, *>)
    }

    @Test
    fun `common get response 404`() {
        val api = TestCommonApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setResponseCode(404).setBody(Utils.error404))
        val response = api.blockingtestCommonGet()

        Assert.assertTrue(response is HttpError<*, *>)

        (response as HttpError<*, *>).apply {
            Assert.assertEquals(response.code, 404)
            Assert.assertTrue(response.data is TestCommonApi.testCommonGetHttpError.Error404)
        }
    }

    @Test
    fun `common get response 304`() {
        val api = TestCommonApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setResponseCode(304))
        val response = api.blockingtestCommonGet()
        Assert.assertTrue(response is HttpError<*, *>)

        (response as HttpError<*, *>).apply {
            Assert.assertEquals(response.code, 304)
        }
    }

    @Test
    fun `common post request with body`() {
        val api = TestCommonApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setBody(Utils.commonResponse))
        val response = api.blockingtestCommonPost(CommonRequestImpl(id = "123"))

        (response as Success<CommonResponse, *>).apply {
            Assert.assertTrue(response.data.version.isNotEmpty())
        }
    }

    @Test
    fun `common get response with headers`() {
        val api = TestCommonApiImpl(gson, client)
        mockWebServer.enqueue(
            MockResponse()
                .setBody(Utils.commonResponse)
                .setHeader("header_key", "header_value")
        )
        val response = api.blockingtestCommonGet()

        (response as Success<*, *>).apply {
            Assert.assertTrue(response.headers.containsKey("header_key"))
        }
    }

    @Test
    fun `common get request with params`() {
        val api = TestCommonApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setBody(Utils.commonResponse))
        val response = api.blockingtestCommonWithparamsGet(date = "2021-09-09", session = "session_id")

        Assert.assertTrue(response is Success<*, *>)
    }

    // fixme: fails even if deserializer is registered
    @Test(expected = RuntimeException::class)
    fun `additionalProperties value with custom type`() {
        val api = TestRefAddpropsApiImpl(gson, client)
        mockWebServer.enqueue(MockResponse().setBody(Utils.additionalPropertyWithCustomTypeResponse))
        val response = api.blockingtestGet()

        Assert.assertTrue((response as Success<RefAdditionalPropsResponse, *>).data.checkResults.isNotEmpty())
    }
}