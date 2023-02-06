package ru.yandex.quasar.centaur_app.div

import org.json.JSONObject
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.mock
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.centaur_app.FakeMetricaReporter
import ru.yandex.quasar.centaur_app.utils.Resulting
import ru.yandex.quasar.div.container.contracts.DivInstanceIdentifier
import ru.yandex.quasar.div.container.contracts.Logger
import ru.yandex.quasar.div.container.registry.DivInstance
import ru.yandex.quasar.div.container.view.DivContainerView

@RunWith(RobolectricTestRunner::class)
class DivRegistryImplTest: BaseTest() {

    private lateinit var registry: DivRegistryImpl
    private lateinit var spy: CallbackSpy

    @Before
    fun setUp() {
        spy = CallbackSpy()
        registry = DivRegistryImpl(
            logger = object: Logger {
                override fun debug(message: String) {}
                override fun error(message: String, throwable: Throwable?) {}
            },
            stasher = spy,
            unstasher = spy
        )
    }

    @Test
    fun `when there is no item to stash then do nothing`() {
        val identifier = makeIdentifier()
        registry.stash(identifier)
        assert(!registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))
    }

    @Test
    fun `when show view registered it could be stashed`() {
        val identifier = makeIdentifier()
        registry.register(identifier, makeShowView(identifier)!!)

        assert(registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))
    }

    @Test
    fun `when show view registered then unregistered it could not be stashed`() {
        val identifier = makeIdentifier()
        registry.register(identifier, makeShowView(identifier)!!)
        registry.notifyCleaned(identifier)

        assert(!registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))
    }

    @Test
    fun `when show view is registered it could be stashed and unstashed`() {
        val identifier = makeIdentifier()
        registry.register(identifier, makeShowView(identifier)!!)

        // pre stash
        assert(registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))

        registry.stash(identifier)

        // stashed
        assert(!registry.canBeStashed(identifier))
        assert(registry.canBeUnstashed(identifier))
        assert(spy.toClose.size == 1)
        assert(spy.toClose[0].isIdenticalTo(identifier))
        assert(spy.toOpen.isEmpty())

        spy.reset()
        registry.unstash(identifier)

        // unstashed
        assert(registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))
        assert(spy.toClose.isEmpty())
        assert(spy.toOpen.size == 1)
        assert(spy.toOpen[0].showViewInfo != null)
        assert(spy.toOpen[0].showViewInfo!!.card.cardName == identifier.cardName)
        assert(spy.toOpen[0].showViewInfo!!.card.cardId == identifier.cardId)
    }

    @Test
    fun `when show view is registered with patches it could be stashed and unstashed with patches`() {
        val identifier = makeIdentifier()
        registry.register(identifier, makeShowView(identifier)!!)
        registry.register(identifier, makePatchView(identifier)!!)

        // pre stash
        assert(registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))

        registry.stash(identifier)

        // stashed
        assert(!registry.canBeStashed(identifier))
        assert(registry.canBeUnstashed(identifier))
        assert(spy.toClose.size == 1)
        assert(spy.toClose[0].isIdenticalTo(identifier))
        assert(spy.toOpen.isEmpty())

        spy.reset()
        registry.unstash(identifier)

        // unstashed
        assert(registry.canBeStashed(identifier))
        assert(!registry.canBeUnstashed(identifier))
        assert(spy.toClose.isEmpty())
        assert(spy.toOpen.size == 1)
        assert(spy.toOpen[0].showViewInfo != null)
        assert(spy.toOpen[0].showViewInfo!!.card.cardName == "A")
        assert(spy.toOpen[0].showViewInfo!!.card.cardId == "1")
        assert(spy.toOpen[0].patchesInfos.isEmpty())
        registry.notifyCreated(DivInstance(identifier, mock(DivContainerView::class.java)))
        assert(spy.toOpen.size == 2)
        assert(spy.toOpen[1].showViewInfo == null)
        assert(spy.toOpen[1].patchesInfos.size == 1)
        assert(spy.toOpen[1].patchesInfos[0].cardName == "A")
        assert(spy.toOpen[1].patchesInfos[0].cardId == "1")
    }

    private fun makeIdentifier(): DivInstanceIdentifier {
        return DivInstanceIdentifier(
            cardName = "A",
            cardId = "1"
        )
    }

    private fun makeShowView(identifier: DivInstanceIdentifier): ShowViewInfo? {
        return ShowViewInfo.Companion.parseDirectivePayload(
            JSONObject(
            """
{
    "div2_card": {
        "body": {
            "card": {
                "log_id": "div_registery_test",
                "states": []
            },
            "templates": {}
        },
        "card_name": "${identifier.cardName}",
        "card_id": ${identifier.cardId?.let { "\"" + it + "\""} ?: "null"},
        "global_templates": {
            "vault_images": {
                "body": {
                    "back_image": {}
                }
            }
        }
    },
    "layer": {
        "content": {}
    }
}
            """.trimIndent()
        ), FakeMetricaReporter()
        )
    }

    private fun makePatchView(identifier: DivInstanceIdentifier): PatchViewInfo? {
        val result = PatchViewInfo.Companion.parseDirectivePayload(
            JSONObject(
            """
{
    "div2_patch": {
        "body": {}                
    },
    "apply_to": {
        "card_name": "${identifier.cardName}",
        "card_id": ${identifier.cardId?.let { "\"" + it + "\"" } ?: "null" }
    }
}                    
            """.trimIndent()
            )
        )
        return when (result) {
            is Resulting.Failure -> null
            is Resulting.Success -> result.data
        }
    }
}

data class Info(
    val identifier: DivInstanceIdentifier,
    val showViewInfo: ShowViewInfo?,
    val patchesInfos: List<PatchViewInfo>
)

private class CallbackSpy: Stasher, Unstasher {
    var toClose = ArrayList<DivInstanceIdentifier>()
    var toOpen = ArrayList<Info>()

    fun reset() {
        toClose.clear()
        toOpen.clear()
    }

    override fun stash(identifier: DivInstanceIdentifier) {
        toClose.add(identifier)
    }

    override fun unstash(
        identifier: DivInstanceIdentifier,
        showViewInfo: ShowViewInfo
    ) {
        toOpen.add(Info(identifier, showViewInfo, emptyList()))
    }

    override fun unstash(identifier: DivInstanceIdentifier, patchesInfos: List<PatchViewInfo>) {
        toOpen.add(Info(identifier, null, patchesInfos))
    }
}
