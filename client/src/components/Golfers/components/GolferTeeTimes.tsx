import React from "react"

export default function GolferTeeTimes() {

    return (
        <div 
        onClick={!disabled ? onClick : undefined} // Disable click when disabled is true
        className={`w-full flex bg-middle h-10 justify-center items-center flex-row border-box ${brightness} text-sm md:text-sm lg:text-md sm:text-sm truncate my-0.5 overflow-visible border-x-2 border-middle font-PTSans 
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:z-20 hover:shadow-lg hover:b-1'}`} // Apply styles based on disabled
        >
            {/* Right side: Dynamic columns */}
            <div className="flex w-1/2 flex-row items-center">
                {Array.from(columns)?.map((col, idx) => (
                    <TData key={idx}>
                        {data[col] ?? "--"}
                    </TData>
                ))}
            </div>
        </div>
    )
}