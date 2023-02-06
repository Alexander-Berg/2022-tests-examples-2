import logging

logger = logging.getLogger(__name__)


def dump_response(response):
    lines = [
        "",
        f"{response.status}",
        ""
    ]
    lines.extend([f"{k}: {v}" for k, v in response.headers])
    lines.append("")
    lines.append(response.get_data(as_text=True))

    logger.info("\n".join(lines))
