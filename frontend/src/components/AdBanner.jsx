import React from 'react';

export const AdBanner = ({ size = 'medium', label = 'Advertisement' }) => {
  const heights = { small: 'h-24', medium: 'h-48', large: 'h-72', wide: 'h-28' };
  return (
    <div className={`w-full ${heights[size]} bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-dashed border-purple-300 rounded-lg flex items-center justify-center my-4`}>
      <div className="text-center">
        <div className="text-xs uppercase tracking-widest text-purple-500 mb-1">{label}</div>
        <div className="text-purple-400 text-sm">Google AdSense Placeholder</div>
      </div>
    </div>
  );
};

export default AdBanner;
