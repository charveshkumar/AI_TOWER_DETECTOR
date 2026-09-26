import React, { useState } from 'react';

export default function AnalyticsDashboard({ onSelectTower }) {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedRegion, setSelectedRegion] = useState('all');

  const fleetMetrics = {
    totalTowers: 1428,
    activeAnomalies: 34,
    fleetHealthScore: 89.4,
    avgScanAccuracy: 98.7,
    remediatedThisMonth: 18
  };

  const defectDistribution = [
    { name: 'Surface Corrosion', percentage: 46, count: 156, color: 'bg-rose-500', barColor: '#f43f5e' },
    { name: 'Missing Bolt / Fastener', percentage: 28, count: 95, color: 'bg-amber-500', barColor: '#f59e0b' },
    { name: 'Structural Micro-Crack', percentage: 16, count: 54, color: 'bg-indigo-500', barColor: '#6366f1' },
    { name: 'Antenna Mount Misalignment', percentage: 10, count: 34, color: 'bg-emerald-500', barColor: '#10b981' }
  ];

  const regionalAssets = [
    { id: 'TWR-408', region: 'North Sector A', type: 'Supporting Lattice', health: 74, status: 'Critical Action', anomalies: 3, lastScan: '2 hours ago' },
    { id: 'TWR-892', region: 'Central Metro', type: 'Monopole Tower', health: 91, status: 'Optimal', anomalies: 1, lastScan: 'Yesterday' },
    { id: 'TWR-102', region: 'Coastal Hub B', type: 'Guyed Mast', health: 68, status: 'High Priority', anomalies: 4, lastScan: '3 days ago' },
    { id: 'TWR-773', region: 'Highland Grid', type: 'Supporting Lattice', health: 95, status: 'Optimal', anomalies: 0, lastScan: '5 days ago' },
    { id: 'TWR-551', region: 'Industrial West', type: 'Self-Supporting', health: 82, status: 'Scheduled', anomalies: 2, lastScan: '1 week ago' },
    { id: 'TWR-309', region: 'South Gateway', type: 'Monopole Tower', health: 88, status: 'Operational', anomalies: 1, lastScan: '2 weeks ago' }
  ];

  const filteredAssets = regionalAssets.filter(item => {
    if (selectedRegion === 'all') return true;
    return item.region.toLowerCase().includes(selectedRegion.toLowerCase());
  });

  return (
    <div className="flex flex-col h-full w-full">
      {/* Header */}
      <header className="pt-8 pb-5 px-10 flex-shrink-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100/80 border border-emerald-300 text-emerald-800 text-[10px] font-bold tracking-wider uppercase">
              Predictive Telemetry
            </span>
            <span className="text-xs text-slate-500 font-medium">• Live Telecommunication Fleet Status</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Fleet Analytics & AI Prognostics</h1>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center gap-2">
          <div className="glass-card p-1 rounded-xl flex gap-1 text-xs font-semibold">
            {['7d', '30d', '90d', '1y'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  timeRange === range
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                }`}
              >
                {range.toUpperCase()}
              </button>
            ))}
          </div>

          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="glass-card px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none focus:border-emerald-500 cursor-pointer shadow-xs"
          >
            <option value="all">All Regional Sectors</option>
            <option value="North">North Sector</option>
            <option value="Central">Central Metro</option>
            <option value="Coastal">Coastal Hub</option>
            <option value="Industrial">Industrial West</option>
          </select>
        </div>
      </header>

      {/* Main Grid Content */}
      <div className="px-10 pb-10 flex-1 w-full max-w-7xl flex flex-col gap-6 overflow-y-auto">
        
        {/* KPI Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass-card rounded-2xl p-5 relative overflow-hidden group hover:border-emerald-400/50 transition-all">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Total Fleet Monitored</span>
              <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-base">
                <i className="ph-fill ph-broadcast"></i>
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 tracking-tight">{fleetMetrics.totalTowers}</div>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-semibold mt-2">
              <i className="ph-fill ph-trend-up"></i>
              <span>+12 towers onboarded this quarter</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-5 relative overflow-hidden group hover:border-emerald-400/50 transition-all">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Fleet Integrity Index</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-base">
                <i className="ph-fill ph-shield-check"></i>
              </div>
            </div>
            <div className="text-3xl font-black text-emerald-700 tracking-tight">{fleetMetrics.fleetHealthScore}%</div>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-semibold mt-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Overall Fleet Grade: A (Nominal)</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-5 relative overflow-hidden group hover:border-rose-400/50 transition-all">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Active Anomalies</span>
              <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center text-base">
                <i className="ph-fill ph-warning-octagon"></i>
              </div>
            </div>
            <div className="text-3xl font-black text-rose-600 tracking-tight">{fleetMetrics.activeAnomalies}</div>
            <div className="flex items-center gap-1.5 text-[11px] text-rose-700 font-semibold mt-2">
              <span>8 critical rust repairs in queue</span>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-5 relative overflow-hidden group hover:border-emerald-400/50 transition-all">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Vision Model Accuracy</span>
              <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-base">
                <i className="ph-fill ph-cpu"></i>
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 tracking-tight">{fleetMetrics.avgScanAccuracy}%</div>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-semibold mt-2">
              <i className="ph-fill ph-sparkle text-amber-500"></i>
              <span>YOLO-Structural v8.4 Engine</span>
            </div>
          </div>
        </div>

        {/* Charts & Distribution Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Anomaly Breakdown Chart Card */}
          <div className="lg:col-span-6 glass-card rounded-3xl p-6 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Detected Anomaly Distribution</h3>
                  <p className="text-xs text-slate-500 font-medium">Breakdown across 339 verified structural defects</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-white/70 border border-slate-200 text-slate-700 text-xs font-bold">
                  AI Classified
                </span>
              </div>

              {/* Progress Distribution Bars */}
              <div className="space-y-4 my-4">
                {defectDistribution.map((item, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-800 flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full ${item.color}`}></span>
                        {item.name}
                      </span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-500 text-[11px]">{item.count} sites</span>
                        <span className="font-bold text-slate-900">{item.percentage}%</span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-200/70 rounded-full h-2 overflow-hidden shadow-inner">
                      <div
                        className="h-2 rounded-full transition-all duration-700"
                        style={{ width: `${item.percentage}%`, backgroundColor: item.barColor }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 bg-emerald-50/70 border border-emerald-200/70 rounded-2xl flex items-center justify-between text-xs text-slate-700 mt-2">
              <span className="flex items-center gap-2 font-medium">
                <i className="ph-fill ph-lightbulb text-emerald-600 text-base"></i>
                Surface corrosion remains highest frequency; proactive recoating saves 64% lifecycle expense.
              </span>
            </div>
          </div>

          {/* Predictive Degradation Timeline Card */}
          <div className="lg:col-span-6 glass-card rounded-3xl p-6 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">30-60-90 Day Predictive Degradation</h3>
                  <p className="text-xs text-slate-500 font-medium">Structural degradation risk curve based on atmospheric salinity & wind loading</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold">
                  AI Forecast
                </span>
              </div>

              {/* Timeline Forecast Grid */}
              <div className="grid grid-cols-3 gap-3 my-4">
                <div className="p-4 rounded-2xl bg-white/70 border border-white/90 flex flex-col justify-between">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">30-Day Outlook</span>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-emerald-700">94.2%</span>
                    <span className="block text-[10px] text-slate-500 mt-0.5">High Stability</span>
                  </div>
                  <span className="text-[10px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200 inline-block text-center">
                    4 Fasteners Due
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-white/70 border border-white/90 flex flex-col justify-between">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">60-Day Outlook</span>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-amber-600">86.8%</span>
                    <span className="block text-[10px] text-slate-500 mt-0.5">Moderate Wear</span>
                  </div>
                  <span className="text-[10px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200 inline-block text-center">
                    12 Recoatings Due
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-white/70 border border-white/90 flex flex-col justify-between">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">90-Day Outlook</span>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-rose-600">76.4%</span>
                    <span className="block text-[10px] text-slate-500 mt-0.5">Elevated Risk</span>
                  </div>
                  <span className="text-[10px] font-semibold text-rose-800 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200 inline-block text-center">
                    18 Interventions
                  </span>
                </div>
              </div>
            </div>

            <div className="p-3 bg-white/60 border border-slate-200/80 rounded-2xl flex items-center justify-between text-xs">
              <span className="text-slate-600 font-medium">Compliant with ANSI/TIA-222-H Structural Standards</span>
              <span className="font-bold text-emerald-700 flex items-center gap-1">
                <i className="ph-fill ph-seal-check"></i> Standard Met
              </span>
            </div>
          </div>

        </div>

        {/* Regional Fleet Asset Table */}
        <div className="glass-card rounded-3xl overflow-hidden shadow-sm flex flex-col">
          <div className="p-5 border-b border-white/80 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-base text-slate-900">Regional Tower Assets & Immediate Action List</h3>
              <p className="text-xs text-slate-500 font-medium">Click any tower asset to inspect full neural scan in primary workspace</p>
            </div>
            <span className="text-xs font-bold text-slate-600 bg-white/80 px-3 py-1.5 rounded-xl border border-white shadow-2xs">
              Showing {filteredAssets.length} of {regionalAssets.length} Assets
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-white/40 border-b border-white/80 text-slate-600 font-bold uppercase text-[11px] tracking-wider">
                  <th className="py-3.5 px-6">Tower Asset ID</th>
                  <th className="py-3.5 px-6">Region / Sector</th>
                  <th className="py-3.5 px-6">Architecture</th>
                  <th className="py-3.5 px-6">Integrity Score</th>
                  <th className="py-3.5 px-6">Defect Flags</th>
                  <th className="py-3.5 px-6">Last AI Scan</th>
                  <th className="py-3.5 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/60 font-medium">
                {filteredAssets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-white/50 transition">
                    <td className="py-4 px-6 font-mono font-bold text-slate-900 flex items-center gap-2.5">
                      <div className="p-1.5 bg-emerald-100/70 text-emerald-700 rounded-lg">
                        <i className="ph-fill ph-broadcast text-sm"></i>
                      </div>
                      #{asset.id}
                    </td>
                    <td className="py-4 px-6 text-slate-700 font-semibold">{asset.region}</td>
                    <td className="py-4 px-6 text-slate-600">{asset.type}</td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-2 font-mono">
                        <span className={`font-bold ${
                          asset.health >= 90 ? 'text-emerald-700' :
                          asset.health >= 80 ? 'text-blue-700' :
                          asset.health >= 70 ? 'text-amber-600' : 'text-rose-600'
                        }`}>
                          {asset.health}%
                        </span>
                        <div className="w-20 bg-slate-200/80 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-1.5 rounded-full ${
                              asset.health >= 90 ? 'bg-emerald-500' :
                              asset.health >= 80 ? 'bg-blue-500' :
                              asset.health >= 70 ? 'bg-amber-500' : 'bg-rose-500'
                            }`}
                            style={{ width: `${asset.health}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${
                        asset.anomalies === 0 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                        asset.anomalies <= 2 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-rose-50 text-rose-700 border-rose-200'
                      }`}>
                        {asset.anomalies} Detected
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-500">{asset.lastScan}</td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => onSelectTower && onSelectTower(asset.id, asset.type)}
                        className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold transition text-xs shadow-sm hover:scale-[1.02] active:scale-[0.98] inline-flex items-center gap-1"
                      >
                        <span>Inspect</span>
                        <i className="ph ph-arrow-right"></i>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
