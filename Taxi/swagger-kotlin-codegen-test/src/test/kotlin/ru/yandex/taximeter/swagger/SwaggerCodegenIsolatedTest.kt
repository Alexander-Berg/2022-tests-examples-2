package ru.yandex.taximeter.swagger

import io.swagger.codegen.v3.DefaultGenerator
import io.swagger.codegen.v3.config.CodegenConfigurator
import org.junit.Assert
import org.junit.Test
import java.nio.file.Paths
import kotlin.io.path.absolutePathString

class SwaggerCodegenIsolatedTest {

    @Test
    fun `oneOf with conflicting properties throws exception`() {
        val msgRegex = "oneOf model <.*> has properties with equal names but different types".toRegex()
        val swaggerPath = Paths.get("src", "test", "swagger", "oneOf-with-conflicting-properties.yaml")
        val buildPath = Paths.get("build", "generated", "swagger")
        val config = CodegenConfigurator().apply {
            inputSpecURL = swaggerPath.absolutePathString()
            outputDir = buildPath.absolutePathString()
            lang = "kotlin-client"
            additionalProperties = additionalProps
        }

        try {
            DefaultGenerator()
                .opts(config.toClientOptInput())
                .generate()
        } catch (e: IllegalStateException) {
            Assert.assertNotNull(e.message)
            Assert.assertTrue(e.message!!.matches(msgRegex))
        }
    }

    private companion object {
        const val TARGET_PACKAGE = "ru.yandex.taxi.swagger.test"
        const val FEATURE_PACKAGE = "feature"

        val additionalProps = mapOf(
            "invokerPackage" to TARGET_PACKAGE,
            "apiPackage" to "$TARGET_PACKAGE.$FEATURE_PACKAGE.api",
            "skippedQueryParams" to "park_id",
            "skippedHeaderParams" to "Accept-Language",
            "enumPropertyNaming" to "UPPERCASE"
        )
    }
}