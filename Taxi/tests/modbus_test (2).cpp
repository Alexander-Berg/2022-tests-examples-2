#include "loveka/components/modbus/crc16ansi.hpp"
#include "loveka/components/modbus/packet.hpp"
#include "loveka/components/modbus/protocol_handler.hpp"
#include "loveka/components/utils/circular_buffer.hpp"

#include <gtest/gtest.h>

using namespace loveka::components::modbus;

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

struct noise_frame {
    static inline header_ext header = {'N', 'O'};
    uint16_t data;
};

struct adc_frame {
    static inline header_ext header = {'L', 'N'};
    uint16_t data[11];
};

struct rm_frame {
    static inline header_ext header = {'R', 'F'};
    uint16_t data[8];
    bool     stale;
    bool     lost;
    bool     fail_safe;
};

struct head_frame {
    static inline header_ext header = {'H', 'D'};
    int32_t data[3];
};

struct pwm_frame {
    static inline header_ext header = {'P', 'W'};
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
    adc_frame  adf  = {};
    rm_frame   rff  = {};
    head_frame head = {};
    pwm_frame  pwm  = {};

    packet<header_ext, counter, adc_frame, crc16ansi> pack_adc(adc_frame::header, cnt, adf);
    const std::size_t                                 sz1
        = sizeof(header_ext) + sizeof(cnt) + sizeof(adc_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz1, pack_adc.size());
    EXPECT_EQ(sz1, pack_adc.to_array().size());

    packet<header_ext, counter, rm_frame, crc16ansi> pack_rff(rm_frame::header, cnt, rff);
    const std::size_t sz2 = sizeof(header_ext) + sizeof(cnt) + sizeof(rm_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz2, pack_rff.size());
    EXPECT_EQ(sz2, pack_rff.to_array().size());

    packet<header_ext, counter, head_frame, crc16ansi> pack_head(head_frame::header, cnt, head);
    const std::size_t                                  sz3
        = sizeof(header_ext) + sizeof(cnt) + sizeof(head_frame) + sizeof(crc16ansi);
    EXPECT_EQ(sz3, pack_head.size());
    EXPECT_EQ(sz3, pack_head.to_array().size());

    packet<header_ext, counter, pwm_frame, crc16ansi> pack_pwm(pwm_frame::header, cnt, pwm);
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
    write_blocking(const uint8_t* data, std::size_t length) override
    {}

    virtual void
    write_non_blocking(uint8_t data)
    {}

    void
    write_non_blocking(const uint8_t* data, std::size_t length) override
    {}

    void
    read_blocking(std::size_t length)
    {}

    void
    read_non_blocking() override
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
    explicit constexpr multi_frame_handler()
        : protocol_handler_multi<Queue, RXBuffer, TXBuffer, header_ext, counter, crc16ansi,
                                 adc_frame, rm_frame>()
    {}

    void
    write_blocking(uint8_t data)
    {}

    void
    write_blocking(const uint8_t* data, std::size_t length) override
    {}

    virtual void
    write_non_blocking(uint8_t data)
    {}

    void
    write_non_blocking(const uint8_t* data, std::size_t length) override
    {}

    void
    read_blocking(std::size_t length)
    {}

    void
    read_non_blocking() override
    {}
};

TEST(modbus_test, protocol_handler_multi)
{
    counter                            cnt     = {0};
    header_ext                         h1      = {'L', 'N'};
    header_ext                         h2      = {'R', 'F'};
    adc_frame                          adf     = {};
    rm_frame                           rff     = {};
    multi_frame_handler<5, 1024, 1024> handler{};

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

using namespace loveka::components::utils;

class test_observer_adc : public observer<std::variant<adc_frame, rm_frame>> {
private:
    int i = 0;

public:
    void
    data(observable<std::variant<adc_frame, rm_frame>>& src, std::variant<adc_frame, rm_frame>& nd) override
    {
        i = 1;
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
    multi_frame_handler<5, 1024, 1024> handler{};
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
    multi_frame_handler<5, 1024, 1024> handler{};

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
    multi_frame_handler<5, 1024, 1024> handler{};
    handler.parse();
    EXPECT_EQ(1, 1);
}

template <std::size_t Queue, std::size_t RXBuffer, std::size_t TXBuffer>
class multi_frame_handler_test : public protocol_handler_multi<Queue, RXBuffer, TXBuffer, header_ext,
                              counter, crc16ansi, adc_frame, rm_frame, head_frame, pwm_frame> {
public:
    explicit constexpr multi_frame_handler_test()
        : protocol_handler_multi<Queue, RXBuffer, TXBuffer, header_ext, counter, crc16ansi,
                                 adc_frame, rm_frame, head_frame, pwm_frame>()
    {}

    void
    write_blocking(uint8_t data)
    {}

    void
    write_blocking(const uint8_t* data, std::size_t length) override
    {}

    virtual void
    write_non_blocking(uint8_t data)
    {}

    void
    write_non_blocking(const uint8_t* data, std::size_t length) override
    {
        loveka::components::usart_base<RXBuffer, TXBuffer>::push_read(data, length);
        loveka::components::usart_base<RXBuffer, TXBuffer>::write_finished();
    }

    void
    read_blocking(std::size_t length)
    {}

    void
    read_non_blocking() override
    {}
};

TEST(modbus_test, protocol_handler_multi_parser)
{
    pwm_frame pf{1, 2, 3, 4};
    adc_frame af{4, 5, 6, 7, 8, 4, 5, 67, 5, 3, 4};
    head_frame hf{1, -2, 3};
    rm_frame rm{1, 2, 3, 4, 4, 3, 2, 1, true, false, true};
    class receiver_data : public observer<std::variant<adc_frame, rm_frame, head_frame, pwm_frame>> {
        using data_type = std::variant<adc_frame, rm_frame, head_frame, pwm_frame>;

        adc_frame af_;
        rm_frame rf_;
        head_frame hf_;
        pwm_frame pf_;

        void
        data(observable<data_type>& src, data_type& nd) override
        {
            switch (nd.index()) {
            case 0: {
                auto af = std::get<0>(nd);
                for(int it=0;it < 11;it++) {
                    EXPECT_EQ(af.data[it], af_.data[it]);
                }
                i++;
            }
                break;
            case 1: {
                auto rf = std::get<1>(nd);
                for(int it=0;it < 8;it++) {
                    EXPECT_EQ(rf.data[it], rf_.data[it]);
                }
                EXPECT_EQ(rf.fail_safe, rf_.fail_safe);
                EXPECT_EQ(rf.lost, rf_.lost);
                EXPECT_EQ(rf.stale, rf_.stale);
                i++;
            }
                break;
            case 2: {
                auto hf = std::get<2>(nd);
                for(int it=0;it < 3;it++) {
                    EXPECT_EQ(hf.data[it], hf_.data[it]);
                }
                i++;
            }
                break;
            case 3: {
                auto pf = std::get<3>(nd);
                for(int it=0;it < 4;it++) {
                    EXPECT_EQ(pf.data[it], pf_.data[it]);
                }
                i++;
            }
                break;
            default:
                break;
            }
        }

    public:
        int i = 0;
        receiver_data(adc_frame &af, rm_frame &rf, head_frame &hf, pwm_frame &pf)
            : af_{af}, rf_{rf}, hf_{hf}, pf_{pf}
        {

        }
    } receiver_obs{af, rm, hf, pf};
    multi_frame_handler_test<5, 1024, 1024> receiver{};
    receiver.add_observer(receiver_obs);
    receiver.send_packet(af);
    receiver.send_packet(noise_frame{543});
    receiver.send_packet(rm);
    receiver.send_packet(noise_frame{543});
    receiver.send_packet(hf);
    receiver.send_packet(noise_frame{543});
    receiver.send_packet(pf);
    receiver.parse();
    receiver.parse();
    receiver.parse();
    receiver.parse();
    EXPECT_EQ(receiver_obs.i, 4);
}
