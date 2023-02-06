import React from 'react';

import { YandexAppPromo } from '.';
import { createClientRender } from '../../libs/testing';

describe('YandexAppPromo', () => {
  const render = createClientRender();

  test('baseline snapshot', () => {
    const result = render(
      <YandexAppPromo
        lang="ru"
        title="Блабла"
        installMessage="asdasd"
        description="dasdasd"
        usrImg=""
      />,
    );

    expect(result.asFragment()).toMatchSnapshot();
  });
});
