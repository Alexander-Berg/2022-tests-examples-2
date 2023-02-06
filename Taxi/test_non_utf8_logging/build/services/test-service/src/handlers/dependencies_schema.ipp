/* dependencies_schema.ipp must not be included from anywhere
 * except main.cpp
 */

#include <custom/dependencies.hpp>

// TODO: move to main.cpp.jinja
#include <handlers/swagger/flatbuffer/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::swagger_flatbuffer::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/swagger/flatbuffer-and-protobuffer/post/handler.hpp>

template <>
inline constexpr bool components::kHasValidate<
    ::handlers::swagger_flatbuffer_and_protobuffer::post::Handler> =
    codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/swagger/protobuffer/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::swagger_protobuffer::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/v1/run/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::v1_run::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/openapi/flatbuffer/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::openapi_flatbuffer::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/openapi/flatbuffer-and-protobuffer/post/handler.hpp>

template <>
inline constexpr bool components::kHasValidate<
    ::handlers::openapi_flatbuffer_and_protobuffer::post::Handler> =
    codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/openapi/protobuffer/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::openapi_protobuffer::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/openapi/v1/run/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::openapi_v1_run::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;
