import React from 'react';

export default function ToastNotification({ toast }) {
  if (!toast) return null;

  const isSuccess = toast.type === 'success';
  const isWarning = toast.type === 'warning';

  return (
    <div className="fixed bottom-6 left-6 bg-white/95 border border-slate-200 text-slate-800 px-5 py-3.5 rounded-2xl shadow-xl backdrop-blur-xl flex items-center gap-3 transition-all duration-300 z-50 animate-in fade-in slide-in-from-bottom-5">
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-sm border ${
        isSuccess 
          ? 'bg-emerald-50 text-emerald-600 border-emerald-200 shadow-sm' 
          : isWarning 
            ? 'bg-amber-50 text-amber-600 border-amber-200 shadow-sm' 
            : 'bg-slate-50 text-slate-700 border-slate-200 shadow-sm'
      }`}>
        <i className={isSuccess ? 'ph-fill ph-check-circle' : isWarning ? 'ph-fill ph-warning-circle' : 'ph-fill ph-info'}></i>
      </div>
      <div>
        <p className="text-xs font-bold text-slate-900">{toast.title}</p>
        <p className="text-[11px] text-slate-500 font-medium">{toast.message}</p>
      </div>
    </div>
  );
}
