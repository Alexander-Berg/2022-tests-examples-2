from settings.settings import logger, tracker
from init_bot import dp, bot

async def check_files(message):
    file_info = None
    attach = []
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        logger.info(file_info)
    if message.document:
        file_info = await bot.get_file(message.document.file_id)
        logger.info(file_info)
    if message.video:
        file_info = await bot.get_file(message.video.file_id)
        logger.info(file_info)
    if file_info:
        file = await bot.download_file(file_info.file_path)
        logger.info(file)
        attach = tracker.upload_temp_attach({'file': ('file', file)}, 'bot_file')
        logger.info(f'attach {attach}')
        return attach['id']
    else:
        return None
