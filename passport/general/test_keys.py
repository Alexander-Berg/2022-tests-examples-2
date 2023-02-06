# coding: utf-8
from passport.backend.oauth.tvm_api.tvm_keygen import (
    generate_rw_keys,
    parse_key,
)
import pytest


def test_generator():
    public, private = generate_rw_keys(2048)
    parse_key(public, private)

    with pytest.raises(RuntimeError):
        parse_key(public, "private")
    with pytest.raises(RuntimeError):
        parse_key("public", private)
    with pytest.raises(RuntimeError):
        parse_key(private, public)
    with pytest.raises(RuntimeError):
        parse_key(private, private)
