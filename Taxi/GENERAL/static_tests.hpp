#pragma once

/**
 * Misc instantiation tests
 */

#include <stm32pp/hal/memory.hpp>
#include <stm32pp/hal/peripherals.hpp>
#include <stm32pp/hal/timer.hpp>
#include <stm32pp/util/packed_structs.hpp>

#include <type_traits>

namespace stm32pp::util {

static_assert(detail::fields_per_storage_unit<std::uint32_t>(8_bit, 0_bit, 0_bit) == 4);
static_assert(detail::fields_per_storage_unit<std::uint32_t>(17_bit, 9_bit, 7_bit) == 2);

static_assert(detail::unit_count<std::uint32_t>(8_bit, 0_bit, 5_x, 0_bit, 0_bit) == 2);
static_assert(detail::unit_count<std::uint32_t>(17_bit, 9_bit, 2_x, 0_bit, 0_bit) == 1);
static_assert(detail::unit_count<std::uint32_t>(17_bit, 9_bit, 2_x, 7_bit, 0_bit) == 1);
static_assert(detail::unit_count<std::uint32_t>(17_bit, 9_bit, 4_x, 7_bit, 0_bit) == 2);

static_assert(bitmask<5_bit>::value == 0b11111);
static_assert(bitmask<4_bit, 1_bit>::value == 0b11110);

static_assert(sizeof(packed_structs<std::uint32_t, 8_bit, 3_x>) == sizeof(std::uint32_t));
static_assert(sizeof(packed_structs<std::uint32_t, 8_bit, 4_x, 16_bit>)
              == sizeof(std::uint32_t) * 2);
static_assert(sizeof(packed_structs<std::uint32_t, 16_bit, 3_x>) == sizeof(std::uint32_t) * 2);
static_assert(sizeof(packed_structs<std::uint32_t, 16_bit, 4_x>) == sizeof(std::uint32_t) * 2);

static_assert(
    std::is_same_v<decltype(packed_structs<std::uint32_t, 8_bit, 3_x>::base::raw), std::uint32_t>);
static_assert(packed_structs<std::uint32_t, 8_bit, 5_x>::base::unit_count == 2);
static_assert(std::is_same_v<decltype(packed_structs<std::uint32_t, 8_bit, 5_x>::base::raw),
                             std::uint32_t[2]>);
}    // namespace stm32pp::util

namespace stm32pp::hal {

namespace memory {

static_assert(memory_base_t<mcu_series::f031x6>::flash_base == 0x08000000UL);
static_assert(memory_base_t<mcu_series::f038xx>::flash_base == 0x08000000UL);

}    // namespace memory

static_assert(peripherals_t<mcu_series::f031x6>::tim2_base
              == memory::memory_base_t<mcu_series::f038xx>::apb_base);
static_assert(peripherals_t<mcu_series::f031x6>::i2c1_base
              == memory::memory_base_t<mcu_series::f038xx>::apb_base + 0x00005400UL);
static_assert(peripherals_t<mcu_series::f031x6>::adc_base
              == memory::memory_base_t<mcu_series::f038xx>::apb_base + 0x00012708UL);
static_assert(peripherals_t<mcu_series::f031x6>::usart1_base
              == memory::memory_base_t<mcu_series::f038xx>::apb_base + 0x00013800UL);
static_assert(peripherals_t<mcu_series::f031x6>::dbgmcu_base
              == memory::memory_base_t<mcu_series::f038xx>::apb_base + 0x00015800UL);

static_assert(peripherals_t<mcu_series::f031x6>::rcc_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb_base + 0x00001000UL);
static_assert(peripherals_t<mcu_series::f031x6>::flash_r_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb_base + 0x00002000UL);

static_assert(peripherals_t<mcu_series::f031x6>::flash_r_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb_base + 0x00002000UL);

static_assert(peripherals_t<mcu_series::f031x6>::gpioa_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb2_base);
static_assert(peripherals_t<mcu_series::f031x6>::gpiob_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb2_base + 0x00000400UL);
static_assert(peripherals_t<mcu_series::f031x6>::gpioc_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb2_base + 0x00000800UL);
static_assert(peripherals_t<mcu_series::f031x6>::gpiof_base
              == memory::memory_base_t<mcu_series::f038xx>::ahb2_base + 0x00001400UL);

namespace timer::traits {

using gpio::operator""_pin;

static_assert(channel_gpio_pin_count_v<mcu_series::f031x6, timers::tim1, timer_channel::ch1> == 1);
static_assert(channel_complementary_gpio_pin_count_v<mcu_series::f031x6, timers::tim1,
                                                     timer_channel::ch1> == 2);
static_assert(channel_complementary_gpio_pin_count_v<mcu_series::f031x6, timers::tim2,
                                                     timer_channel::ch1> == 0);

static_assert(channel_gpio_pin_count_v<mcu_series::h747, timers::tim1, timer_channel::ch1> == 3);

static_assert(
    channel_gpio_traits_t<mcu_series::h745, timers::tim1, timer_channel::ch1>::find_pin("PA8"_pin)
    == pin_alternative{0});

static_assert(
    channel_gpio_traits_t<mcu_series::h745, timers::tim1, timer_channel::ch1>::find_pin("PE9"_pin)
    == pin_alternative{1});

static_assert(
    channel_gpio_traits_t<mcu_series::h745, timers::tim1, timer_channel::ch1>::find_pin("PE10"_pin)
    == no_pin_alternative);

}    // namespace timer::traits

}    // namespace stm32pp::hal
