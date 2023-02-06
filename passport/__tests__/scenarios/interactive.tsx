import React from 'react';

import { Story } from '@storybook/react';

import { Shortcut } from '../../index';

export const Interactive: Story = (args) => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      <Shortcut
        size="l"
        data-testid="shortcut"
        buttonText="Выбрать карту"
        label="Семейная оплата"
        text="Поделитесь картой с близкими"
        textBold
        withImage
        {...args}
      />
    </div>
  );
};

Interactive.args = {
  variant: 'default',
  disabled: false,
};
