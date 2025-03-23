
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <cstdint>

#include <iostream>

namespace py = pybind11;

using Idx_t = uint32_t;
//start,end,profif
using Interval = std::tuple<Idx_t,Idx_t,float>;

struct CompMemo {
    Idx_t comp;
    float memo;
};

inline Idx_t get_start(const Interval& i)  { return std::get<0>(i); }
inline Idx_t get_end(const Interval& i)    { return std::get<1>(i); }
inline float get_profit(const Interval& i) { return std::get<2>(i); }

Idx_t find_latest_compatible(Idx_t n, const std::vector<Interval>& intervals) 
{
    Idx_t res {0};
    for (Idx_t i = n-1; i > 0; --i) {
        if (get_end(intervals[i]) <= get_start(intervals[n])) {
            res = i;
            break;
        }
    }
    return res;
}

void fill_tables(const std::vector<Interval>& intervals, std::vector<CompMemo>& comp_memo)
{
    const auto n_intervals = comp_memo.size();
    for (Idx_t idx = 1; idx < n_intervals; ++idx) {
        const auto idx_latest_compatible = find_latest_compatible(idx,intervals);
        const auto memo = std::max(get_profit(intervals[idx]) + comp_memo[idx_latest_compatible].memo, comp_memo[idx-1].memo);
        comp_memo[idx] = {idx_latest_compatible,memo};
    }
}

std::vector<uint32_t> find_solution(const std::vector<Interval>& intervals, const std::vector<CompMemo>& comp_memo) 
{
    std::vector<uint32_t> selected_intervals;
    Idx_t n = comp_memo.size()-1;
    while (n) {
        const auto idx_latest_compatible = comp_memo[n].comp;
        if (get_profit(intervals[n]) + comp_memo[idx_latest_compatible].memo > comp_memo[n-1].memo) {
            selected_intervals.push_back(n);
            n = idx_latest_compatible;
        } else {
            --n;
        }
    }
    return selected_intervals;
}

std::vector<Idx_t> find_optimal_trading_points(std::vector<std::tuple<Idx_t,Idx_t,float>>& intervals)
{
    std::vector<CompMemo> comp_memo(intervals.size());
    fill_tables(intervals, comp_memo);
    return find_solution(intervals, comp_memo);
}

using TradingPoint = std::tuple<Idx_t,Idx_t,float>;

inline Idx_t get_idx  (const TradingPoint& i) { return std::get<0>(i); }
inline Idx_t get_type (const TradingPoint& i) { return std::get<1>(i); }
inline float get_price(const TradingPoint& i) { return std::get<2>(i); }

constexpr Idx_t buy_marker  = 0;
constexpr Idx_t sell_marker = 1;

std::vector<std::tuple<Idx_t,Idx_t,float>> generate_intervals(std::vector<TradingPoint>& trading_points, float initial_cash, float spread, float min_profit)
{
    // input   idx, type{0:buy,1:sell}, price
    // output stat,  end, profit

    uint32_t n_buy_points {0}, n_sell_points {0};

    for (const auto & tp : trading_points) {
        if (buy_marker== get_type(tp)) ++n_buy_points;
        else if (sell_marker== get_type(tp)) ++n_sell_points;
    }

    std::vector<Interval> intervals;
    intervals.reserve(n_buy_points * n_sell_points);
    float cash = initial_cash;
    for (Idx_t buy_idx = 0; buy_idx < trading_points.size(); ++buy_idx) {
        const auto & buy_point = trading_points[buy_idx];
        const auto buy_price  = get_price(buy_point);
        if (buy_marker == get_type(buy_point)) {
            for (Idx_t sell_idx = buy_idx + 1; sell_idx < trading_points.size(); ++sell_idx) {
                if (sell_marker == get_type(trading_points[sell_idx])) {
                    const auto & sell_point = trading_points[sell_idx];
                    const auto sell_price = get_price(sell_point);
                    uint32_t shares =  floor(cash / buy_price);
                    if (shares >= 1) {
                        const auto profit = (sell_price - buy_price - spread) * shares;
                        if (profit >= min_profit) {
                            intervals.emplace_back( get_idx(buy_point), get_idx(sell_point), profit );
                        }
                    }
                }
            }
        }
    }
    return intervals;
}

PYBIND11_MODULE(wis, m) {
    m.doc() = "find_optimal_trading_points using weighted interval scheduling";
    m.def("find_optimal_trading_points", &find_optimal_trading_points, "Process array of (int, int, float) -> array of int");
    m.def("generate_intervals",&generate_intervals,"Generate valid (buy idx, sell idx, profit) intervals");
}