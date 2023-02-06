#pragma once

#include <smart_devices/libs/segment_clock_leds/sc_led_controller.h>

#include <yandex_io/modules/leds/led_manager/ng/animation.h>

#include <chrono>
#include <memory>

class ClockTestAnimation: public Animation {
public:
    explicit ClockTestAnimation(std::weak_ptr<ScLedController> clockLedController, bool infinite = false);
    void drawCurrentFrame() override;
    bool finished() const override;
    TimePoint getEndOfFrameTimePoint() const override;
    std::string getName() const override;
    void resetAnimation() override;
    void updateTime(TimePoint timePoint) override;
    void startAnimationFrom(TimePoint timePoint) override;
    std::chrono::nanoseconds getLength() const override;

private:
    void updateBrightness();

private:
    std::weak_ptr<ScLedController> clockLedController_;
    std::chrono::time_point<std::chrono::steady_clock> endOfFrame_;
    int currentBrightness_ = ScLedFrame::brightnessOn;
    int counter_ = 0;
    bool infinite_;
    bool started_ = false;
};
