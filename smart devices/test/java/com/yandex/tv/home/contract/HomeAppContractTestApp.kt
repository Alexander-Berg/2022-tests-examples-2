package com.yandex.tv.home.contract

import android.app.Application
import androidx.lifecycle.MutableLiveData
import com.yandex.io.sdk.environment.TandemInfoProvider
import com.yandex.launcher.logger.Logger
import com.yandex.tv.common.connectivity.ConnectivityReceiver
import com.yandex.tv.home.BrowsingActivity
import com.yandex.tv.home.HomeActivity
import com.yandex.tv.home.WebViewActivity
import com.yandex.tv.home.content.personal.PersonalCarouselsManager
import com.yandex.tv.home.informer.ConnectionErrorProvider
import com.yandex.tv.home.informer.InformersDataProvider
import com.yandex.tv.home.informer.TandemProvider
import com.yandex.tv.home.informer.TimeProvider
import com.yandex.tv.home.model.Carousel
import com.yandex.tv.home.model.Category
import com.yandex.tv.home.routing.BrowsingRouter
import com.yandex.tv.home.routing.HomeAppRouter
import com.yandex.tv.home.routing.HomeRouter
import com.yandex.tv.home.routing.WebViewRouter
import com.yandex.tv.home.ui.headers.CategoriesLoader
import com.yandex.tv.home.ui.headers.CategoryHeadersLoader
import com.yandex.tv.home.utils.ConsoleLogProcessor
import com.yandex.tv.home.utils.HttpRequestManager
import com.yandex.tv.home.utils.IdleExecutor
import org.koin.dsl.binds
import org.koin.dsl.module
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import org.mockito.kotlin.whenever

val TEST_REMOTE_CATEGORY = Category(categoryId = "test", persistentId = null, title = "test_title", rank = 10, icon = "")

class HomeAppContractTestApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Logger.setProcessor(ConsoleLogProcessor())
    }
}

class TestCategoryHeadersLoader : CategoryHeadersLoader() {
    override var categories: List<Category>? = listOf(TEST_REMOTE_CATEGORY)
}

class TestIdleExecutor : IdleExecutor() {
    override fun execute(label: String?, task: () -> Unit) = task()
}

val deeplinkTestModule = module {

    single<CategoriesLoader>(createdAtStart = true) { TestCategoryHeadersLoader() }

    single<ConnectivityReceiver> { mock() }

    single<TandemInfoProvider> { mock() }

    single<InformersDataProvider> { mock() } binds arrayOf(TimeProvider::class, ConnectionErrorProvider::class, TandemProvider::class)

    single<PersonalCarouselsManager> {
        mock<PersonalCarouselsManager>().apply {
            whenever(this.updatedCarousel).thenReturn(MutableLiveData<Carousel?>())
        }
    }

    single<HttpRequestManager> { mock() }

    scope<HomeActivity> {
        scoped<HomeAppRouter> { spy(HomeRouter(get()))}

        scoped<IdleExecutor> { TestIdleExecutor() }
    }

    scope<BrowsingActivity> {
        scoped<HomeAppRouter> { spy(BrowsingRouter(get())) }

        scoped<IdleExecutor> { TestIdleExecutor() }
    }

    scope<WebViewActivity> {
        scoped<HomeAppRouter> { spy(WebViewRouter(get())) }

        scoped<IdleExecutor> { TestIdleExecutor() }
    }
}
