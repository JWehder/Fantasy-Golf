import React from "react"

export default function THead({ datapoint }: { datapoint: number | string }) {
    return (
        <div className="font-bold text-xs w-8 flex-grow flex justify-center items-center flex-row flex-shrink overflow-hidden text-ellipsis whitespace-nowrap">
            {datapoint}
        </div>
    );
}