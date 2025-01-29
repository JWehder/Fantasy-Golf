import React from "react";

export default function TData({ children }) {
    return (
        <div className="flex flex-col items-center justify-center w-8 text-center flex-grow text-xs lg:text-md md:text-sm sm:text-sm font-PTSans">
            {children}
        </div>
    )
}