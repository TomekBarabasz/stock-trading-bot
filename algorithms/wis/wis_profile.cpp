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

template< typename I, typename F>
struct Interval_t {
    I start,end;
    F profit;
};
using Idx_t = uint32_t;
using Profit_t = float;
using Interval = Interval_t<Idx_t,Profit_t>;

template <typename I, typename F>
struct CompMemo_t {
    I comp;
    F memo;
};
using CompMemo = CompMemo_t<Idx_t,Profit_t>;

std::vector<Interval> load_intervals(const char * filename_)
{
    std::vector<Interval> intervals;
    std::string filename {filename_};
    if (filename.ends_with(".txt")) {
        std::cout << "not implemented" << std::endl;
    } else if (filename.ends_with(".bin")) {
        std::ifstream inp(filename.c_str(),std::ios::binary);
        uint32_t n_intervals;
        inp.read(reinterpret_cast<char*>(&n_intervals),sizeof(n_intervals));
        intervals.resize(n_intervals);
        inp.read(reinterpret_cast<char*>(intervals.data()), n_intervals*sizeof(Interval));
    }
    return intervals;
}

std::vector<Interval> revert_intervals(const std::vector<Interval>& intervals)
{
    const auto n_intervals = intervals.size();
    std::vector<Interval> reverted(n_intervals);
    const auto offset = intervals.size() - 1;
    for (int i=0;i<n_intervals;++i) {
        reverted[i] = intervals[offset - i];
    }
    return reverted;
}

Idx_t find_latest_compatible_1(Idx_t n, const std::vector<Interval>& intervals) 
{
    Idx_t res {0};
    for (Idx_t i = n-1; i > 0; --i) {
        if (intervals[i].end <= intervals[n].start) {
            res = i;
            break;
        }
    }
    return res;
}

Idx_t find_latest_compatible_2(Idx_t n, const std::vector<Interval>& reverted) 
{
    const Idx_t offset {static_cast<Idx_t>(reverted.size()) - 1};
    const Idx_t n_offset {offset - n};
    for( Idx_t i = n_offset + 1; i < reverted.size(); ++i) {
        if (reverted[i].end <= reverted[n_offset].start) {
            return offset - i;
        }
    }
    return 0;
}

void fill_memo_table_1(const std::vector<Interval>& intervals, Profit_t* memo)
{
    for (Idx_t idx = 1; idx < intervals.size(); ++idx){
        memo[idx] = std::max(intervals[idx].profit + memo[find_latest_compatible_1(idx,intervals)], memo[idx-1]);
    }
}

void fill_memo_table_2(Profit_t* memo, const std::vector<Interval>& intervals, const std::vector<Interval>& reverted)
{
    for (Idx_t idx = 1; idx < intervals.size(); ++idx) {
        const auto idx_latest_compatible = find_latest_compatible_2(idx,reverted);
        memo[idx] = std::max(intervals[idx].profit + memo[idx_latest_compatible], memo[idx-1]);
    }
}

void fill_tables(const std::vector<Interval>& intervals, std::vector<CompMemo>& comp_memo)
{
    for (Idx_t idx = 1; idx < intervals.size(); ++idx) {
        const auto idx_latest_compatible = find_latest_compatible_1(idx,intervals);
        const auto memo = std::max(intervals[idx].profit + comp_memo[idx_latest_compatible].memo, comp_memo[idx-1].memo);
        comp_memo[idx] = {idx_latest_compatible,memo};
    }
}

std::vector<uint32_t> find_solution_1(const std::vector<Interval>& intervals, const Profit_t* memo) 
{
    std::vector<uint32_t> selected_intervals;
    Idx_t n = intervals.size()-1;
    while (n) {
        const auto idx_latest_compatible = find_latest_compatible_1(n,intervals);
        if (intervals[n].profit + memo[idx_latest_compatible] > memo[n-1]) {
            selected_intervals.push_back(n);
            n = idx_latest_compatible;
        } else {
            --n;
        }
    }
    return selected_intervals;
}

std::vector<uint32_t> find_solution_2(const std::vector<Interval>& intervals, const Profit_t* memo) 
{
    std::vector<uint32_t> selected_intervals;
    Idx_t n = intervals.size()-1;
    while (n) {
        const auto idx_latest_compatible = find_latest_compatible_2(n,intervals);
        if (intervals[n].profit + memo[idx_latest_compatible] > memo[n-1]) {
            selected_intervals.push_back(n);
            n = idx_latest_compatible;
        } else {
            --n;
        }
    }
    return selected_intervals;
}

std::vector<uint32_t> find_solution_3(const std::vector<Interval>& intervals, const std::vector<CompMemo>& comp_memo) 
{
    std::vector<uint32_t> selected_intervals;
    Idx_t n = intervals.size()-1;
    while (n) {
        const auto idx_latest_compatible = comp_memo[n].comp;
        if (intervals[n].profit + comp_memo[idx_latest_compatible].memo > comp_memo[n-1].memo) {
            selected_intervals.push_back(n);
            n = idx_latest_compatible;
        } else {
            --n;
        }
    }
    return selected_intervals;
}

void wis_1(const std::vector<Interval>& intervals)
{
    auto memo = std::make_unique<Profit_t[]>(intervals.size());
    PerfCounter pc;

    auto t0 = pc.timestamp();
    fill_memo_table_1(intervals, memo.get());
    auto t1 = pc.timestamp();
    auto selected_intervals = find_solution_1(intervals, memo.get());
    auto t2 = pc.timestamp();

    std::cout << "fill_memo_table done in " << pc.dt_to_string(t1 - t0) << std::endl;
    std::cout << "find_solution done in "   << pc.dt_to_string(t2 - t1) << std::endl;
    std::cout << "total exec time "         << pc.dt_to_string(t2 - t0) << std::endl;

    Profit_t total_profit {0};
    for (const auto idx : selected_intervals) {
        total_profit += intervals[idx].profit;
    }
    std::cout << "selected " << selected_intervals.size() << " intervals, total_profit = " << total_profit << std::endl;
}

void wis_2(const std::vector<Interval>& intervals)
{
    auto memo = std::make_unique<Profit_t[]>(intervals.size());
    PerfCounter pc;
    auto t00 = pc.timestamp();
    
    auto t0 = pc.timestamp();
    auto reverted = revert_intervals(intervals);
    std::cout << "revert_intervals done in " << pc.dt_to_string(pc.timestamp() - t0) << std::endl;

    t0 = pc.timestamp();
    fill_memo_table_2(memo.get(), intervals, reverted);
    std::cout << "fill_memo_table done in " << pc.dt_to_string(pc.timestamp() - t0) << std::endl;

    t0 = pc.timestamp();
    auto selected_intervals = find_solution_2(intervals, memo.get());
    std::cout << "find_solution done in " << pc.dt_to_string(pc.timestamp() - t0) << std::endl;

    Profit_t total_profit {0};
    for (const auto idx : selected_intervals) {
        total_profit += intervals[idx].profit;
    }
    std::cout << "selected " << selected_intervals.size() << " intervals, total_profit = " << total_profit << std::endl;
}

void wis_3(const std::vector<Interval>& intervals)
{
    std::vector<CompMemo> comp_memo(intervals.size());
    PerfCounter pc;
    
    auto t0 = pc.timestamp();
    fill_tables(intervals, comp_memo);
    auto t1 = pc.timestamp();
    auto selected_intervals = find_solution_3(intervals, comp_memo);
    auto t2 = pc.timestamp();

    std::cout << "fill_tables done in "   << pc.dt_to_string(t1 - t0) << std::endl;   
    std::cout << "find_solution done in " << pc.dt_to_string(t2 - t1) << std::endl;
    std::cout << "total exec time "       << pc.dt_to_string(t2 - t0) << std::endl;

    Profit_t total_profit {0};
    for (const auto idx : selected_intervals) {
        total_profit += intervals[idx].profit;
    }
    std::cout << "selected " << selected_intervals.size() << " intervals, total_profit = " << total_profit << std::endl;
}

int main(int argc, const char** argv)
{
    if (argc < 2) {
        std::cout << "usage: wis filename_in method:int" << std::endl;
        return 1;
    }
    std::vector<Interval> intervals = load_intervals(argv[1]);
    std::cout << "loaded " << intervals.size() << " intervals" << std::endl;
    int version_idx = std::stoi(argv[2]);
    switch (version_idx) {
        case 1:
            wis_1(intervals);
            break;
        case 2:
            wis_2(intervals);
            break;
        case 3:{
            wis_3(intervals);
            break;
        }
        default:
            std::cout << "version not implemented" << std::endl;
    }
    
    return 0;
}
