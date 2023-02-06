/* dependencies_schema.ipp must not be included from anywhere
 * except main.cpp
 */

#include <custom/dependencies.hpp>

// TODO: move to main.cpp.jinja
#include <handlers/v1/run/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::v1_run::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/handler/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::handler::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;

// TODO: move to main.cpp.jinja
#include <handlers/openapi/v1/run/post/handler.hpp>

template <>
inline constexpr bool
    components::kHasValidate<::handlers::openapi_v1_run::post::Handler> =
        codegen::impl::kIsHandlerSchemaReady<::custom::Dependencies>;
