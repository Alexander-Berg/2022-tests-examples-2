import block from 'bem-cn';
import moment from 'moment';
import React, { FC, memo, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import waiting from '../../../../assets/waiting.svg';

import './styles.scss';

type Props = {};

const b = block('testing-not-available-label');

const TestingNotAvailableLabel: FC<Props> = () => {
  const { t } = useTranslation();

  const date = useMemo(
    () => {
      const d = moment();
      // до пятницы обещаем начало след недели, если не успели - добавляем неделю
      const delta = d.day() < 5 ? 8 : 15;
      return d.day(delta).format('DD MMMM');
    },
    [],
  );

  return (
    <div className={b()}>
      <img
        className={b('image')}
        width={300}
        height={300}
        src={waiting}
        alt=""
      />
      {t('PAGE_ONLINE_DIALOG.NOT_AVAILABLE', { date }).split('\n').map((text, i) => (
        <span className={b('text')} key={i}>{text}</span>
      ))}
    </div>
  );
};

export default memo(TestingNotAvailableLabel);
