from telegram.error import BadRequest


async def safe_edit(query, text, reply_markup=None):
    """edit_message_text с игнором 'Message is not modified'."""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" in str(e):
            pass  # Игнорируем, если сообщение не изменилось
        else:
            raise e