from settings.settings import logger, tracker

async def send_message(message, file=None):
    try:
        description = message.text if message.text else message.caption
        query = f'Queue: DVCORPBOT "Park Db ID": "{str(message.chat.id)}" "Sort by": Key'
        tickets = tracker.search_issues(query)
        logger.info(tickets)
        if tickets:
            key = tickets[-1]['key']
            if file:
                file_data = {
                    "attachmentIds": [file]
                }
                update_ticket_files = tracker.update_issue(data=file_data, issue_id=key)
                logger.info(f'update_ticket_files {update_ticket_files}')
                data = {
                    "text": f"\nКлиент приложил файл в первое сообщение\nСообщение от клиента:\n{description}",
                }
            else:
                data = {
                    "text": f"Сообщение от клиента:\n{str(description)}",
                }
            tracker.post_issue_comment(key, data=data)
            return key
        else:
            logger.error('Нет подходящего тикета для отправки сообщения')
            await message.answer("Пожалуйста, отправьте свой ответ в новом обращении, выбрав нужный раздел в боте.")
    except Exception as e:
        logger.error(f'send_message {e}')
