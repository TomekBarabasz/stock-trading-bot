#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <immintrin.h>
#include <sstream>
#include <algorithm>

struct PerfCounter
{
    double ticks_per_sec;
    PerfCounter()
    {
        ticks_per_sec = static_cast<double>(measure_ticks_per_sec());
    }
    std::string dt_to_string(uint64_t dt)
    {
        const auto dt_in_seconds = static_cast<double>(dt) / ticks_per_sec;
        const auto seconds = static_cast<uint64_t>(dt_in_seconds);
        const auto fraction = dt_in_seconds - seconds;
        const auto msec = static_cast<uint64_t>(fraction * 1000);
        const auto usec = static_cast<uint64_t>(fraction * 1000000) % 1000;
        std::ostringstream ss;
        if (seconds > 0) {
            ss << seconds << " s ";
        }
        ss << msec << " ms " << usec << " us";
        return ss.str();
    }
    static uint64_t measure_ticks_per_sec()
    {
        auto tm_start = timestamp();
        usleep(1000000);
        return timestamp() - tm_start;
    }
    static uint64_t timestamp() { return __rdtsc(); }
};

using Idx_t = uint32_t;
struct TradingPoint {
    Idx_t idx;
    Idx_t type;
    float price;
};

struct Interval {
    Idx_t start,end;
    float profit;
};

std::vector<TradingPoint> load_trading_points(const char* filename_)
{
    std::vector<TradingPoint> trading_points;
    std::string filename {filename_};

    if (filename.ends_with(".txt")) {
        std::cout << "not implemented" << std::endl;
    } else if (filename.ends_with(".bin")) {
        std::ifstream inp(filename.c_str(),std::ios::binary);
        uint32_t n_points;
        inp.read(reinterpret_cast<char*>(&n_points),sizeof(n_points));
        trading_points.resize(n_points);
        inp.read(reinterpret_cast<char*>(trading_points.data()), n_points*sizeof(TradingPoint));
    }
    return trading_points;
}

std::vector<Interval> generate_intervals(std::vector<TradingPoint>& trading_points, float initial_cash, float spread, float min_profit)
{
    std::vector<Interval> intervals;
    return intervals;
}

constexpr Idx_t buy_marker  = 0;
constexpr Idx_t sell_marker = 1;
void gen_1(const std::vector<TradingPoint>& trading_points)
{
    PerfCounter pc;
    uint32_t n_buy_points {0}, n_sell_points {0};

    const auto t0 = pc.timestamp();
    for (const auto & tp : trading_points) {
        if (0 == tp.type) ++n_buy_points;
        else ++n_sell_points;
    }
    std::cout << "calc buy,sell points " << n_buy_points << ',' << n_sell_points << " done in " << pc.dt_to_string(pc.timestamp() - t0) << std::endl;

    std::vector<Interval> intervals;
    intervals.reserve(n_buy_points * n_sell_points);

    for (Idx_t buy_idx = 0; buy_idx < trading_points.size(); ++buy_idx) {
        if (buy_marker == trading_points[buy_idx].type) {
            for (Idx_t sell_idx = buy_idx + 1; sell_idx < trading_points.size(); ++sell_idx) {
                if (sell_marker == trading_points[buy_idx].type) {
                    const auto buy_price  = get_price(trading_points[buy_idx]);
                    const auto sell_price = get_price(trading_points[sell_idx]);
                    shares =  np.floor(cash / buy_price)
                    if shares > 1:
                        profit = (sell_price - buy_price - spread) * shares
                        if profit > min_profit:
                            valid_intervals.append( (bi,si, profit) )
                }
            }
        }
    }
}
int main(int argc, const char** argv)
{
    if (argc < 2) {
        std::cout << "usage: intp filename_in" << std::endl;
        return 1;
    }
    std::vector<TradingPoint> trading_points = load_trading_points(argv[1]);
    std::cout << "loaded " << trading_points.size() << " trading points" << std::endl;
    int version_idx = argc >=3 ? std::stoi(argv[2]) : 1;
    switch (version_idx) {
        case 1:
            gen_1(trading_points);
            break;
        default:
            std::cout << "version not implemented" << std::endl;
    }
    
    return 0;
}
