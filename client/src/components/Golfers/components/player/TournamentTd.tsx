import { setHolesComparisonChart } from "../../../User/state/userSlice";
import HolesComparisonChart from "./HolesComparisonChart";
import React, { useState } from "react";
import { TournamentDetails } from "../../../../types/golferTournamentDetails";

export default function TournamentTd({ 
    golferDetails, 
    even, 
    desiredKeys }
    :
    {
    golferDetails: TournamentDetails,
    even: boolean,
    desiredKeys: Set<string>
    }) 
    {
    const [showHolesComparisonChart, setShowHolesComparisonChart] = useState<boolean | null>(false);

    const brightness = even ? 'brightness-125' : '';

    return (
        <>
            <div 
            onClick={() => setHolesComparisonChart(setShowHolesComparisonChart(!showHolesComparisonChart))}
            className={`w-full flex bg-middle h-10 justify-center items-center hover:z-20 cursor-pointer hover:shadow-lg shadow-middle flex-row border-box ${brightness} text-sm md:text-sm lg:text-md sm:text-sm truncate hover:b-1 my-1 overflow-visible border-x-2 border-middle`}>
                <div className="text-center flex w-3/6 items-center">
                    <div className="w-1/6 text-left px-2">
                        start date
                    </div>
                    <div className="w-5/6 text-left flex items-center pl-6">
                        <div className="flex justify-center">
                            {golferDetails.TournamentName}
                        </div>
                    </div>
                </div>
                <div className="flex w-3/6 flex-row items-center">
                {
                    Object.entries(golferDetails)
                        .filter(([key]) => desiredKeys.has(key))
                        .map(([key, value]) => (
                            <div key={key} className="flex flex-col w-6 flex-grow items-center justify-center px-3">
                                {value as React.ReactNode}
                            </div>
                        ))
                }
                </div>
            </div>
            { showHolesComparisonChart ?
                <HolesComparisonChart
                rounds={golferDetails.Rounds}
                />
                :
                ""
            }
            
        </>

    )
}