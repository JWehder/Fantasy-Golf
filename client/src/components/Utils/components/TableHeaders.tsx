import React from "react"
import THead from "./THead"

export default function TableHeaders({ headers } : { headers: string[] }) {

    return (
        <div className="w-full flex bg-middle text-xs truncate font-bold p-2 items-center text-clip border-b border-light">
            <div className="text-center flex w-1/2">
                <div className="w-1/6">
                    {headers[0]}
                </div>
                <div className="w-5/6">
                    {headers[1]}
                </div>
            </div>
            <div className="flex w-1/2 flex-row bg-middle">
                {headers?.slice(2).map((header: string, idx: number) => {
                    return <THead 
                    key={`${header}-${idx}`}
                    datapoint={header}
                    />
                })}
            </div>
        </div>
    )
}