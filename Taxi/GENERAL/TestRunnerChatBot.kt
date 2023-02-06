package ru.yandex.taxi.arbitrage.modules.uitestrunner

import org.slf4j.LoggerFactory
import ru.yandex.taxi.arbitrage.di.DepsContainer
import ru.yandex.taxi.arbitrage.modules.admin.commands.PrPublishRunnerCI.Companion.PARAM_BUILD_ID
import ru.yandex.taxi.arbitrage.modules.bot.BotUpdatesFacade
import ru.yandex.taxi.arbitrage.modules.bot.TelegramInteractionFacade
import ru.yandex.taxi.arbitrage.modules.bot.UserValidation
import ru.yandex.taxi.arbitrage.modules.releases.ReleasesRepoProvider
import ru.yandex.taxi.arbitrage.modules.releases.ReleasesInfoService
import ru.yandex.taxi.arbitrage.modules.uitestrunner.kolhoz.KolhozPrUiTestRunner
import ru.yandex.taxi.arbitrage.utils.buffer.PrChatRingBuffer
import ru.yandex.taxi.arbitrage.utils.buffer.ReleasesTestConfig
import ru.yandex.taxi.arbitrage.utils.buffer.ReleasesRingBuffer
import ru.yandex.taxi.arbitrage.utils.regex.getPairedValue
import ru.yandex.taxi.arbitrage.utils.regex.parseAsInlineCommand
import ru.yandex.taxi.infra.im.telegram.InlineCallback
import ru.yandex.taxi.infra.im.telegram.TelegramFrom
import ru.yandex.taxi.infra.im.telegram.TelegramMessage
import ru.yandex.taxi.infra.im.telegram.TelegramUpdate
import ru.yandex.taxi.lang.kotlin.EMPTY_STRING

internal class TestRunnerChatBot(
    private val botApi: TelegramInteractionFacade,
    private val releaseInfoService: ReleasesInfoService = DepsContainer.releaseServiceContainer.releaseService,
    private val releasesInfoBuildHelper: ReleasesRepoProvider = DepsContainer.releaseServiceContainer.releaseBuildHelper,
    private val uiTestReportDecorator: UiTestReportDecorator = UiTestReportDecorator(botApi, releasesInfoBuildHelper)
) : BotUpdatesFacade, UserValidation by UserValidation.SimpleValidation {

    override fun initialize() {}

    private val logger = LoggerFactory.getLogger("TestRunnerChatBot")
    private fun acceptedCommands() = arrayOf(RUN_KOLHOZ_PR_UI_TEST, RUN_KOLHOZ_RELEASE_UI_TEST)

    override fun proceed(update: TelegramUpdate) {
        val commandLine = update.callback?.data
            ?: return

        val msgDto = update.callback
            ?: return

        if (acceptedCommands().any { it in commandLine }) {
            val params = commandLine.parseAsInlineCommand()

            when {
                commandLine.startsWith(RUN_KOLHOZ_PR_UI_TEST) -> runPrUiTest(msgDto, params)
                commandLine.startsWith(RUN_KOLHOZ_RELEASE_UI_TEST) -> runReleaseUiTest(msgDto, params)
            }
            return
        }
    }

    private fun runPrUiTest(msg: InlineCallback<TelegramFrom, TelegramMessage>, params: List<String>) {
        val msgInfo = msg.message
        val buildId = params.getPairedValue(PARAM_BUILD_ID) ?: ""

        PrChatRingBuffer.getByPullRequestBuild(buildId)?.let { prData ->
            KolhozPrUiTestRunner(prData, uiTestReportDecorator).runAsyncKolhozPrUiTest()
        }
            ?: reportTestNotRunning(msgInfo, buildId)
    }

    private fun runReleaseUiTest(msg: InlineCallback<TelegramFrom, TelegramMessage>, params: List<String>) {
        val msgInfo = msg.message
        val releaseBuildId = params.getPairedValue(PARAM_BUILD_ID)

        releaseBuildId?.let { releaseBuildId ->
            val releaseBuild = releasesInfoBuildHelper.getBuildByReleaseId(releaseBuildId.toLong())
            val uiTestConfig = ReleasesTestConfig(
                releaseBuild = releaseBuild,
                uiTestKolhozConfig = null
            )

            ReleasesRingBuffer.addToBuffer(uiTestConfig)
            releaseInfoService.runKolhozUiTest(uiTestConfig)
        }
            ?: reportTestNotRunning(msgInfo, EMPTY_STRING)
    }

    private fun reportTestNotRunning(msgInfo: TelegramMessage, buildId: String) {
        val msgText = msgInfo.text?: ""
        uiTestReportDecorator.reportPrUiTestWasNotRunning(msgText, msgInfo)
        logger.warn("Test not running by Telegram, because build $buildId not found")
    }

    companion object ReleaseCommands {
        const val RUN_KOLHOZ_PR_UI_TEST = "/runKolhozPrUiTest"
        const val RUN_KOLHOZ_RELEASE_UI_TEST = "/runKolhozReleaseUiTest"
    }
}