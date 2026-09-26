import React, { useRef, useEffect } from 'react';

export default function CameraModal({ isOpen, onClose, onCapture }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            streamRef.current = stream;
            if (videoRef.current) {
              videoRef.current.srcObject = stream;
            }
          })
          .catch(() => {});
      }
    } else {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
      <div className="w-full max-w-lg bg-white border border-slate-200 rounded-3xl p-6 shadow-2xl relative text-center">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-slate-800 font-bold text-base">
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <i className="ph ph-camera text-lg"></i>
            </div>
            <span>Live Optical Feed</span>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 flex items-center justify-center transition">
            <i className="ph ph-x"></i>
          </button>
        </div>

        <p className="text-xs text-slate-500 mb-4 text-left font-medium">Position the telecommunication tower structure within the frame.</p>
        
        <div className="aspect-video bg-slate-900 rounded-2xl overflow-hidden border border-slate-200 relative flex items-center justify-center mb-6">
          <video ref={videoRef} className="w-full h-full object-cover" autoPlay playsInline></video>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-emerald-400 pointer-events-none bg-black/20">
            <div className="w-12 h-12 rounded-full border-2 border-dashed border-emerald-400 animate-spin flex items-center justify-center mb-2">
              <i className="ph ph-broadcast text-lg"></i>
            </div>
            <span className="text-xs text-slate-300 font-medium">Optical Sensor Stream Active</span>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3">
          <button 
            onClick={onClose} 
            className="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition"
          >
            Cancel
          </button>
          <button 
            onClick={onCapture} 
            className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 active:scale-95 transition flex items-center gap-2"
          >
            <i className="ph ph-aperture text-sm"></i>
            Capture Snapshot
          </button>
        </div>
      </div>
    </div>
  );
}
