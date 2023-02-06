package ru.yandex.taxi.arbitrage.deployer.stubs

import ru.yandex.taxi.arbitrage.web.projects.Project.ITAXIMETER
import ru.yandex.taxi.arbitrage.web.projects.Project.TAXIMETER
import ru.yandex.taxi.arbitrage.web.releaseDeployer.DRAFT_SIGNER_STATUS
import ru.yandex.taxi.arbitrage.web.releaseDeployer.DeployModel
import ru.yandex.taxi.arbitrage.web.releaseDeployer.DeployStatus
import ru.yandex.taxi.arbitrage.web.releaseDeployer.DeployStatus.ADDED_TO_SLUG
import ru.yandex.taxi.arbitrage.web.releaseDeployer.DeployViewModel
import ru.yandex.taxi.arbitrage.web.releaseDeployer.HuaweiBuildInfo
import ru.yandex.taxi.arbitrage.web.releaseDeployer.ViewChoiceVersionHandler
import ru.yandex.taxi.arbitrage.web.releaseDeployer.ViewChoiceVersionHandler.DEPLOY
import ru.yandex.taxi.infra.storeship.Track
import ru.yandex.taxi.infra.storeship.VersionInfo
import ru.yandex.taxi.infra.storeship.VersionInfoResult
import ru.yandex.taxi.lang.kotlin.EMPTY_STRING

internal object TestDeployDataProvider {
    internal val defaultVersionInfoPercent = "0"
    internal val defaultVersionInfoError = listOf("testError")
    internal val defaultReleaseId = 1L
    internal val defaultAppVersion = "appVersion"
    internal val defaulTestDistributionParam = "yandex"
    internal val defaultTestLastReleaseNum = "lastReleaseNum"
    internal val defaultProject: String = TAXIMETER.name
    internal val defaultSignerStatus = DRAFT_SIGNER_STATUS
    internal val defaultDeployPercent = defaultVersionInfoPercent.toInt()
    internal val defaultDeployStatus = ADDED_TO_SLUG
    internal val defaultBuildLink = "chainLink"

    internal val frontHeadersList = listOf("appVersion", "appDistribution", "chainBuildLink", "lastReleaseNum", "deployStatus", "deployPercent", "signerStatus", "projectName", "huaweiBuildInfo")

    internal val defaultSignRequestId = "testSignRequestId"

    internal val defaultDeployListModel = listOf(
        DeployModel(1, defaultAppVersion, defaulTestDistributionParam, defaultBuildLink, defaultTestLastReleaseNum, projectName = TAXIMETER.name),
        DeployModel(2, defaultAppVersion, defaulTestDistributionParam, defaultBuildLink, defaultTestLastReleaseNum, projectName = ITAXIMETER.name)
    )

    internal val defaultHuaweiListModel = listOf(
        HuaweiBuildInfo("signRequestId1", prodBuildNumber = "1", projectName = TAXIMETER.name),
        HuaweiBuildInfo("signRequestId2", prodBuildNumber = "2", projectName = ITAXIMETER.name)
    )

    internal fun HuaweiInfoBuilder(
        signRequestId: String = defaultSignRequestId,
        deployPercent: Int = 0,
        prodBuildNumber: String = defaultTestLastReleaseNum,
        project: String = defaultProject
    ) = HuaweiBuildInfo(
        signRequestId = signRequestId,
        deployPercent = deployPercent,
        prodBuildNumber = prodBuildNumber,
        projectName = project
    )

    internal fun versionInfoGenerator(
        lastReleaseNumber: String,
        newDeployPercent: String = defaultVersionInfoPercent,
        newSignerStatus: String = DRAFT_SIGNER_STATUS,
        versionInfoErrors: List<String>? = emptyList(),
        versionResultErrors: String = EMPTY_STRING
    ) = VersionInfoResult(
        data = VersionInfo(
            deployedPercentage = newDeployPercent,
            errors = versionInfoErrors,
            id = 91,
            notes = mapOf("ru-Ru" to "testNotes"),
            status = newSignerStatus,
            track = Track(
                id = 89,
                slug = "beta",
                appName = "Таксометр бета",
                appSlug = "taximeter-Beta"
            ),
            number = lastReleaseNumber
        ),
        errors = versionResultErrors
    )

    internal fun deployModelGenerator(
        releaseId: Long = defaultReleaseId,
        distributionParam: String = defaulTestDistributionParam,
        lastReleaseNum: String = defaultTestLastReleaseNum,
        deployPercent: Int = defaultDeployPercent,
        project: String = defaultProject,
        appVersion: String = defaultAppVersion,
        signerStatus: String = defaultSignerStatus,
        deployStatus: DeployStatus = defaultDeployStatus,
        errors: List<String>? = emptyList(),
        huaweiBuildInfo: HuaweiBuildInfo? = null,
        timestamp: Long? = null
    ) = DeployModel(
        releaseId = releaseId,
        appVersion = appVersion,
        appDistribution = distributionParam,
        chainBuildLink = defaultBuildLink,
        lastReleaseNum = lastReleaseNum,
        deployStatus = deployStatus,
        deployPercent = deployPercent,
        signerStatus = signerStatus,
        projectName = project,
        errors = errors,
        huaweiBuildInfo = huaweiBuildInfo,
        firstDeployTimeStamp = timestamp
    )

    internal fun deployViewModelGenerator(
        releaseId: Long = 1,
        appVersion: String = defaultAppVersion,
        distributionParam: String = defaulTestDistributionParam,
        lastReleaseNum: String = defaultTestLastReleaseNum,
        signerStatus: String = defaultSignerStatus,
        deployStatus: String = defaultDeployStatus.name,
        deployPercent: Int = 0,
        projectName: String = TAXIMETER.name,
        errors: List<String>? = emptyList(),
        previousVersionHandler: ViewChoiceVersionHandler = DEPLOY,
        frontTableFields: List<String> = frontHeadersList
    ): DeployViewModel {
        return DeployViewModel(
            releaseId = releaseId,
            appVersion = appVersion,
            appDistribution = distributionParam,
            chainBuildLink = defaultBuildLink,
            lastReleaseNum = lastReleaseNum,
            deployStatus = deployStatus,
            deployPercent = deployPercent,
            signerStatus = signerStatus,
            projectName = projectName,
            errors = errors,
            previousVersionHandler = previousVersionHandler,
            frontTableFields = frontTableFields
        )
    }
}