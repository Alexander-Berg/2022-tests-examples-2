import React from 'react';

import { Story } from '@storybook/react';
import { StarOutline } from '@yandex/ui-icons';

import { Button } from '../../index';

export const Icons: Story = () => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      <Button before={<StarOutline size={16} />}>Button</Button>
      <Button after={<StarOutline size={16} />}>Button</Button>
      <Button before={<StarOutline size={16} />} after={<StarOutline size={16} />}>
        Button
      </Button>
      <Button>
        <StarOutline size={16} />
      </Button>
    </div>
  );
};
