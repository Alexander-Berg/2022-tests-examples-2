#include "loveka/common/modbus/crc16ansi.hpp"
#include "loveka/common/modbus/packet.hpp"
#include "loveka/common/modbus/protocol_handler.hpp"
#include "loveka/common/models/circular_buffer.hpp"

#include <gtest/gtest.h>

using namespace loveka::common::modbus;

TEST(modbus_test, crc16ansi)
{
    std::array<std::uint8_t, 5> data = {1, 2, 3, 4, 5};
    crc16ansi                   crc(data);
    std::uint16_t               value = crc.value();
    EXPECT_EQ(value, 47914);

    crc.calculate<5>({1, 2, 3, 4, 5});
    std::uint16_t value2 = crc.value();
    EXPECT_EQ(value, value2);
}

struct header_ext {
    uint8_t magic_header[2];
};

struct adc_frame {
    uint16_t data[11];
};

struct rm_frame {
    uint16_t data[8];
    bool     stale;
    bool     lost;
    bool     fail_safe;
};

struct head_frame {
    int32_t data[3];
};

struct pwm_frame {
    int32_t data[4];
};

struct counter {
    uint16_t cnt = 0;
    void
    operator++(int)
    {
        cnt++;
    }
};

TEST(modbus_test, packet)
{
    counter    cnt  = {0};
    header_ext h1   = {'L', 'N'};
    header_ext h2   = {'R', 'F'};
    header_ext h3   = {'H', 'D'};
    header_ext h4   = {'P', 'W'};
    adc_frame  adf  = {};
    rm_frame   rff  = {};
    head_frame head = {};
    pwm_frame  pwm  = {};

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(h1, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    packet<header_ext, counter, rm_frame, crc16ansi> pack_rff(h2, cnt, rff);
    const std::size_t sz2 = sizeof(header_ext) + sizeof(cnt) + sizeof(rm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz2, pack_rff.size());
    EXPECT_EQ(sz2, pack_rff.to_array().size());

    packet<header_ext, counter, head_frame, crc16ansi> pack_head(h3, cnt, head);
    const std::size_t                                  sz3
        = sizeof(header_ext) + sizeof(cnt) + sizeof(head_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz3, pack_head.size());
    EXPECT_EQ(sz3, pack_head.to_array().size());

    packet<header_ext, counter, pwm_frame, crc16ansi> pack_pwm(h4, cnt, pwm);
    const std::size_t                                 sz4
        = sizeof(header_ext) + sizeof(cnt) + sizeof(pwm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz4, pack_pwm.size());
    EXPECT_EQ(sz4, pack_pwm.to_array().size());
}

template <std::size_t Queue, std::size_t RXBuffer, std::size_t TXBuffer>
class adc_frame_handler : public protocol_handler<header_ext, counter, adc_frame, crc16ansi, Queue,
                                                  RXBuffer, TXBuffer> {

    void
    write_blocking(uint8_t data)
    {}

    void
    write_blocking(const uint8_t* data, std::size_t length)
    {}

    virtual void
    write_non_blocking(uint8_t data)
    {}

    void
    write_non_blocking(const uint8_t* data, std::size_t length)
    {}

    void
    read_blocking(std::size_t length)
    {}

    void
    read_non_blocking()
    {}
};

TEST(modbus_test, protocol_handler_one)
{
    counter                          cnt = {0};
    header_ext                       h1  = {'L', 'N'};
    adc_frame                        adf = {};
    adc_frame_handler<5, 1024, 1024> adf_handler;

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(h1, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    const char* test_noise = "12345";
    adf_handler.push_read(reinterpret_cast<const uint8_t*>(test_noise), strlen(test_noise));
    adf_handler.push_read(pack_adc.to_array().begin(), pack_adc.to_array().size());
    adf_handler.receive(h1);
    EXPECT_EQ(1, adf_handler.size());
}

template <std::size_t Queue, std::size_t RXBuffer, std::size_t TXBuffer>
class multi_frame_handler : public protocol_handler_multi<Queue, RXBuffer, TXBuffer, header_ext,
                                                          counter, crc16ansi, adc_frame, rm_frame> {
public:
    explicit constexpr multi_frame_handler(std::array<header_ext, 2> const& headers)
        : protocol_handler_multi<Queue, RXBuffer, TXBuffer, header_ext, counter, crc16ansi,
                                 adc_frame, rm_frame>(headers)
    {}

    void
    write_blocking(uint8_t data)
    {}

    void
    write_blocking(const uint8_t* data, std::size_t length)
    {}

    virtual void
    write_non_blocking(uint8_t data)
    {}

    void
    write_non_blocking(const uint8_t* data, std::size_t length)
    {}

    void
    read_blocking(std::size_t length)
    {}

    void
    read_non_blocking()
    {}
};

TEST(modbus_test, protocol_handler_multi)
{
    counter                            cnt     = {0};
    header_ext                         h1      = {'L', 'N'};
    header_ext                         h2      = {'R', 'F'};
    adc_frame                          adf     = {};
    rm_frame                           rff     = {};
    std::array<header_ext, 2>          headers = {h1, h2};
    multi_frame_handler<5, 1024, 1024> handler{headers};

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(h1, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    packet<header_ext, counter, rm_frame, crc16ansi> pack_rf(h2, cnt, rff);
    const std::size_t sz2 = sizeof(header_ext) + sizeof(cnt) + sizeof(rm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz2, pack_rf.size());
    EXPECT_EQ(sz2, pack_rf.to_array().size());

    const char* test_noise = "12345";
    handler.push_read(reinterpret_cast<const uint8_t*>(test_noise), strlen(test_noise));
    handler.push_read(pack_adc.to_array().begin(), pack_adc.to_array().size());
    handler.push_read(pack_rf.to_array().begin(), pack_rf.to_array().size());
    handler.push_read(reinterpret_cast<const uint8_t*>(test_noise), strlen(test_noise));
    handler.push_read(pack_rf.to_array().begin(), pack_rf.to_array().size());
    handler.parse();
    EXPECT_EQ(3, (handler.size()));
    auto msg = handler.pop_msg();
}

using namespace loveka::common::models;

class test_observer_adc : public observer<std::variant<adc_frame, rm_frame>, 1> {
private:
    int i = 0;

public:
    void
    data(observable<std::variant<adc_frame, rm_frame>, 1>& src,
         std::array<std::variant<adc_frame, rm_frame>, 1>& nd)
    {
        i = 1;
    }

    void
    state_change(observable<std::variant<adc_frame, rm_frame>, 1>& src, state& state_new)
    {
        i = 2;
    }

    void
    disconnect(observable<std::variant<adc_frame, rm_frame>, 1>& src)
    {
        i = 3;
    }

    int
    get()
    {
        return i;
    }
};

TEST(modbus_test, protocol_handler_multi_observe)
{
    counter                            cnt     = {0};
    header_ext                         h1      = {'L', 'N'};
    header_ext                         h2      = {'R', 'F'};
    adc_frame                          adf     = {};
    rm_frame                           rff     = {};
    std::array<header_ext, 2>          headers = {h1, h2};
    multi_frame_handler<5, 1024, 1024> handler{headers};
    test_observer_adc                  obs1;

    handler.add_observer(obs1);

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(h1, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    packet<header_ext, counter, rm_frame, crc16ansi> pack_rf(h2, cnt, rff);
    const std::size_t sz2 = sizeof(header_ext) + sizeof(cnt) + sizeof(rm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz2, pack_rf.size());
    EXPECT_EQ(sz2, pack_rf.to_array().size());

    const char* test_noise = "12345";
    handler.push_read(reinterpret_cast<const uint8_t*>(test_noise), strlen(test_noise));
    handler.push_read(pack_adc.to_array().begin(), pack_adc.to_array().size());
    handler.push_read(pack_rf.to_array().begin(), pack_rf.to_array().size());
    handler.push_read(reinterpret_cast<const uint8_t*>(test_noise), strlen(test_noise));
    handler.push_read(pack_rf.to_array().begin(), pack_rf.to_array().size());
    handler.parse();
    EXPECT_EQ(1, obs1.get());
}

TEST(modbus_test, protocol_handler_multi_send)
{
    counter                            cnt     = {0};
    header_ext                         h1      = {'L', 'N'};
    header_ext                         h2      = {'R', 'F'};
    adc_frame                          adf     = {};
    rm_frame                           rff     = {};
    std::array<header_ext, 2>          headers = {h1, h2};
    multi_frame_handler<5, 1024, 1024> handler{headers};

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(h1, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    packet<header_ext, counter, rm_frame, crc16ansi> pack_rf(h2, cnt, rff);
    const std::size_t sz2 = sizeof(header_ext) + sizeof(cnt) + sizeof(rm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz2, pack_rf.size());
    EXPECT_EQ(sz2, pack_rf.to_array().size());

    auto arr = pack_adc.to_array();
    handler.send(adf);
}

TEST(modbus_test, protocol_handler_multi_variant)
{
    header_ext                         h1      = {'L', 'N'};
    header_ext                         h2      = {'R', 'F'};
    std::array<header_ext, 2>          headers = {h1, h2};
    multi_frame_handler<5, 1024, 1024> handler{headers};

    std::variant<adc_frame, rm_frame> var;
    handler.parse();
    EXPECT_EQ(1, 1);
}
