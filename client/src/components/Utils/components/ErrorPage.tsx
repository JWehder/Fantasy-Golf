import React from "react";

type ErrorPageProps = {
  message?: string;
  onRetry?: () => void; // Optional callback for retry actions
};

const ErrorPage: React.FC<ErrorPageProps> = ({
  message = "An unexpected error occurred.",
  onRetry,
}) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-dark text-light p-6">
      <h1 className="text-3xl font-bold mb-4">Error</h1>
      <p className="text-md text-gray-300 mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-md shadow"
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorPage;
