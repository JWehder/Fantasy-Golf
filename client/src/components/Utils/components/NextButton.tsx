import React from "react";

type NextButtonProps = {
  handleNextClick: () => void;
  size: number; // Size in pixels
  color: string; // TailwindCSS color class
  disabled?: boolean;
};

const NextButton: React.FC<NextButtonProps> = ({ handleNextClick, size, color, disabled }) => {
  const sizeClass = `w-${size} h-${size}`;
  const disabledClass = disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer";

  return (
    <div className={`min-w-12 max-w-64 ${disabledClass}`}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        className={`${sizeClass} mx-2 ${color} hover:brightness-125`}
        onClick={!disabled ? handleNextClick : undefined} // Prevent click if disabled
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H3"
        />
      </svg>
    </div>
  );
};

export default NextButton;
