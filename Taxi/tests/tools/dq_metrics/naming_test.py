import pytest
import sources_root


from dmp_suite.inspect_utils import find_objects
from dmp_suite.dq_metrics.query_builder import QueryBuilder


ALLOWED_MODULE_SUFFIXES = (
    "loader",
)


def module_filter(module_name, is_package):

    last_component = module_name.rsplit('.', 1)[-1]
    return is_package or last_component.endswith(ALLOWED_MODULE_SUFFIXES)


def get_query_builder_instances(etl_service):

    yield from find_objects(
            etl_service,
            filters=[lambda obj: isinstance(obj, QueryBuilder)],
            modules_filters=[module_filter],
            skip_import_errors=True,
            return_object_only=False,
    )


@pytest.mark.parametrize("etl_service", sources_root.ETL_SERVICES)
def test_query_builder_naming(etl_service):

    def build_msg(module_, errors, white_list_mask_patterns, black_list_mask_patterns):
        return f"""
            {module_} has QueryBuilder obj with incorrect metric_names: {errors},
            f"checked regex white_list patterns: {white_list_mask_patterns},
            f" checked regex black_list patterns: {black_list_mask_patterns}
            """

    errors_accumulated = []
    msg_accumulated = []

    for module_, _, query_builder in get_query_builder_instances(etl_service):
        metrics_names = query_builder.metrics_names_for_linter
        naming_rule = query_builder.naming_rule.value

        # note: проверяем, что имя соответствует белым-регекс-маскам
        white_list_operator = naming_rule.white_list_operator
        white_list_masks = naming_rule.white_list_masks
        white_list_mask_patterns = [mask.pattern for mask in white_list_masks]
        white_list_mask_matches = {name: [mask.match(name) for mask in white_list_masks] for name in metrics_names}
        errors = [name for name in white_list_mask_matches
                  if not white_list_operator(white_list_mask_matches[name])]

        # note: проверяем, что имя НЕ соответствует черным-регекс-маскам
        black_list_operator = naming_rule.black_list_operator
        black_list_masks = naming_rule.black_list_masks
        black_list_mask_patterns = [mask.pattern for mask in black_list_masks]
        black_list_mask_matches = {name: [mask.match(name) for mask in black_list_masks] for name in metrics_names}
        black_list_errors = [name for name in black_list_mask_matches
                             if black_list_operator(black_list_mask_matches[name])]

        errors.extend(black_list_errors)
        errors = sorted(set(errors))

        if errors:
            errors_accumulated.extend(errors)
            msg_parts = (module_, errors, white_list_mask_patterns, black_list_mask_patterns)
            msg_accumulated.append(msg_parts)

    assert not errors_accumulated, "".join([build_msg(*msg_parts) for msg_parts in msg_accumulated])
