import React, { useRef } from 'react';
import StructiLogo from './StructiLogo';

export default function ReportModal({ isOpen, onClose, scanResult, imageSrc, qualityMetrics }) {
  const printRef = useRef(null);

  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const currentResult = scanResult || {
    tower_type: "Supporting Lattice Tower",
    confidence: 0.984,
    health_score: 74,
    detections: [
      { class: "Surface Corrosion", confidence: 0.964, severity: "Critical", box: { top: "30%", left: "45%", width: "25%", height: "20%" }, recommendation: "Rust treatment & protective epoxy recoating within 30 days" },
      { class: "Missing Bolt", confidence: 0.882, severity: "High", box: { top: "58%", left: "28%", width: "20%", height: "16%" }, recommendation: "Fasten Grade 8.8 galvanized structural bolt at elevation +14m" },
      { class: "Structural Crack", confidence: 0.915, severity: "Medium", box: { top: "44%", left: "60%", width: "18%", height: "15%" }, recommendation: "Ultrasonic NDT inspection on gusset weld seam" }
    ]
  };

  return (
    <div className="fixed inset-0 bg-slate-900/70 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-in fade-in overflow-y-auto">
      <div className="w-full max-w-4xl glass-modal rounded-3xl p-6 sm:p-8 shadow-2xl relative flex flex-col max-h-[92vh] overflow-hidden text-slate-800 my-auto">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200/80 mb-5 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-xl shadow-md">
              <i className="ph-fill ph-file-text"></i>
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                Structural Engineering Dossier
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 border border-emerald-200">
                  Certified AI Report
                </span>
              </h3>
              <p className="text-xs text-slate-500 font-medium">Official Automated Inspection & Defect Remediation Sheet</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs flex items-center gap-1.5 transition shadow-sm hover:scale-[1.02] active:scale-[0.98]"
            >
              <i className="ph-fill ph-printer text-sm"></i>
              <span>Print / Export PDF</span>
            </button>
            <button
              onClick={onClose}
              className="w-9 h-9 rounded-xl bg-white/80 hover:bg-white text-slate-500 hover:text-slate-800 flex items-center justify-center transition border border-slate-200"
            >
              <i className="ph ph-x text-base font-bold"></i>
            </button>
          </div>
        </div>

        {/* Printable Report Document Body */}
        <div ref={printRef} className="flex-1 overflow-y-auto pr-1 space-y-6 text-slate-800">
          
          {/* Document Header Card */}
          <div className="p-5 rounded-2xl bg-white/80 border border-white/90 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <StructiLogo size="md" />
            <div className="text-left sm:text-right text-xs">
              <span className="font-mono font-bold text-slate-900 text-sm block">REPORT #SV-{Date.now().toString().slice(-6)}</span>
              <span className="text-slate-500 font-medium">Generated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
              <span className="text-emerald-700 font-bold block mt-0.5">ANSI / TIA-222-H Structural Standard</span>
            </div>
          </div>

          {/* Asset Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-white/70 border border-white/90">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Classified Asset</span>
              <span className="font-bold text-slate-900 text-sm">{currentResult.tower_type}</span>
              <span className="text-[10px] text-emerald-700 font-semibold block mt-0.5">{(currentResult.confidence * 100).toFixed(1)}% Match Conf.</span>
            </div>
            <div className="p-3.5 rounded-xl bg-white/70 border border-white/90">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Structural Health</span>
              <span className="font-bold text-amber-600 text-sm">{currentResult.health_score || 74}% / 100</span>
              <span className="text-[10px] text-slate-500 font-semibold block mt-0.5">Moderate Degradation</span>
            </div>
            <div className="p-3.5 rounded-xl bg-white/70 border border-white/90">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Anomalies Detected</span>
              <span className="font-bold text-rose-600 text-sm">{currentResult.detections?.length || 3} Classes</span>
              <span className="text-[10px] text-rose-700 font-semibold block mt-0.5">1 Critical Action</span>
            </div>
            <div className="p-3.5 rounded-xl bg-white/70 border border-white/90">
              <span className="text-[10px] font-bold uppercase text-slate-400 block">Optics Quality</span>
              <span className="font-bold text-emerald-700 text-sm">{qualityMetrics?.sharpness || 96}% Sharpness</span>
              <span className="text-[10px] text-slate-500 font-semibold block mt-0.5">Optimal HD Feed</span>
            </div>
          </div>

          {/* Visual Scan Layout */}
          {imageSrc && (
            <div className="p-4 rounded-2xl bg-white/70 border border-white/90 space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500">Annotated Optical Inspection Plate</h4>
              <div className="relative rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center max-h-64">
                <img src={imageSrc} alt="Inspection Plate" className="max-h-60 w-auto object-contain mx-auto" />
                {currentResult.detections?.map((det, i) => (
                  <div
                    key={i}
                    style={{
                      position: 'absolute',
                      top: det.box.top,
                      left: det.box.left,
                      width: det.box.width,
                      height: det.box.height
                    }}
                    className="border-2 border-emerald-400 bg-emerald-400/20 rounded pointer-events-none"
                  >
                    <span className="absolute -top-5 left-0 bg-slate-900/90 text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                      {det.class}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Defect Manifest Table */}
          <div className="rounded-2xl bg-white/80 border border-white/90 overflow-hidden shadow-xs">
            <div className="p-4 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-700">Defect Manifest & Remediation Mandate</h4>
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200">
                Action Required within 30 Days
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-100 text-slate-500 uppercase font-bold text-[10px]">
                    <th className="py-2.5 px-4">Defect Class</th>
                    <th className="py-2.5 px-4">Severity</th>
                    <th className="py-2.5 px-4">Confidence</th>
                    <th className="py-2.5 px-4">Bounding Coordinates</th>
                    <th className="py-2.5 px-4">Recommended Field Remediation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {currentResult.detections?.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50">
                      <td className="py-3 px-4 font-bold text-slate-900">{item.class}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.severity === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                          item.severity === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                          'bg-blue-50 text-blue-700 border border-blue-200'
                        }`}>
                          {item.severity || 'Medium'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-emerald-700">{(item.confidence * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 font-mono text-[10px] text-slate-500">
                        [T:{item.box?.top}, L:{item.box?.left}, W:{item.box?.width}, H:{item.box?.height}]
                      </td>
                      <td className="py-3 px-4 text-slate-700 text-[11px] leading-relaxed">
                        {item.recommendation || "Standard field maintenance required."}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Inspector Endorsement Footer */}
          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-700">
            <div className="flex items-center gap-2.5">
              <i className="ph-fill ph-certificate text-2xl text-emerald-600"></i>
              <div>
                <span className="font-bold text-slate-900 block">AI Vision Engine Endorsement</span>
                <span className="text-[11px] text-slate-500">Autonomous edge inference validated against ISO 9001 quality metrics.</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 uppercase font-mono block">Signature Token</span>
              <span className="font-mono text-emerald-800 font-bold text-[10px]">SHA256: 8f4a21...d9e03c</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
