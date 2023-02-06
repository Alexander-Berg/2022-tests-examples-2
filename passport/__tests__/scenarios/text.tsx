import React from 'react';

import { Story } from '@storybook/react';
import { StarOutline } from '@yandex/ui-icons';

import { TextButton } from '../../index';

export const Text: Story = () => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      <TextButton before={<StarOutline size={16} />}>Button</TextButton>
      <TextButton after={<StarOutline size={16} />}>Button</TextButton>
      <TextButton before={<StarOutline size={16} />} after={<StarOutline size={16} />}>
        Button
      </TextButton>
      <TextButton>
        <StarOutline size={16} />
      </TextButton>
    </div>
  );
};
