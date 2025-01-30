import React from "react";
import TData from "../../Utils/components/TData";

interface GolferTeeTimesProps {
    onClick: () => void;
    golferName: string;
    teeTime: string;
    even: boolean;
}

export default function GolferTeeTimesRows(
    { onClick, golferName, teeTime, even }
    :
    GolferTeeTimesProps
    ) {
    return (
        <div 
        onClick={onClick} // Disable click when disabled is true
        className={`w-full flex bg-middle h-10 justify-center items-center flex-row border-box text-sm md:text-sm lg:text-md sm:text-sm truncate my-0.5 overflow-visible border-x-2 border-middle font-PTSans hover:b-1 text-light ${even ? 'brightness-125': ''} cursor-pointer hover:z-20 hover:shadow-lg`} // Apply styles based on disabled
        >
            {/* Left side: Name */}
            <div className="flex w-1/2 flex-row items-center">
                    <TData>
                        {golferName}
                    </TData>
            </div>
            {/* Right side: Tee Times */}
            <div className="flex w-1/2 flex-row items-center brightness-125">
                <TData>
                    {teeTime}
                </TData>
            </div>
        </div>
    )
}