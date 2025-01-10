import React, { useState, useEffect } from 'react';

export default function NotificationBanner({ message, variant, timeout, onClose }) {
  const [isVisible, setIsVisible] = useState(true);

  // Helper method to convert seconds to milliseconds
  const secondsToMilliseconds = (seconds) => {
      if (typeof seconds === 'number') {
          return seconds * 1000;
      }
      return 0; // Default to 0 if no timeout is provided
  };

  useEffect(() => {
      console.log("Timeout in ms:", secondsToMilliseconds(timeout));
      if (timeout) {
          const timer = setTimeout(() => {
              console.log("Hiding the banner");
              setIsVisible(false); // Hide the banner after timeout
              if (onClose) onClose(); // Call onClose callback if provided
          }, secondsToMilliseconds(timeout)); // Convert seconds to milliseconds

          return () => clearTimeout(timer); // Cleanup timeout on component unmount
      }
  }, [timeout, onClose]);

  // Determine the background color based on the variant
  const getVariantStyle = () => {
      switch (variant) {
          case 'success':
              return 'bg-green-300';  
          case 'error':
              return 'bg-red-300'; 
          case 'warning':
              return 'bg-yellow-300'; 
          default:
              return 'bg-blue-300'; 
      }
  };

  if (!isVisible) return null;

  return (
      <div
          className={`${getVariantStyle()} text-dark px-2 py-2 rounded fixed left-1/2 top-6 transform -translate-x-1/2 w-11/12 md:w-1/3 shadow-lg z-50`}
      >
          <div className="flex items-center justify-between">
              <span className="text-sm px-0.5">{message}</span>
              <button
                  onClick={() => {
                      setIsVisible(false);
                      if (onClose) {
                          onClose();
                      }
                  }}
                  className="text-white hover:text-gray-200 focus:outline-none"
              >
                  ✕
              </button>
          </div>
      </div>
  );
}
