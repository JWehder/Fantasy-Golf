import React, { useState } from "react"
import TableRow from "../../Utils/components/TableRow"
import HolesComparisonChart from "./player/HolesComparisonChart"
import { GolferTournamentDetails } from "../../../types/golferTournamentDetails";
import { TournamentHoles } from "../../../types/tournamentHoles";

export default function GolferTournamentDetailsTd({ detail, desiredKeysSet, idx, holeData}: 
    {
        detail: GolferTournamentDetails, 
        idx: number, 
        desiredKeysSet: Set<string>,
        holeData: TournamentHoles[] 
    }) {
    
    const [showHolesComparisonChart, setShowHolesComparisonChart] = useState<Boolean>(false);

    return (
        <>
            <TableRow 
            firstTwoDatapoints={[detail.Position, detail.Name]}
            data={detail}
            columns={desiredKeysSet}
            brightness={idx % 2 === 0 ? 'brightness-125' : ''}
            onClick={() => setShowHolesComparisonChart(!showHolesComparisonChart)}
            disabled={false}
            />
            {showHolesComparisonChart && (
                <HolesComparisonChart
                    rounds={detail.Rounds}
                    holes={holeData}
                />
            )}
        </>
    )
}

