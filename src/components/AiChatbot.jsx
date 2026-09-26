import React, { useState, useRef, useEffect } from 'react';
import { sampleTowerSvg } from '../constants/assets';
import StructiLogo from './StructiLogo';

export default function AiChatbot({ onLoadToDashboard, showToast }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      type: 'text',
      text: "Hello! I'm your StructiVision AI Assistant. You can ask me questions or <strong>upload any tower image directly here</strong> for instant structural defect detection and quality analysis."
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [position, setPosition] = useState({ x: null, y: null });
  const [isDragOver, setIsDragOver] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ startX: 0, startY: 0, initialX: 0, initialY: 0 });
  const hasMovedRef = useRef(false);
  const chatBottomRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen && chatBottomRef.current) {
      chatBottomRef.current.scrollTop = chatBottomRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  // Floating trigger dragging logic
  const handlePointerDown = (e) => {
    isDraggingRef.current = true;
    hasMovedRef.current = false;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    dragStartRef.current = {
      startX: clientX,
      startY: clientY,
      initialX: position.x ?? (window.innerWidth - 80),
      initialY: position.y ?? (window.innerHeight - 80)
    };
  };

  const handlePointerMove = (e) => {
    if (!isDraggingRef.current) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    const dx = clientX - dragStartRef.current.startX;
    const dy = clientY - dragStartRef.current.startY;

    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
      hasMovedRef.current = true;
    }

    let newX = dragStartRef.current.initialX + dx;
    let newY = dragStartRef.current.initialY + dy;

    newX = Math.max(10, Math.min(newX, window.innerWidth - 70));
    newY = Math.max(10, Math.min(newY, window.innerHeight - 70));

    setPosition({ x: newX, y: newY });
  };

  const handlePointerUp = () => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    if (!hasMovedRef.current) {
      setIsOpen(!isOpen);
    }
  };

  useEffect(() => {
    const handleWindowMove = (e) => handlePointerMove(e);
    const handleWindowUp = () => handlePointerUp();

    window.addEventListener('mousemove', handleWindowMove);
    window.addEventListener('mouseup', handleWindowUp);
    window.addEventListener('touchmove', handleWindowMove);
    window.addEventListener('touchend', handleWindowUp);

    return () => {
      window.removeEventListener('mousemove', handleWindowMove);
      window.removeEventListener('mouseup', handleWindowUp);
      window.removeEventListener('touchmove', handleWindowMove);
      window.removeEventListener('touchend', handleWindowUp);
    };
  }, [isOpen, position]);

  // Handle Chat Image Upload & In-Chat Neural Analysis
  const handleChatImageUpload = (file) => {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const imageSrc = e.target.result;
      processUploadedImage(imageSrc, file.name);
    };
    reader.readAsDataURL(file);
  };

  const processUploadedImage = (imageSrc, fileName) => {
    const userMsgId = Date.now();
    const botMsgId = userMsgId + 1;

    // 1. Add User message with image preview
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      type: 'image_upload',
      imageSrc,
      fileName,
      text: `Uploaded structural inspection image: <strong>${fileName}</strong>`
    };

    // 2. Add initial Processing Bot message
    const botProcessingMsg = {
      id: botMsgId,
      sender: 'bot',
      type: 'processing',
      imageSrc,
      fileName,
      progress: 45,
      text: 'Analyzing structural integrity, detecting bounding boxes & assessing quality...'
    };

    setMessages(prev => [...prev, userMsg, botProcessingMsg]);

    if (showToast) {
      showToast("Image Uploaded to Chat", `Running in-chat structural detection on "${fileName}"`, "info");
    }

    // 3. Simulate backend/neural detection processing & complete analysis inside chat
    setTimeout(() => {
      const fullAnalysisResult = {
        id: botMsgId,
        sender: 'bot',
        type: 'inspection_report',
        imageSrc,
        fileName,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        tower_type: "Supporting Lattice Tower",
        tower_confidence: 98.4,
        health_score: 74,
        health_status: 'Moderate (Preventive Recoating Required)',
        qualityMetrics: {
          sharpness: 96,
          color: 94,
          lighting: 91,
          noise: 98
        },
        detections: [
          {
            id: 'det-1',
            class: "Surface Corrosion",
            confidence: 96.4,
            severity: "Critical",
            location: "Lower cross-brace truss",
            color: "#ef4444",
            box: { top: "30%", left: "45%", width: "25%", height: "20%" }
          },
          {
            id: 'det-2',
            class: "Missing Bolt",
            confidence: 88.2,
            severity: "High",
            location: "Flange joint elevation +14m",
            color: "#f59e0b",
            box: { top: "58%", left: "28%", width: "20%", height: "16%" }
          },
          {
            id: 'det-3',
            class: "Structural Crack",
            confidence: 91.5,
            severity: "Medium",
            location: "Gusset plate weld",
            color: "#6366f1",
            box: { top: "44%", left: "60%", width: "18%", height: "15%" }
          }
        ],
        recommendation: "Perform surface rust treatment and recoating within 30 days. Fasten missing flange bolt to restore structural load rating."
      };

      setMessages(prev => prev.map(m => m.id === botMsgId ? fullAnalysisResult : m));

      if (showToast) {
        showToast("Analysis Complete", `Found 3 anomalies on ${fullAnalysisResult.tower_type}`, "success");
      }
    }, 1200);
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleChatImageUpload(e.target.files[0]);
      e.target.value = '';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleChatImageUpload(e.dataTransfer.files[0]);
    }
  };

  // Text message sender
  const sendMessage = (textToSend) => {
    const query = textToSend || inputValue.trim();
    if (!query) return;

    if (query === '__upload_sample__') {
      processUploadedImage(sampleTowerSvg, "telecom_lattice_scan.svg");
      return;
    }

    const userMsg = { id: Date.now(), sender: 'user', type: 'text', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');

    setTimeout(() => {
      let aiReply = "I have reviewed your scan parameters. The structure demonstrates moderate degradation requiring schedule attention.";
      const lower = query.toLowerCase();

      if (lower.includes('tower type') || lower.includes('architecture')) {
        aiReply = "The AI vision model has classified this asset as a <strong>Supporting Lattice Tower</strong> (98.4% match confidence) with a 4-legged truss design.";
      } else if (lower.includes('defect') || lower.includes('found') || lower.includes('anomaly')) {
        aiReply = "Detected 3 anomalies: <br>• <strong>Surface Corrosion (96.4% conf.)</strong> at lower cross-brace.<br>• <strong>Missing Bolt Anomaly (88.2% conf.)</strong> on flange joint.<br>• Antenna mount alignment: Nominal.";
      } else if (lower.includes('maintenance') || lower.includes('schedule') || lower.includes('recommend')) {
        aiReply = "Recommended Action: <strong>Surface rust treatment & recoating within 30 days</strong>. Tighten flange bolts at structural elevation +14m.";
      } else if (lower.includes('health') || lower.includes('summary') || lower.includes('score')) {
        aiReply = "Overall Structural Integrity: <strong>74% / 100</strong> (Moderate). Safe for operational loading, but preventive recoating is required.";
      }

      setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'bot', type: 'text', text: aiReply }]);
    }, 500);
  };

  return (
    <>
      {/* Hidden File Input for in-chat image uploads */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileInputChange} 
        accept="image/*" 
        className="hidden" 
      />

      {/* Floating Circular Trigger */}
      <div 
        style={{
          position: 'fixed',
          left: position.x !== null ? `${position.x}px` : 'auto',
          top: position.y !== null ? `${position.y}px` : 'auto',
          right: position.x === null ? '24px' : 'auto',
          bottom: position.y === null ? '24px' : 'auto',
          zIndex: 50,
          cursor: 'grab'
        }}
        onMouseDown={handlePointerDown}
        onTouchStart={handlePointerDown}
        className="select-none touch-none"
      >
        <div className="w-14 h-14 rounded-full bg-emerald-600 text-white flex items-center justify-center text-2xl shadow-xl shadow-emerald-600/30 hover:scale-105 active:scale-95 transition-transform relative group">
          <span className="absolute inset-0 rounded-full border-2 border-emerald-400 animate-ping pointer-events-none opacity-40"></span>
          <span className="w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-white absolute top-0 right-0 shadow-sm"></span>
          <i className="ph-fill ph-robot"></i>
          
          <span className="absolute right-16 px-3 py-1.5 bg-slate-900 text-white text-xs font-semibold rounded-xl whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-lg">
            Drag to move • Click to chat
          </span>
        </div>
      </div>

      {/* Floating Chatbot Window */}
      {isOpen && (
        <div 
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`fixed bottom-20 right-6 ${
            isExpanded ? 'w-[480px] h-[640px]' : 'w-[410px] h-[540px]'
          } max-w-[calc(100vw-2rem)] max-h-[calc(100vh-6rem)] glass-modal rounded-3xl z-50 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200 text-slate-800 transition-all`}
        >
          {/* Header */}
          <div className="p-3.5 bg-white/60 backdrop-blur-md border-b border-white/80 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2.5">
              <StructiLogo size="sm" showText={false} />
              <div>
                <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  StructiAI Vision Copilot
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                </h4>
                <p className="text-[10px] text-slate-500 font-medium">In-Chat Structural Analysis & Vision</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <button 
                onClick={() => setIsExpanded(!isExpanded)} 
                title={isExpanded ? "Collapse" : "Expand"}
                className="w-7 h-7 rounded-lg bg-white hover:bg-slate-100 text-slate-500 hover:text-slate-800 flex items-center justify-center transition border border-slate-200 text-xs"
              >
                <i className={`ph ${isExpanded ? 'ph-arrows-in' : 'ph-arrows-out'}`}></i>
              </button>
              <button 
                onClick={() => setIsOpen(false)} 
                className="w-7 h-7 rounded-lg bg-white hover:bg-slate-100 text-slate-400 hover:text-slate-700 flex items-center justify-center transition border border-slate-200"
              >
                <i className="ph ph-caret-down text-xs font-bold"></i>
              </button>
            </div>
          </div>

          {/* Prompt Chips with Image Upload Button */}
          <div className="px-3 py-2 bg-slate-50/50 border-b border-slate-100 flex gap-1.5 overflow-x-auto text-[10px] flex-shrink-0">
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="px-2.5 py-1 rounded-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 whitespace-nowrap transition font-bold shadow-sm flex items-center gap-1"
            >
              <i className="ph-fill ph-camera-plus text-xs"></i>
              Upload Image
            </button>
            <button 
              onClick={() => sendMessage('__upload_sample__')}
              className="px-2.5 py-1 rounded-full bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap transition font-medium shadow-sm flex items-center gap-1"
            >
              <i className="ph ph-lightning text-xs text-amber-500"></i>
              Sample Scan
            </button>
            <button 
              onClick={() => sendMessage('What defects were found?')} 
              className="px-2.5 py-1 rounded-full bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap transition font-medium shadow-sm"
            >
              🔍 Defects
            </button>
            <button 
              onClick={() => sendMessage('What is the detected tower type?')} 
              className="px-2.5 py-1 rounded-full bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap transition font-medium shadow-sm"
            >
              🏷️ Tower Type
            </button>
          </div>

          {/* Drag Overlay Notice */}
          {isDragOver && (
            <div className="absolute inset-0 bg-emerald-600/90 text-white z-50 flex flex-col items-center justify-center p-6 text-center backdrop-blur-sm">
              <i className="ph-fill ph-cloud-arrow-up text-5xl mb-2 animate-bounce"></i>
              <h3 className="text-base font-bold">Drop Image to Inspect in Chat</h3>
              <p className="text-xs text-emerald-100 mt-1">AI will detect bounding boxes & structural quality immediately</p>
            </div>
          )}

          {/* Messages Area */}
          <div ref={chatBottomRef} className="flex-1 p-3.5 space-y-3.5 overflow-y-auto text-xs bg-slate-50/40">
            {messages.map(msg => (
              <div key={msg.id} className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'items-start'}`}>
                {msg.sender === 'bot' && (
                  <div className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs shrink-0 mt-0.5 font-bold shadow-sm">
                    <i className="ph-fill ph-robot"></i>
                  </div>
                )}

                {/* 1. Normal Text Message */}
                {msg.type === 'text' && (
                  <div 
                    className={`p-2.5 rounded-2xl leading-relaxed text-xs max-w-[85%] ${
                      msg.sender === 'user'
                        ? 'bg-emerald-600 text-white rounded-tr-none shadow-sm'
                        : 'bg-white text-slate-700 border border-slate-200 rounded-tl-none shadow-sm'
                    }`}
                    dangerouslySetInnerHTML={{ __html: msg.text }}
                  />
                )}

                {/* 2. User Image Upload Message */}
                {msg.type === 'image_upload' && (
                  <div className="bg-emerald-600 text-white rounded-2xl rounded-tr-none p-2.5 max-w-[85%] shadow-sm space-y-2">
                    <div className="relative rounded-xl overflow-hidden border border-emerald-400/40 max-h-40 bg-slate-900/20">
                      <img src={msg.imageSrc} alt="User upload" className="w-full h-auto object-contain max-h-36 mx-auto" />
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-emerald-100 pt-0.5">
                      <span className="font-semibold truncate max-w-[180px]"><i className="ph-fill ph-image mr-1"></i>{msg.fileName}</span>
                      <span className="bg-emerald-700/60 px-2 py-0.5 rounded text-[9px]">Uploaded</span>
                    </div>
                  </div>
                )}

                {/* 3. Bot Scanning State */}
                {msg.type === 'processing' && (
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-3.5 max-w-[90%] shadow-sm space-y-2.5">
                    <div className="flex items-center gap-2 text-emerald-700 font-bold text-xs">
                      <i className="ph ph-spinner-gap animate-spin text-base"></i>
                      <span>Running Neural Inspection...</span>
                    </div>
                    <div className="relative rounded-lg overflow-hidden bg-slate-900 border border-slate-200 max-h-32">
                      <img src={msg.imageSrc} alt="Processing" className="w-full h-28 object-contain opacity-50" />
                      <div className="absolute inset-0 bg-emerald-500/10 flex items-center justify-center">
                        <div className="w-full h-0.5 bg-emerald-400 shadow-[0_0_12px_#10b981] animate-pulse"></div>
                      </div>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-emerald-500 h-full rounded-full animate-pulse w-3/4"></div>
                    </div>
                    <p className="text-[10px] text-slate-500">Detecting corrosion, missing bolts & assessing quality...</p>
                  </div>
                )}

                {/* 4. Complete In-Chat Inspection Report Card */}
                {msg.type === 'inspection_report' && (
                  <InChatInspectionCard 
                    report={msg} 
                    onLoadToDashboard={onLoadToDashboard}
                  />
                )}

              </div>
            ))}
          </div>

          {/* Input Bar */}
          <div className="p-2.5 bg-white border-t border-slate-100 flex items-center gap-2 flex-shrink-0">
            {/* Attachment Button */}
            <button 
              type="button"
              onClick={() => fileInputRef.current?.click()}
              title="Upload image for inspection"
              className="w-8 h-8 rounded-xl bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 flex items-center justify-center transition border border-slate-200 shrink-0"
            >
              <i className="ph-fill ph-paperclip text-sm"></i>
            </button>

            {/* Input Box */}
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question or upload image..." 
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-500"
            />

            {/* Send Button */}
            <button 
              onClick={() => sendMessage()}
              className="w-8 h-8 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center active:scale-95 transition shrink-0 shadow-sm"
            >
              <i className="ph-fill ph-paper-plane-right text-xs"></i>
            </button>
          </div>
        </div>
      )}
    </>
  );
}

// Subcomponent: Complete Inspection Result Card Inside Chat Bubble
function InChatInspectionCard({ report, onLoadToDashboard }) {
  const [showBoxes, setShowBoxes] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'defects' | 'quality'

  return (
    <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-3 shadow-md max-w-[95%] space-y-3 text-slate-800">
      
      {/* Card Header & Classification */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center text-sm font-bold shadow-xs">
            <i className="ph-fill ph-broadcast"></i>
          </div>
          <div>
            <h5 className="font-bold text-xs text-slate-900">{report.tower_type}</h5>
            <p className="text-[9px] text-slate-500 font-medium">Confidence: <span className="text-emerald-700 font-bold">{report.tower_confidence}%</span></p>
          </div>
        </div>
        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[9px] font-bold px-2 py-0.5 rounded-full">
          AI Verified
        </span>
      </div>

      {/* Annotated Image with Bounding Box Overlay inside Chat */}
      <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-900 group">
        <img 
          src={report.imageSrc} 
          alt="Chat inspection scan" 
          className="w-full h-44 object-contain mx-auto"
        />

        {/* Dynamic Bounding Boxes */}
        {showBoxes && report.detections.map((det) => (
          <div
            key={det.id}
            style={{
              position: 'absolute',
              top: det.box.top,
              left: det.box.left,
              width: det.box.width,
              height: det.box.height,
              borderColor: det.color
            }}
            className="border-2 rounded-sm bg-white/10 transition-all pointer-events-auto"
          >
            <div 
              style={{ backgroundColor: det.color }} 
              className="absolute -top-5 left-0 text-white text-[8px] font-bold px-1.5 py-0.5 rounded-xs shadow-sm flex items-center gap-1 whitespace-nowrap uppercase tracking-wider"
            >
              <span>{det.class}</span>
              <span>{(det.confidence).toFixed(0)}%</span>
            </div>
          </div>
        ))}

        {/* Overlay Action Bar on Image */}
        <div className="absolute bottom-2 right-2 flex items-center gap-1.5 z-10">
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2 py-0.5 rounded-md text-[9px] font-bold backdrop-blur-md transition shadow-sm flex items-center gap-1 ${
              showBoxes 
                ? 'bg-slate-900/80 text-emerald-300 border border-emerald-500/40' 
                : 'bg-slate-900/80 text-slate-300 border border-slate-700'
            }`}
          >
            <i className={`ph ${showBoxes ? 'ph-eye' : 'ph-eye-slash'}`}></i>
            Boxes {showBoxes ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Internal Mini Tabs */}
      <div className="flex bg-slate-100 p-0.5 rounded-lg text-[10px] font-semibold text-slate-600">
        <button 
          onClick={() => setActiveTab('overview')} 
          className={`flex-1 py-1 rounded-md transition ${activeTab === 'overview' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'}`}
        >
          Overview
        </button>
        <button 
          onClick={() => setActiveTab('defects')} 
          className={`flex-1 py-1 rounded-md transition flex items-center justify-center gap-1 ${activeTab === 'defects' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'}`}
        >
          Defects <span className="bg-red-100 text-red-700 text-[8px] px-1 rounded-full font-bold">{report.detections.length}</span>
        </button>
        <button 
          onClick={() => setActiveTab('quality')} 
          className={`flex-1 py-1 rounded-md transition ${activeTab === 'quality' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'}`}
        >
          Quality
        </button>
      </div>

      {/* Tab 1: Overview & Health Score */}
      {activeTab === 'overview' && (
        <div className="space-y-2 text-[11px]">
          <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-100">
            <div>
              <span className="text-[10px] text-slate-500 font-medium">Structural Integrity Score</span>
              <p className="font-bold text-slate-900 text-xs">{report.health_status}</p>
            </div>
            <div className="text-right">
              <span className="text-sm font-black text-amber-600">{report.health_score}%</span>
            </div>
          </div>
          <div className="p-2 rounded-xl bg-emerald-50/60 border border-emerald-100 text-slate-700 text-[10px] leading-relaxed">
            <span className="font-bold text-emerald-800 block mb-0.5"><i className="ph-fill ph-check-circle mr-1"></i>AI Action Recommendation:</span>
            {report.recommendation}
          </div>
        </div>
      )}

      {/* Tab 2: Detected Anomaly Classes List */}
      {activeTab === 'defects' && (
        <div className="space-y-1.5 text-[10px]">
          {report.detections.map(det => (
            <div key={det.id} className="flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-100">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: det.color }}></span>
                <div>
                  <h6 className="font-bold text-slate-900">{det.class}</h6>
                  <p className="text-[9px] text-slate-500">{det.location}</p>
                </div>
              </div>
              <div className="text-right">
                <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold ${
                  det.severity === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                  det.severity === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                  'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {det.severity}
                </span>
                <span className="block text-[8px] text-slate-500 font-semibold mt-0.5">{det.confidence}% conf</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: 4-Metric Quality Assessment */}
      {activeTab === 'quality' && (
        <div className="grid grid-cols-2 gap-1.5 text-[10px]">
          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-500 text-[9px]">Sharpness</span>
              <span className="font-bold text-emerald-700">{report.qualityMetrics.sharpness}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report.qualityMetrics.sharpness}%` }}></div>
            </div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-500 text-[9px]">Color Acc.</span>
              <span className="font-bold text-emerald-700">{report.qualityMetrics.color}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report.qualityMetrics.color}%` }}></div>
            </div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-500 text-[9px]">Lighting</span>
              <span className="font-bold text-emerald-700">{report.qualityMetrics.lighting}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report.qualityMetrics.lighting}%` }}></div>
            </div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex justify-between items-center mb-1">
              <span className="text-slate-500 text-[9px]">Noise Level</span>
              <span className="font-bold text-emerald-700">{report.qualityMetrics.noise}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report.qualityMetrics.noise}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Action: Load to Main Dashboard Button */}
      {onLoadToDashboard && (
        <button
          onClick={() => onLoadToDashboard(report.imageSrc)}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition shadow-sm"
        >
          <i className="ph-fill ph-browsers text-sm"></i>
          Load into Main Dashboard
        </button>
      )}

    </div>
  );
}
