import React from 'react';

import { Story } from '@storybook/react';
import { CoinsIcon, FamilyCardIcon, PayServiceIcon, PlusGradientIcon } from '@yandex-id/icons';

import { Shortcut } from '../../index';

export const Common: Story = (args) => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      <Shortcut
        variant="plus"
        text="Как копить и тратить"
        label="Баллы Плюса"
        labelBold
        amount="37"
        amountIcon={<PlusGradientIcon />}
        size="s"
        {...args}
      />
      <Shortcut
        size="s"
        variant="edadeal"
        text="Найти товары с кешбэком"
        label="Кешбэк"
        labelBold
        amount="1205"
        amountIcon={<CoinsIcon />}
        currency="₽"
        {...args}
      />
      <Shortcut
        size="l"
        variant="plus"
        buttonText="Подключить"
        text="Фильмы, музыка и кешбэк баллами"
        label="Баллы Плюса"
        textBold
        withImage
        {...args}
      />
      <Shortcut
        size="l"
        variant="edadeal"
        buttonText="Хочу кешбэк"
        label="Мои чеки"
        text="Кешбэк за покупки в магазинах"
        textBold
        withImage
        {...args}
      />
      <Shortcut
        size="l"
        variant="family"
        buttonText="Выбрать карту"
        label="Семейная оплата"
        text="Поделитесь картой с близкими"
        textBold
        withImage
        {...args}
      />
      <Shortcut
        size="s"
        variant="family"
        label="Для близких"
        text="Семейная оплата"
        textBold
        icon={<FamilyCardIcon />}
        {...args}
      />
      <Shortcut
        size="s"
        variant="pay"
        label="Знакомтесь"
        text="Оплаты с Yandex Pay"
        textBold
        icon={<PayServiceIcon />}
        {...args}
      />
    </div>
  );
};
