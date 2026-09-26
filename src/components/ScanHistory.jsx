import React, { useState } from 'react';

export default function ScanHistory({ onViewScan }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const historyData = [
    { id: 'TWR-4091', type: 'Supporting', architecture: 'Supporting Lattice', date: 'Today, 15:42', confidence: 96.4, color: 'bg-emerald-500', icon: 'ph-broadcast' },
    { id: 'TWR-8812', type: 'Monopole', architecture: 'Monopole Tower', date: 'Yesterday, 11:20', confidence: 99.1, color: 'bg-blue-500', icon: 'ph-arrows-vertical' },
    { id: 'TWR-7734', type: 'Supporting', architecture: 'Supporting Lattice', date: '23 Sep 2026', confidence: 94.8, color: 'bg-emerald-500', icon: 'ph-broadcast' },
    { id: 'TWR-6520', type: 'Guyed', architecture: 'Guyed Mast Cable', date: '21 Sep 2026', confidence: 98.5, color: 'bg-indigo-500', icon: 'ph-anchor' },
    { id: 'TWR-5103', type: 'Monopole', architecture: 'Monopole Tower', date: '18 Sep 2026', confidence: 97.2, color: 'bg-blue-500', icon: 'ph-arrows-vertical' }
  ];

  const filteredHistory = historyData.filter(item => {
    const matchesQuery = item.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || item.type === filterType;
    return matchesQuery && matchesFilter;
  });

  return (
    <div className="flex flex-col h-full w-full">
      {/* Header */}
      <header className="pt-10 pb-6 px-10 flex-shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Scan History</h1>
          <p className="text-sm font-medium text-slate-500 mt-1">Historical Telecommunication Structural Inspections</p>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <i className="ph ph-magnifying-glass text-slate-400 text-base absolute left-3 top-2.5"></i>
            <input 
              type="text" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search Tower ID..." 
              className="pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-500 w-44 sm:w-52 shadow-sm font-medium"
            />
          </div>
          <select 
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl text-xs text-slate-700 py-2 px-3 focus:outline-none focus:border-emerald-500 shadow-sm font-medium"
          >
            <option value="all">All Types</option>
            <option value="Supporting">Supporting</option>
            <option value="Monopole">Monopole</option>
            <option value="Guyed">Guyed</option>
          </select>
        </div>
      </header>

      {/* Content Container */}
      <div className="px-10 pb-10 flex-1 w-full max-w-7xl flex flex-col gap-6">
        {/* History Summary Stats with Glassmorphism */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-card rounded-2xl p-4 shadow-sm">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block">Total Scans</span>
            <span className="text-2xl font-bold text-slate-900 mt-1 block">14</span>
          </div>
          <div className="glass-card rounded-2xl p-4 shadow-sm">
            <span className="text-xs text-emerald-700 font-semibold uppercase tracking-wider block">Avg. Confidence</span>
            <span className="text-2xl font-bold text-emerald-800 mt-1 block">97.2%</span>
          </div>
          <div className="glass-card rounded-2xl p-4 shadow-sm">
            <span className="text-xs text-blue-700 font-semibold uppercase tracking-wider block">High Confidence (&gt;95%)</span>
            <span className="text-2xl font-bold text-blue-800 mt-1 block">12</span>
          </div>
          <div className="glass-card rounded-2xl p-4 shadow-sm">
            <span className="text-xs text-amber-700 font-semibold uppercase tracking-wider block">Under Review</span>
            <span className="text-2xl font-bold text-amber-800 mt-1 block">2</span>
          </div>
        </div>

        {/* History Table Container with Glassmorphism */}
        <div className="glass-card rounded-3xl overflow-hidden shadow-sm flex-1 flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-white/40 border-b border-white/80 text-slate-600 font-bold uppercase text-[11px] tracking-wider backdrop-blur-md">
                  <th className="py-4 px-6">Tower ID</th>
                  <th className="py-4 px-6">Architecture</th>
                  <th className="py-4 px-6">Scan Date</th>
                  <th className="py-4 px-6">Confidence Score</th>
                  <th className="py-4 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredHistory.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-4 px-6 font-mono font-bold text-slate-900 flex items-center gap-2.5">
                      <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                        <i className={`ph-fill ${row.icon} text-sm`}></i>
                      </div>
                      #{row.id}
                    </td>
                    <td className="py-4 px-6 text-slate-700 font-semibold">{row.architecture}</td>
                    <td className="py-4 px-6 text-slate-500">{row.date}</td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <span className="text-emerald-700 font-bold font-mono text-xs">{row.confidence}%</span>
                        <div className="w-28 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                          <div className={`${row.color} h-2 rounded-full`} style={{ width: `${row.confidence}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button 
                        onClick={() => onViewScan(row.id, row.type)}
                        className="px-4 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-xl font-semibold transition text-xs shadow-sm"
                      >
                        View Scan
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
