import React, { FC, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';

import * as action from '../../../../redux/graphChat/actions';
import Button from '../../../../components-new/button';

const ChatDisabledMessage: FC<{}> = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const handleUpdateChat = useCallback(
    () => {
      dispatch(action.updateChatOnGraphEdit());
    },
    [dispatch]
  );

  return (
    <div className="graph-chat-disabled-message">
      <span>{t('GRAPH.TESTING_CHAT.DISABLED_MESSAGE')}</span>
      <Button
        primary
        blank={false}
        size="large"
        onClick={handleUpdateChat}
      >
        {t('GRAPH.TESTING_CHAT.DISABLED_MESSAGE_RESET')}
      </Button>
    </div>
  )
};

export default ChatDisabledMessage;