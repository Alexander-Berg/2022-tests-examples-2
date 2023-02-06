#include <views/v1/client_cache_projection/test/get/view.hpp>

#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>

namespace handlers::v1_client_cache_projection_test::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  auto cached = dependencies.projected_cache;

  LOG_DEBUG() << "items size : " << cached->Size();
  UASSERT(cached->Size() == 2);

  auto example1 = cached->Fetch("example_1");
  UASSERT(example1->example_id == "example_1");
  UASSERT(*example1->example_main_field == "example_1_main_field");
  UASSERT(example1->example_object_array_field->size() == 3);
  UASSERT(bool(example1->example_object_array_field->at(0).obj_int_field));
  UASSERT(bool(*example1->example_object_type_field->bool_field));
  UASSERT(*example1->example_object_array_field->at(0).obj_int_field == 5);
  UASSERT(!bool(example1->example_object_array_field->at(1).obj_int_field));
  UASSERT(example1->example_object_array_field->at(2).obj_int_field == 6);

  auto example2 = cached->Fetch("example_2");
  UASSERT(example2->example_id == "example_2");
  UASSERT(*example2->example_main_field == "example_2_main_field");
  UASSERT(example2->example_object_array_field->size() == 3);
  UASSERT(example2->example_object_array_field->at(0).obj_int_field == 7);
  UASSERT(bool(*example2->example_object_type_field->bool_field));
  UASSERT(!bool(example2->example_object_array_field->at(1).obj_int_field));
  UASSERT(example2->example_object_array_field->at(2).obj_int_field == 8);

  return Response200{};
}

}  // namespace handlers::v1_client_cache_projection_test::get
