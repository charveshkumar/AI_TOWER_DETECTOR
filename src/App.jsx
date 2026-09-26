import React, { useState } from 'react';
import HomeInspection from './components/HomeInspection';
import { sampleTowerSvg } from './constants/assets';
import ScanHistory from './components/ScanHistory';
import ImageRefineModal from './components/ImageRefineModal';
import CameraModal from './components/CameraModal';
import ReportModal from './components/ReportModal';
import AiChatbot from './components/AiChatbot';
import ToastNotification from './components/ToastNotification';
import StructiLogo from './components/StructiLogo';
import NotificationDropdown from './components/NotificationDropdown';

export default function StructiVisionDashboard() {
  const [activeTab, setActiveTab] = useState('inspection'); // 'inspection' | 'history'
  const [currentImage, setCurrentImage] = useState(null);
  const [imageFilter, setImageFilter] = useState('');
  const [isRefineModalOpen, setIsRefineModalOpen] = useState(false);
  const [isCameraModalOpen, setIsCameraModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const [toastTimer, setToastTimer] = useState(null);

  const [qualityMetrics, setQualityMetrics] = useState({
    status: 'Awaiting Upload',
    sharpness: 0,
    color: 0,
    lighting: 0,
    noise: 0
  });

  const showToast = (title, message, type = 'info') => {
    if (toastTimer) clearTimeout(toastTimer);
    setToast({ title, message, type });
    const timer = setTimeout(() => {
      setToast(null);
    }, 3500);
    setToastTimer(timer);
  };

  const handleImageLoaded = (src, file) => {
    setCurrentImage(src);
    window.currentUploadedFile = file;
  };

  const handleResetImage = () => {
    setCurrentImage(null);
    setImageFilter('');
    window.currentUploadedFile = null;
  };

  const handleApplyRefined = (calibration) => {
    setImageFilter(calibration.filterString);
    setQualityMetrics({
      status: 'Assessed: Optimal (AI HD)',
      sharpness: 99,
      color: 97,
      lighting: 95,
      noise: 99
    });
    showToast("Refining Applied", "Calibrated image loaded into Home Inspection with enhanced quality scores.", "success");
  };

  const handleCameraCapture = () => {
    setIsCameraModalOpen(false);
    setCurrentImage(sampleTowerSvg);
    setQualityMetrics({
      status: 'Assessed: Optimal',
      sharpness: 96,
      color: 94,
      lighting: 91,
      noise: 98
    });
    showToast("Image Successfully Uploaded", "Camera snapshot captured and uploaded successfully.", "success");
  };

  const handleViewHistoricalScan = (towerId, type) => {
    setActiveTab('inspection');
    setCurrentImage(sampleTowerSvg);
    setQualityMetrics({
      status: 'Assessed: Optimal',
      sharpness: 96,
      color: 94,
      lighting: 91,
      noise: 98
    });
    showToast("Scan Loaded", `Loaded historical inspection for #${towerId}`, "info");
  };

  return (
    <div className="text-slate-800 antialiased h-screen w-full flex overflow-hidden relative font-sans">
      {/* 100% Visible Background Image (Watermark Cleaned) */}
      <div 
        className="fixed inset-0 pointer-events-none z-0 bg-cover bg-right-bottom bg-no-repeat opacity-100"
        style={{ backgroundImage: "url('/bg-tower.jpg')" }}
      />
      
      {/* Sidebar with Glassmorphism */}
      <aside className="w-72 glass-sidebar flex flex-col justify-between flex-shrink-0 z-20 relative">
        <div>
          {/* Logo Section */}
          <div 
            onClick={() => setActiveTab('inspection')}
            className="h-20 flex items-center px-6 border-b border-white/60 cursor-pointer hover:bg-white/40 transition"
          >
            <StructiLogo size="md" />
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1 mt-2">
            <button 
              onClick={() => setActiveTab('inspection')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold border transition-all text-left ${
                activeTab === 'inspection'
                  ? 'bg-emerald-500/15 text-emerald-800 border-emerald-500/30 shadow-sm backdrop-blur-md'
                  : 'text-slate-600 hover:bg-white/50 hover:text-slate-900 border-transparent font-medium'
              }`}
            >
              <i className="ph ph-house text-xl"></i>
              Home
            </button>

            <button 
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all text-left border ${
                activeTab === 'history'
                  ? 'bg-emerald-500/15 text-emerald-800 border-emerald-500/30 shadow-sm backdrop-blur-md font-semibold'
                  : 'text-slate-600 hover:bg-white/50 hover:text-slate-900 border-transparent font-medium group'
              }`}
            >
              <div className="flex items-center gap-3">
                <i className="ph ph-clock-counter-clockwise text-xl group-hover:text-slate-800"></i>
                Scan History
              </div>
              <span className="bg-white/70 border border-slate-200/80 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full shadow-2xs">14</span>
            </button>

            <button 
              onClick={() => setIsRefineModalOpen(true)}
              className="w-full flex items-center justify-between px-4 py-3 text-slate-600 hover:bg-white/50 hover:text-slate-900 rounded-xl font-medium transition-all group mt-2 border border-transparent text-left"
            >
              <div className="flex items-center gap-3">
                <i className="ph ph-magic-wand text-xl group-hover:text-slate-800"></i>
                Image Refining
              </div>
              <span className="bg-emerald-100/90 border border-emerald-300/80 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-md shadow-2xs">AI HD</span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer Status */}
        <div className="p-6 border-t border-white/60 bg-white/30 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-slate-600 tracking-wide uppercase">Vision Model Active</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-y-auto relative z-10">
        {/* Top Navbar Header with Glassmorphism */}
        <header className="h-16 px-10 glass-header flex items-center justify-between sticky top-0 z-30 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-sm font-bold text-slate-900 tracking-tight">
              Smarter Vision. Stronger Structures.
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick Dossier trigger */}
            <button
              onClick={() => setIsReportModalOpen(true)}
              className="h-10 px-3.5 rounded-xl bg-white/90 hover:bg-white text-slate-700 hover:text-slate-900 border border-white text-xs font-bold flex items-center gap-1.5 transition shadow-2xs backdrop-blur-md"
            >
              <i className="ph-fill ph-file-text text-base text-emerald-600"></i>
              <span className="hidden sm:inline">Dossier Sheet</span>
            </button>

            {/* Quick Refine trigger */}
            <button
              onClick={() => setIsRefineModalOpen(true)}
              className="h-10 px-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold flex items-center gap-1.5 transition shadow-xs"
            >
              <i className="ph ph-magic-wand text-base text-emerald-600"></i>
              <span className="hidden sm:inline">Refine HD</span>
            </button>

            {/* Notification Button & Flyout Dropdown */}
            <NotificationDropdown 
              showToast={showToast} 
              onViewScan={handleViewHistoricalScan} 
            />
          </div>
        </header>

        {activeTab === 'inspection' && (
          <HomeInspection 
            currentImage={currentImage}
            onImageLoaded={handleImageLoaded}
            onResetImage={handleResetImage}
            onOpenRefineModal={() => setIsRefineModalOpen(true)}
            onOpenCameraModal={() => setIsCameraModalOpen(true)}
            onOpenReportModal={() => setIsReportModalOpen(true)}
            showToast={showToast}
            imageFilter={imageFilter}
            qualityMetrics={qualityMetrics}
            setQualityMetrics={setQualityMetrics}
          />
        )}

        {activeTab === 'history' && (
          <ScanHistory onViewScan={handleViewHistoricalScan} />
        )}
      </main>

      {/* Image Refining Studio Modal */}
      <ImageRefineModal 
        isOpen={isRefineModalOpen}
        onClose={() => setIsRefineModalOpen(false)}
        imageSrc={currentImage || sampleTowerSvg}
        onApply={handleApplyRefined}
      />

      {/* Camera Live Feed Modal */}
      <CameraModal 
        isOpen={isCameraModalOpen}
        onClose={() => setIsCameraModalOpen(false)}
        onCapture={handleCameraCapture}
      />

      {/* Engineering Report Dossier Modal */}
      <ReportModal 
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        imageSrc={currentImage || sampleTowerSvg}
        qualityMetrics={qualityMetrics}
      />

      {/* Circular Draggable AI Chatbot */}
      <AiChatbot 
        onLoadToDashboard={(imageData) => {
          setActiveTab('inspection');
          setCurrentImage(imageData);
          setQualityMetrics({
            status: 'Assessed: Optimal (AI Copilot)',
            sharpness: 96,
            color: 94,
            lighting: 91,
            noise: 98
          });
          showToast("Loaded from AI Copilot", "In-chat inspection analysis transferred to main dashboard.", "success");
        }}
        showToast={showToast}
      />

      {/* Toast Notification Alert */}
      <ToastNotification toast={toast} />

    </div>
  );
}
