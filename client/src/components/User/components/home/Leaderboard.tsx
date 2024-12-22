import Tourney from "./Tourney";
import React, { useState } from "react";
import GolferTournamentDetailsTable from "../../../Golfers/components/GolferTournamentDetailsTable";
import TournamentScheduleTable from "./TournamentScheduleTable";
import { Tournament } from "../../../../types/tournaments";
import BackButton from "../../../Utils/components/BackButton";
import { useSelector } from "react-redux";
import { RootState } from "../../../../store";
import { useFetchTournamentDetails } from "../../../../hooks/tournaments"
import SkeletonTable from "../../../Utils/components/SkeletonTable";

export default function Leaderboard() {

    const [selectedTournament, setSelectedTournament] = useState<Tournament | null>(null);

    const fantasyLeagueSeasonId = useSelector((state: RootState) => state.leagues.selectedLeague?.CurrentFantasyLeagueSeasonId)

    const { data,
        isFetching,
        isSuccess,
        isError
    } = useFetchTournamentDetails(fantasyLeagueSeasonId);

    return (
        <div className="w-full h-full text-light font-PTSans p-4 bg-middle shadow-xl">
            { selectedTournament ?
                <>
                    <span className='inline-flex items-center'>
                        <BackButton 
                            size={8}
                            color={"stroke-light"} 
                            handleBackClick={() => setSelectedTournament(null)}
                        />
                    </span>
                    <Tourney 
                    tournament={selectedTournament}
                    />
                    <GolferTournamentDetailsTable 
                    tournamentId={selectedTournament.id}
                    holeData={selectedTournament.Holes}
                    />
                </>
            :
                <>
                    { isError && <div>Error loading tournament details.</div> }
                    {isFetching && !isSuccess && !data?.tournaments?.length && <SkeletonTable />}
                    { isSuccess && 
                    <TournamentScheduleTable 
                    setSelectedTournament={setSelectedTournament!}
                    tournaments={data?.tournaments!}
                    />
                    }
                </>
            }
        </div>
    )
}