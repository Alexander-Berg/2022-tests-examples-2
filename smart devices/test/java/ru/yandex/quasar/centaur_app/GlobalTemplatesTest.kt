package ru.yandex.quasar.centaur_app

import android.app.Activity
import android.view.View
import android.widget.ImageView
import com.yandex.alicekit.core.json.ParsingErrorLogger
import com.yandex.div.core.Div2Logger
import com.yandex.div.core.DivCustomViewAdapter
import com.yandex.div.core.DivImageLoader
import com.yandex.div.core.DivViewFacade
import com.yandex.div.core.view2.Div2View
import com.yandex.div.view.image.LoadReference
import com.yandex.div2.DivAction
import com.yandex.div2.DivCustom
import com.yandex.div2.DivVisibilityAction
import com.yandex.images.ImageDownloadCallback
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.StandardTestDispatcher
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Before
import org.junit.Ignore
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.coroutines.TestScope
import ru.yandex.quasar.div.container.GlobalTemplatesKeeper
import ru.yandex.quasar.div.container.actions.DelegatingDivActionHandler
import ru.yandex.quasar.div.container.contracts.DivCardInfo
import ru.yandex.quasar.div.container.contracts.DivContainerConfiguration
import ru.yandex.quasar.div.container.contracts.DivInfo
import ru.yandex.quasar.div.container.contracts.Logger
import ru.yandex.quasar.div.container.initialization.InitializationContext
import ru.yandex.quasar.div.container.triggers.IntrinsicState
import ru.yandex.quasar.div.container.triggers.StateChangeEvent
import ru.yandex.quasar.div.container.view.DivContainerView

@RunWith(RobolectricTestRunner::class)
@OptIn(ExperimentalCoroutinesApi::class)
class GlobalTemplatesTest: BaseTest() {
    private lateinit var activity: Activity

    @Before
    fun setUp() {
        activity = Robolectric.buildActivity(Activity::class.java)
            .create(null)
            .resume()
            .get()
    }

    @Test
    @Ignore("CENTAUR-529")
    fun `when setup global templates check they are reported and supplied`() {
        val container = DivContainerView(activity)
        val divInfo = DivInfo(
            cardInfo = DivCardInfo(
                card = JSONObject(mapOf(
                    "log_id" to "some_screen",
                    "states" to JSONArray()
                )),
                cardName = "Testing",
                cardId = "1",
                templates = null,
                providedGlobalTemplates = mapOf("x" to JSONObject(mapOf("x" to "x")))
            )
        )
        val state = State()
        val testDispatcher = StandardTestDispatcher()
        val coroutineScope = TestScope(testDispatcher)

        val globalTemplatesSpy = GlobalTemplatesSpy()
        globalTemplatesSpy.providedTemplates["y"] = JSONObject(mapOf("y" to "y"))

        val configuration = DivContainerConfiguration(
            baseContext = activity,
            divInitializationContext = InitializationContext(
                imageLoader = FakeImageLoader(),
                extensionInitializer = { },
                delegatingDivActionHandler = FakeDivActionHandler(),
                delegatingCustomViewAdapter = FakeCustomViewAdapter(),
                delegatingDivLogger = Div2Logger.STUB,
                isVisualErrorsEnabled = { false }
            ),
            coroutineScope = coroutineScope,
            parsingErrorLogger = ParsingErrorLogger.LOG,
            logger = FakeLogger(),
            globalTemplatesKeeper = globalTemplatesSpy,
            triggersPostInitAction = {},
            postBindAction = { _, _ -> }
        )
        container.setup(divInfo, state, configuration)
        assert(globalTemplatesSpy.puttedTemplates.size == 1)
        assert(globalTemplatesSpy.puttedTemplates[0].containsKey("x"))
        assert(globalTemplatesSpy.acquiredTemplates.size == 1)
        assert(globalTemplatesSpy.acquiredTemplates[0].size == 2)
        assert(globalTemplatesSpy.acquiredTemplates[0][0].has("x"))
        assert(globalTemplatesSpy.acquiredTemplates[0][1].has("y"))
    }

    private class State : IntrinsicState {
        override fun reset() {
            // do nothing
        }

        override val stateChangeEvents: Flow<List<StateChangeEvent>> = MutableSharedFlow()
    }

    private class FakeLogger: Logger {
        override fun debug(message: String) {
        }

        override fun error(message: String, throwable: Throwable?) {
        }
    }

    private class GlobalTemplatesSpy: GlobalTemplatesKeeper {
        var providedTemplates = HashMap<String, JSONObject>()
        var puttedTemplates = ArrayList<Map<String, JSONObject>>()
        var acquiredTemplates = ArrayList<List<JSONObject>>()

        override var updates = MutableStateFlow<Map<String, JSONObject>>(mutableMapOf())

        override fun put(templates: Map<String, JSONObject>) {
            puttedTemplates.add(templates)
        }

        override fun acquire(): List<JSONObject> {
            val result = puttedTemplates
                .reduce { acc, item ->
                    val r = HashMap<String, JSONObject>()
                    r.putAll(acc)
                    r.putAll(item)
                    r
                }
                .values.toList() + providedTemplates.values.toList()
            acquiredTemplates.add(result)
            return result
        }
    }

    private class FakeImageLoader: DivImageLoader {
        override fun loadImage(imageUrl: String, callback: ImageDownloadCallback): LoadReference {
            return LoadReference {  }
        }

        override fun loadImage(imageUrl: String, imageView: ImageView): LoadReference {
            return LoadReference {  }
        }

        override fun loadImageBytes(imageUrl: String, callback: ImageDownloadCallback): LoadReference {
            return LoadReference {  }
        }

    }

    private class FakeDivActionHandler: DelegatingDivActionHandler {
        override fun handleDelegatedAction(action: DivAction, view: DivViewFacade, actionUid: String?): Boolean {
            return false
        }

        override fun handleDelegatedAction(action: DivVisibilityAction, view: DivViewFacade, actionUid: String?): Boolean {
            return false
        }
    }

    private class FakeCustomViewAdapter: DivCustomViewAdapter {
        override fun bindView(view: View, div: DivCustom, divView: Div2View) {

        }

        override fun createView(div: DivCustom, divView: Div2View): View {
            return View(divView.context)
        }

        override fun isCustomTypeSupported(type: String): Boolean {
            return false
        }

        override fun release(view: View, div: DivCustom) {

        }

    }
}
