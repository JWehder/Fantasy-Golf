import React from "react";

type BackButtonProps = {
  handleBackClick: () => void;
  size: number; // Size in pixels
  color: string; // TailwindCSS color class
  disabled?: boolean;
};

const BackButton: React.FC<BackButtonProps> = ({ handleBackClick, size, color, disabled }) => {
  const sizeClass = `w-${size} h-${size}`;
  const disabledClass = disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer hover:translate-x-[-5px]";

  return (
    <div className={`min-w-12 max-w-64 ${disabledClass}`}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        className={`${sizeClass} mx-2 ${color} hover:brightness-125`}
        onClick={!disabled ? handleBackClick : undefined} // Prevent click if disabled
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M6.75 15.75L3 12m0 0l3.75-3.75M3 12h18"
        />
      </svg>
    </div>
  );
};

export default BackButton;
