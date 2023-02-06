import React from 'react';
import { useTranslation } from 'react-i18next';

import User from '../../../../components-new/icon/images/user';

const StartPage = () => {
  const { t } = useTranslation();

  return (
    <div className="graph-chat-start-page">
      <User />
      <span className="graph-chat-start-page__text">
        {t('GRAPH.TESTING_CHAT.EMPTY_SCREEN')}
      </span>
    </div>
  );
};

export default StartPage;