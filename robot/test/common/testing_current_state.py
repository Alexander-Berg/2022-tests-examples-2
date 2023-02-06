from os.path import join as pj


def set_testing_current_state(local_blrt, value):
    jupiter_meta_path = pj(local_blrt.yt_prefix, "@jupiter_meta")
    if not local_blrt.yt_client.exists(jupiter_meta_path):
        local_blrt.yt_client.set(jupiter_meta_path, {})
    local_blrt.yt_client.set(pj(jupiter_meta_path, "yandex_testing_current_state"), value)
