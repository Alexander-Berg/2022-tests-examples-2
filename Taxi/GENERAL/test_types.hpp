#pragma once

// This is a header to test serialization internals. Ignore it!

#include <userver/formats/json/string_builder_fwd.hpp>
#include <userver/formats/serialize/to.hpp>
#include <userver/formats/serialize/write_to_stream.hpp>

namespace lib_sample {

struct TestTypes {};

template <class Value>
Value Serialize(const TestTypes&, ::formats::serialize::To<Value>) {}

template <class Builder>
void WriteToStream(const TestTypes&, Builder&) {}

}  // namespace lib_sample

namespace formats::serialize::impl {

// How it works:
//   1) This header is used from docs/yaml/defininitions.yaml of this library
//   2) userver-sample uses schema of this library
//   3) This header is included in definitions.hpp of the userver-sample
//   4) kIsSerializeAllowedInWriteToStream used inside WriteToStream to assert
//   that the only SAX serializars are allowed
template <typename Value>
constexpr inline bool
    kIsSerializeAllowedInWriteToStream<Value, formats::json::StringBuilder> =
        false;

}  // namespace formats::serialize::impl
