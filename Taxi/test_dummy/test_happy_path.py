def test_component(library_context):
    assert library_context.dummy_component.get_parameters() is None
