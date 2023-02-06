pluginManagement {
    includeBuild("../")
}

arrayOf("swagger-kotlin-codegen", "swagger-http-client")
    .forEach { project ->
        include(":$project")
        project(":$project").projectDir = File(rootProject.projectDir.parentFile, project)
    }