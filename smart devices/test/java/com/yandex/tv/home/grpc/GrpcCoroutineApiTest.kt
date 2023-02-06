package com.yandex.tv.home.grpc

import NGProxy.GProxyGrpc
import com.yandex.tv.common.network.grpc.GrpcCoroutineApi
import com.yandex.tv.home.content.remote.grpc.GrpcCardDetailRequest
import com.yandex.tv.home.model.ContentItem
import com.yandex.tv.home.model.DimensionedUriMap
import com.yandex.tv.home.model.vh.VhEpisodeItem
import com.yandex.tv.home.network.ParseException
import io.grpc.ManagedChannel
import io.grpc.Status
import io.grpc.StatusException
import io.grpc.inprocess.InProcessChannelBuilder
import io.grpc.inprocess.InProcessServerBuilder
import io.grpc.stub.StreamObserver
import io.grpc.testing.GrpcCleanupRule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.asExecutor
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.instanceOf
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.JUnit4
import org.mockito.AdditionalAnswers.delegatesTo
import org.mockito.Mockito.mock
import ru.yandex.alice.protos.data.video.CardDetailProto
import kotlin.coroutines.cancellation.CancellationException
import kotlin.test.assertEquals

@RunWith(JUnit4::class)
class GrpcCoroutineApiTest {

    /**
     * This rule manages automatic graceful shutdown for the registered servers and channels
     * at the end of test.
     */
    @get:Rule
    val grpcCleanup: GrpcCleanupRule = GrpcCleanupRule()


    private var grpcCoroutineApi: GrpcCoroutineApi? = null

    /**
       Here we use cardDetail method to test general grpc aspects.
       It is easier than creating a separate dummy grpc stub for tests.
     */
    private var cardDetailResponse: ArrayList<GrpcResponseEvent<CardDetailProto.TTvCardDetailResponse>>? = null


    @Before
    fun before() {
        val serverName = InProcessServerBuilder.generateName()
        grpcCleanup.register(
            InProcessServerBuilder
                .forName(serverName)
                .addService(gProxyServiceMock)
                .directExecutor()
                .build()
                .start()
        )
        val channel: ManagedChannel = grpcCleanup.register(
            InProcessChannelBuilder
                .forName(serverName)
                .executor(Dispatchers.IO.asExecutor())
                .build()
        )

        grpcCoroutineApi = GrpcCoroutineApi(channel, CLIENT_TIMEOUT_MS)
        cardDetailResponse = null
    }

    @Test
    fun `server respond incorrect data, client gets onError`() = runBlocking {
        val cardDetailRequest = createRequest()
        cardDetailResponse = arrayListOf(
            GrpcResponseEvent.OnNext(CardDetailProto.TTvCardDetailResponse.getDefaultInstance()),
            GrpcResponseEvent.OnComplete(),
        )

        val result = kotlin.runCatching {
            grpcCoroutineApi!!.execGrpcRequest(cardDetailRequest)
        }

        // This is how default grpc implementation handles errors during onNext.
        // We can consider more explicit exceptions if we need.
        assertThat(result.exceptionOrNull(), instanceOf(ParseException::class.java))
        val t = result.exceptionOrNull() as ParseException

        assertEquals(t.message, "cannot parse ")
    }

    @Test
    fun `server does not respond, client timeouts`() = runBlocking {
        val cardDetailRequest = createRequest()
        cardDetailResponse = arrayListOf(
            GrpcResponseEvent.Sleep(SERVER_LONG_RESPONSE_MS),
            GrpcResponseEvent.OnNext(CardDetailProto.TTvCardDetailResponse.getDefaultInstance()),
            GrpcResponseEvent.OnComplete(),
        )

        val result = kotlin.runCatching {
            grpcCoroutineApi!!.execGrpcRequest(cardDetailRequest)
        }

        assertThat(result.exceptionOrNull(), instanceOf(StatusException::class.java))
        val t = result.exceptionOrNull() as StatusException

        assertThat(t.status.code, equalTo(Status.Code.DEADLINE_EXCEEDED))
    }

    @Test
    fun `cancel request, request canceled`() = runBlocking {
        val cardDetailRequest = createRequest()
        cardDetailResponse = arrayListOf(
            GrpcResponseEvent.Sleep(SERVER_LONG_RESPONSE_MS),
            GrpcResponseEvent.OnNext(CardDetailProto.TTvCardDetailResponse.getDefaultInstance()),
            GrpcResponseEvent.OnComplete(),
        )

        val deferred = async {
            grpcCoroutineApi!!.execGrpcRequest(cardDetailRequest)
        }
        delay(CLIENT_CANCEL_AFTER_MS)
        deferred.cancel(CancellationException("too slow!"))
        val result = kotlin.runCatching { deferred.await() }

        assertThat(result.exceptionOrNull(), instanceOf(CancellationException::class.java))
        assertThat(result.exceptionOrNull()!!.message, equalTo("too slow!"))
    }

    private fun createRequest(): GrpcCardDetailRequest {
        val contentItem = VhEpisodeItem.Builder().apply {
            id = "id"
            contentType = ContentItem.TYPE_VOD_EPISODE
            title = "title"
            thumbnailUrls = DimensionedUriMap.emptyDimensionedUriMap()
            ontoId = "ontoId"
        }.build()
        return GrpcCardDetailRequest(contentItem, false, null)
    }

    private val gProxyServiceMock: GProxyGrpc.GProxyImplBase = mock(
        GProxyGrpc.GProxyImplBase::class.java,
        delegatesTo<GProxyGrpc.GProxyImplBase>(
            object : GProxyGrpc.GProxyImplBase() {
                override fun getTvCardDetail(request: CardDetailProto.TTvCardDetailsRequest, responseObserver: StreamObserver<CardDetailProto.TTvCardDetailResponse>) {
                    cardDetailResponse?.let {
                        for (e in it) {
                            e.pushToObserver(responseObserver)
                        }
                    }
                }
            }))


    private sealed class GrpcResponseEvent<T> {
        abstract fun pushToObserver(observer: StreamObserver<T>)
        class OnNext<T>(val data: T): GrpcResponseEvent<T>() {
            override fun pushToObserver(observer: StreamObserver<T>) = observer.onNext(data)
        }
        class OnComplete<T>: GrpcResponseEvent<T>() {
            override fun pushToObserver(observer: StreamObserver<T>) = observer.onCompleted()
        }
        class OnError<T>(val t: Throwable): GrpcResponseEvent<T>() {
            override fun pushToObserver(observer: StreamObserver<T>) = observer.onError(t)
        }
        class Sleep<T>(val sleepMs: Long): GrpcResponseEvent<T>() {
            override fun pushToObserver(observer: StreamObserver<T>) = Thread.sleep(sleepMs)
        }
    }

    companion object {
        private const val SERVER_LONG_RESPONSE_MS = 5000L
        private const val CLIENT_TIMEOUT_MS = 2000L
        private const val CLIENT_CANCEL_AFTER_MS = 300L
    }
}
