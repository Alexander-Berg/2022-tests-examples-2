package org.jetbrains.teamcity.rest

import org.apache.log4j.*
import java.io.File
import java.io.FileInputStream
import java.util.*
import kotlin.reflect.KFunction
import kotlin.reflect.KProperty
import kotlin.reflect.full.valueParameters

private val TEAMCITY_CONNECTION_FILE_PATH = "teamcity_connection.properties"

//slf4j simple ignores debug output
fun setupLog4jDebug() {
    LogManager.resetConfiguration()
    Logger.getRootLogger().removeAllAppenders()
    Logger.getRootLogger().addAppender(ConsoleAppender(PatternLayout("TEST[%d] %6p [%15.15t] - %30.30c - %m %n")))
    Logger.getLogger("jetbrains").level = Level.DEBUG
    Logger.getLogger("org.apache.http").level = Level.ERROR
}

val publicInstanceUrl = "http://localhost:8111"

fun publicInstance() = TeamCityInstanceFactory.guestAuth(publicInstanceUrl).withLogResponses()

fun customInstance(serverUrl: String, username: String, password: String) = TeamCityInstanceFactory
    .httpAuth(serverUrl, username, password)
    .withLogResponses()

fun haveCustomInstance(): Boolean = ConnectionPropertiesFileLoader(TEAMCITY_CONNECTION_FILE_PATH).validate()

fun customInstanceByConnectionFile(): TeamCityInstance {
    val connectionPropertiesFileLoader = ConnectionPropertiesFileLoader(TEAMCITY_CONNECTION_FILE_PATH)
    return if (connectionPropertiesFileLoader.validate()) {
        val connectionConfig = connectionPropertiesFileLoader.fetch()
        customInstance(
            connectionConfig.serverUrl,
            connectionConfig.username,
            connectionConfig.password
        )
    } else {
        publicInstance()
    }
}

val reportProject = ProjectId("ProjectForReports")
val testProject = ProjectId("TestProject")
val changesBuildConfiguration = BuildConfigurationId("ProjectForSidebarCounters_MultibranchChange")
val testsBuildConfiguration = BuildConfigurationId("ProjectForSidebarCounters_MultibranchTestResult")
val runTestsBuildConfiguration = BuildConfigurationId("TestProject_RunTests")
val dependantBuildConfiguration = BuildConfigurationId("TeamcityTestMetadataDemo_TestMetadataDemo")
val pausedBuildConfiguration = BuildConfigurationId("ProjectForReports_TestPaused")
val manyTestsBuildConfiguration = BuildConfigurationId("TeamcityTestData_Test")

internal class ConnectionPropertiesFileLoader(filePath: String) {

    private val connectionFile: File?

    init {
        val classLoader = javaClass.classLoader
        connectionFile = classLoader.getResource(filePath)?.let { File(it.file) }
    }

    fun fetch(): ConnectionConfig {
        if (!validate()) {
            throw IllegalStateException("Properties are invalid")
        }
        val connectionProperties = Properties()
        connectionProperties.load(FileInputStream(connectionFile))
        return ConnectionConfig(
            connectionProperties.getProperty(SERVER_URL),
            connectionProperties.getProperty(USERNAME),
            connectionProperties.getProperty(PASSWORD)
        )
    }

    fun validate(): Boolean {
        if (connectionFile == null || !connectionFile.exists()) return false
        val connectionProperties = Properties()
        connectionProperties.load(FileInputStream(connectionFile))
        return validateConnectionProperties(connectionProperties)
    }

    private fun validateConnectionProperties(connectionProperties: Properties): Boolean {
        return validPropertyValue(connectionProperties.getProperty(SERVER_URL))
                && validPropertyValue(connectionProperties.getProperty(USERNAME))
                && validPropertyValue(connectionProperties.getProperty(PASSWORD))
    }

    private fun validPropertyValue(value: String?): Boolean {
        return (value != null) && (!value.isNullOrEmpty())
    }

    companion object {
        val SERVER_URL = "serverUrl"
        val USERNAME = "username"
        val PASSWORD = "password"
    }
}

internal class ConnectionConfig(val serverUrl: String, val username: String, val password: String)

inline fun <reified T> callPublicPropertiesAndFetchMethods(instance: T) {
    instance.toString()

    for (member in T::class.members) {
        when (member) {
            is KProperty<*> -> {
                member.getter.call(instance)
//                    println("${member.name} = ${member.getter.call(instance)}")
            }

            is KFunction<*> -> if (
                member.name.startsWith("fetch") ||
                member.name.startsWith("get")
            ) {
                if (member.valueParameters.isEmpty()) {
                    member.call(instance)
//                    println("${member.name} = ${member.call(instance)}")
                }
            }
        }
    }
}
