import React, { useState } from 'react';

export default function ImageRefineModal({ isOpen, onClose, imageSrc, onApply }) {
  const [contrast, setContrast] = useState(140);
  const [brightness, setBrightness] = useState(110);
  const [sharpness, setSharpness] = useState(160);
  const [saturation, setSaturation] = useState(140);
  const [activePreset, setActivePreset] = useState('HDR Defect Boost');

  if (!isOpen) return null;

  const applyPreset = (preset) => {
    if (preset === 'hdr') {
      setContrast(145);
      setBrightness(115);
      setSharpness(180);
      setSaturation(160);
      setActivePreset('HDR Defect Boost');
    } else if (preset === 'superRes') {
      setContrast(125);
      setBrightness(100);
      setSharpness(240);
      setSaturation(110);
      setActivePreset('Super-Res 4X');
    } else if (preset === 'rust') {
      setContrast(160);
      setBrightness(95);
      setSharpness(150);
      setSaturation(220);
      setActivePreset('Rust Isolate');
    }
  };

  const resetSliders = () => {
    setContrast(100);
    setBrightness(100);
    setSharpness(100);
    setSaturation(100);
    setActivePreset('Natural / Raw');
  };

  const handleApply = () => {
    onApply({
      contrast,
      brightness,
      sharpness,
      saturation,
      filterString: `contrast(${contrast}%) brightness(${brightness}%) saturate(${saturation}%)`
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
      <div className="w-full max-w-4xl bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-2xl relative flex flex-col max-h-[92vh] overflow-hidden text-slate-800">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 text-xl shadow-sm">
              <i className="ph-fill ph-magic-wand"></i>
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                Image Refining Studio
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 border border-emerald-200">AI HD Engine</span>
              </h3>
              <p className="text-xs text-slate-500 font-medium">Calibrate optical exposure, enhance structural edges, and super-resolve defects.</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition">
            <i className="ph ph-x text-base"></i>
          </button>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1 overflow-y-auto pr-1">
          {/* Canvas Preview */}
          <div className="md:col-span-7 flex flex-col items-center justify-center bg-slate-900 rounded-2xl p-4 relative overflow-hidden min-h-[280px]">
            <img 
              src={imageSrc} 
              alt="Refined Target" 
              style={{ filter: `contrast(${contrast}%) brightness(${brightness}%) saturate(${saturation}%)` }}
              className="max-h-[300px] w-full object-contain rounded-xl transition-all duration-150"
            />
            
            <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-3 py-1 rounded-lg border border-slate-200 text-[11px] text-slate-700 font-medium flex items-center gap-2 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Active Preset: <strong className="text-emerald-700 font-semibold">{activePreset}</strong></span>
            </div>
          </div>

          {/* Controls */}
          <div className="md:col-span-5 flex flex-col gap-4 bg-slate-50 border border-slate-200 rounded-2xl p-5">
            <div>
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-2.5">Neural Filter Presets</span>
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => applyPreset('hdr')} className="px-3 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 transition text-left flex items-center gap-2 shadow-sm">
                  <i className="ph-fill ph-sun text-amber-500"></i> HDR Boost
                </button>
                <button onClick={() => applyPreset('superRes')} className="px-3 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 transition text-left flex items-center gap-2 shadow-sm">
                  <i className="ph-fill ph-sparkle text-emerald-600"></i> Super-Res 4X
                </button>
                <button onClick={() => applyPreset('rust')} className="px-3 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 transition text-left flex items-center gap-2 shadow-sm">
                  <i className="ph-fill ph-eye text-orange-500"></i> Rust Isolate
                </button>
                <button onClick={resetSliders} className="px-3 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-600 transition text-left flex items-center gap-2 shadow-sm">
                  <i className="ph ph-arrow-counter-clockwise"></i> Reset Raw
                </button>
              </div>
            </div>

            {/* Sliders */}
            <div className="space-y-3 pt-2 border-t border-slate-200">
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>Contrast Boost</span>
                  <span className="text-emerald-700 font-mono font-bold">{contrast}%</span>
                </div>
                <input 
                  type="range" min="50" max="200" value={contrast} 
                  onChange={(e) => setContrast(Number(e.target.value))} 
                  className="w-full accent-emerald-600 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>Exposure & Brightness</span>
                  <span className="text-amber-600 font-mono font-bold">{brightness}%</span>
                </div>
                <input 
                  type="range" min="50" max="180" value={brightness} 
                  onChange={(e) => setBrightness(Number(e.target.value))} 
                  className="w-full accent-amber-500 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>Edge Sharpness</span>
                  <span className="text-indigo-600 font-mono font-bold">{sharpness}%</span>
                </div>
                <input 
                  type="range" min="100" max="300" value={sharpness} 
                  onChange={(e) => setSharpness(Number(e.target.value))} 
                  className="w-full accent-indigo-600 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>Color Saturation (Rust)</span>
                  <span className="text-orange-600 font-mono font-bold">{saturation}%</span>
                </div>
                <input 
                  type="range" min="50" max="250" value={saturation} 
                  onChange={(e) => setSaturation(Number(e.target.value))} 
                  className="w-full accent-orange-500 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                />
              </div>

              {/* Detection Thresholds Section */}
              <div className="pt-3 border-t border-slate-200 space-y-2.5">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded-md bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 text-xs">
                    <i className="ph-fill ph-bounding-box"></i>
                  </div>
                  <span className="text-[11px] font-bold text-slate-800 uppercase tracking-wider">Detection Thresholds</span>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-medium text-slate-700">Confidence Threshold</span>
                    <span className="font-mono font-bold text-rose-500 text-xs">0.20</span>
                  </div>
                  <input 
                    type="range" min="0.05" max="0.95" step="0.01" defaultValue="0.20" 
                    className="w-full accent-rose-500 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                  />
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-medium text-slate-700">NMS IoU Threshold</span>
                    <span className="font-mono font-bold text-rose-500 text-xs">0.45</span>
                  </div>
                  <input 
                    type="range" min="0.10" max="0.90" step="0.01" defaultValue="0.45" 
                    className="w-full accent-rose-500 bg-slate-200 h-1.5 rounded-lg cursor-pointer"
                  />
                </div>
              </div>
            </div>

            <div className="mt-auto pt-3 flex gap-3">
              <button onClick={onClose} className="flex-1 py-2.5 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold transition shadow-sm">
                Cancel
              </button>
              <button onClick={handleApply} className="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 active:scale-95 transition flex items-center justify-center gap-1.5">
                <i className="ph ph-check text-sm font-bold"></i> Apply to Scan
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
