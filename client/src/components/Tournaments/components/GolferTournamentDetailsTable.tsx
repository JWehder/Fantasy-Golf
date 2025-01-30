import React from "react";
import TableHeaders from "../../Utils/components/TableHeaders";
import { useFetchAllTournamentDetails } from "../../../hooks/golferTournamentDetails";
import GolferTournamentDetailsTd from "../../Golfers/components/GolferTournamentDetailsTd";
import { TournamentHoles } from "../../../types/tournamentHoles";
import { useSelector } from "react-redux";
import { RootState } from "../../../store";
import SkeletonTable from "../../Utils/components/SkeletonTable";
import GolferTeeTimes from "../../Golfers/components/GolferTeeTimes";

export default function GolferTournamentDetailsTable(
    { tournamentId, holeData, currentRoundNum } : 
    {
        tournamentId: string,
        holeData: TournamentHoles[],
        currentRoundNum: string
    
    }) {

    const { data,
    isFetching,
    isSuccess,
    isError } = useFetchAllTournamentDetails(tournamentId);

    const tournamentHeaders = ["place", "golfer name", "position", "r1", "r2", "r3", "r4", "strokes", "score", "fedex pts"];

    // Set of keys to display with fallback support
    const desiredKeysSet = new Set(["Position", "R1", "R2", "R3", "R4", "TotalStrokes", "Score", "FedexPts"]);

    const leaguesGolferTournamentDetailsIds = useSelector((state: RootState) => {
        return state.golfers.leaguesGolfersTournamentDetailsIds
    });

    return (
        <div className="bg-middle rounded-xl text-light overflow-auto">
        { data?.roundsExist ?
            <TableHeaders 
            headers={tournamentHeaders}
            />
            :
            ""
        }
        {data?.roundsExist ? (
            isSuccess && data?.details && (
                leaguesGolferTournamentDetailsIds ? (
                    // Filter by IDs present in leaguesGolferTournamentDetailsIds
                    data.details
                        .filter((detail) => leaguesGolferTournamentDetailsIds.has(detail.id))
                        .map((detail, idx) => (
                            <GolferTournamentDetailsTd 
                                key={detail.id}  // Always include a key when mapping
                                detail={detail}
                                desiredKeysSet={desiredKeysSet}
                                holeData={holeData}
                                idx={idx}
                            />
                        ))
                ) : (
                    // Render without filtering if leaguesGolferTournamentDetailsIds is not available
                    data.details.map((detail, idx) => (
                        <GolferTournamentDetailsTd 
                            key={detail.id}
                            detail={detail}
                            desiredKeysSet={desiredKeysSet}
                            holeData={holeData}
                            idx={idx}
                        />
                    ))
                )
            )
        ) : (
            isSuccess && data?.details && (
                <GolferTeeTimes
                    golfers={data.details}
                    currentRoundNum={currentRoundNum}
                />
            )
        )}


        { isError && <div>Error loading tournament details.</div> }
        { isFetching && <SkeletonTable /> }
    </div>
    )
}