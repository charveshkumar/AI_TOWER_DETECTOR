import React, { useState, useRef, useEffect } from 'react';

export default function NotificationDropdown({ showToast, onViewScan }) {
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all' | 'alerts' | 'system'
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "Critical Corrosion Detected",
      description: "Surface rust (>96.4% confidence) detected on lower cross-brace of Lattice Tower #TWR-408.",
      type: "alert",
      severity: "critical",
      time: "Just now",
      read: false,
      towerId: "TWR-408"
    },
    {
      id: 2,
      title: "Missing Flange Bolt Alert",
      description: "Bolt absence identified at structural joint elevation +14.2m on asset #TWR-102.",
      type: "alert",
      severity: "high",
      time: "12m ago",
      read: false,
      towerId: "TWR-102"
    },
    {
      id: 3,
      title: "AI Neural Scan Completed",
      description: "Inspection scan for Monopole #TWR-892 completed with 91% Structural Integrity Score.",
      type: "system",
      severity: "success",
      time: "1h ago",
      read: true,
      towerId: "TWR-892"
    },
    {
      id: 4,
      title: "Image Refining Model v2.4 Active",
      description: "AI HD edge calibration filters and sharpness enhancements updated successfully.",
      type: "system",
      severity: "info",
      time: "3h ago",
      read: true
    }
  ]);

  const dropdownRef = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    if (showToast) {
      showToast("Notifications Marked", "All notifications have been marked as read.", "info");
    }
  };

  const handleNotificationClick = (item) => {
    setNotifications(prev => prev.map(n => n.id === item.id ? { ...n, read: true } : n));
    if (item.towerId && onViewScan) {
      onViewScan(item.towerId, "Supporting Lattice Tower");
    } else if (showToast) {
      showToast(item.title, item.description, item.severity === 'critical' ? 'error' : 'info');
    }
    setIsOpen(false);
  };

  const removeNotification = (e, id) => {
    e.stopPropagation();
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const filteredNotifications = notifications.filter(item => {
    if (filter === 'alerts') return item.type === 'alert';
    if (filter === 'system') return item.type === 'system';
    return true;
  });

  const triggerTestAlert = () => {
    const newId = Date.now();
    const newAlert = {
      id: newId,
      title: "New Structural Anomaly Detected",
      description: "Fresh automated drone inspection found micro-cracks on Guyed Mast #TWR-773.",
      type: "alert",
      severity: "critical",
      time: "Just now",
      read: false,
      towerId: "TWR-773"
    };
    setNotifications(prev => [newAlert, ...prev]);
    if (showToast) {
      showToast(newAlert.title, newAlert.description, "error");
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Notification Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        title="Inspection Notifications"
        className={`relative w-10 h-10 rounded-xl flex items-center justify-center transition border ${
          isOpen
            ? 'bg-emerald-50 text-emerald-700 border-emerald-300 shadow-sm'
            : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 shadow-xs'
        }`}
      >
        <i className="ph-fill ph-bell text-xl"></i>

        {/* Unread Counter Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-600 text-white text-[10px] font-bold flex items-center justify-center shadow-sm border-2 border-white animate-pulse">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Floating Notification Popover Menu with Glassmorphism */}
      {isOpen && (
        <div className="absolute right-0 mt-3 w-96 max-w-[calc(100vw-2rem)] glass-modal rounded-2xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150 text-slate-800">
          
          {/* Header */}
          <div className="p-4 bg-white/60 backdrop-blur-md border-b border-white/80 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold">
                <i className="ph-fill ph-bell"></i>
              </div>
              <h3 className="font-bold text-sm text-slate-900">Notifications</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-bold text-[10px]">
                  {unreadCount} New
                </span>
              )}
            </div>
            
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-[11px] font-semibold text-emerald-700 hover:text-emerald-800 transition"
              >
                Mark all read
              </button>
            )}
          </div>

          {/* Filter Tabs */}
          <div className="px-3 pt-2 pb-2 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
            <div className="flex gap-1 text-[11px] font-medium">
              <button
                onClick={() => setFilter('all')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  filter === 'all' ? 'bg-white font-bold text-slate-900 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                All ({notifications.length})
              </button>
              <button
                onClick={() => setFilter('alerts')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  filter === 'alerts' ? 'bg-white font-bold text-slate-900 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Alerts ({notifications.filter(n => n.type === 'alert').length})
              </button>
              <button
                onClick={() => setFilter('system')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  filter === 'system' ? 'bg-white font-bold text-slate-900 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                System ({notifications.filter(n => n.type === 'system').length})
              </button>
            </div>

            <button 
              onClick={triggerTestAlert}
              title="Simulate incoming alert"
              className="text-[10px] font-bold text-emerald-700 hover:bg-emerald-50 px-2 py-1 rounded-md transition flex items-center gap-1 border border-emerald-200"
            >
              <i className="ph-fill ph-plus-circle text-xs"></i>
              Simulate Alert
            </button>
          </div>

          {/* Notification Items List */}
          <div className="max-h-[340px] overflow-y-auto divide-y divide-slate-100 text-xs">
            {filteredNotifications.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                <i className="ph ph-bell-slash text-3xl mb-2 block"></i>
                <p className="font-medium text-xs">No notifications found</p>
              </div>
            ) : (
              filteredNotifications.map(item => (
                <div
                  key={item.id}
                  onClick={() => handleNotificationClick(item)}
                  className={`p-3.5 hover:bg-slate-50 cursor-pointer transition flex gap-3 items-start group relative ${
                    !item.read ? 'bg-emerald-50/30' : 'bg-white'
                  }`}
                >
                  {/* Severity Icon Indicator */}
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-base shrink-0 mt-0.5 ${
                    item.severity === 'critical' ? 'bg-red-100 text-red-600' :
                    item.severity === 'high' ? 'bg-amber-100 text-amber-600' :
                    item.severity === 'success' ? 'bg-emerald-100 text-emerald-600' :
                    'bg-blue-100 text-blue-600'
                  }`}>
                    <i className={
                      item.severity === 'critical' ? 'ph-fill ph-warning-octagon' :
                      item.severity === 'high' ? 'ph-fill ph-warning' :
                      item.severity === 'success' ? 'ph-fill ph-check-circle' :
                      'ph-fill ph-info'
                    }></i>
                  </div>

                  {/* Content */}
                  <div className="flex-1 pr-4">
                    <div className="flex items-center justify-between mb-0.5">
                      <h4 className={`text-xs ${!item.read ? 'font-bold text-slate-900' : 'font-semibold text-slate-700'}`}>
                        {item.title}
                      </h4>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-2">
                      {item.description}
                    </p>
                    <div className="flex items-center justify-between mt-1.5 text-[10px]">
                      <span className="text-slate-400 font-medium">{item.time}</span>
                      {item.towerId && (
                        <span className="text-emerald-700 font-bold group-hover:underline flex items-center gap-0.5">
                          Inspect Scan <i className="ph ph-arrow-right"></i>
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Dismiss / Delete Button */}
                  <button
                    onClick={(e) => removeNotification(e, item.id)}
                    title="Dismiss"
                    className="opacity-0 group-hover:opacity-100 absolute top-3 right-3 text-slate-400 hover:text-slate-700 w-5 h-5 flex items-center justify-center rounded-md hover:bg-slate-200 transition"
                  >
                    <i className="ph ph-x text-xs"></i>
                  </button>

                  {/* Unread dot */}
                  {!item.read && (
                    <span className="absolute top-4 right-3 group-hover:opacity-0 w-2 h-2 rounded-full bg-emerald-500"></span>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-2.5 bg-slate-50 border-t border-slate-100 text-center">
            <span className="text-[10px] text-slate-400 font-medium">
              StructiVision Real-Time Sensor & Vision Alerts
            </span>
          </div>

        </div>
      )}
    </div>
  );
}
