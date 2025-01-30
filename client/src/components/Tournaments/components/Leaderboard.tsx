import Tourney from "./Tourney";
import React, { useState } from "react";
import GolferTournamentDetailsTable from "./GolferTournamentDetailsTable";
import TournamentScheduleTable from "./TournamentScheduleTable";
import BackButton from "../../Utils/components/BackButton";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../store";
import { useFetchTournamentDetails } from "../../../hooks/tournaments"
import SkeletonTable from "../../Utils/components/SkeletonTable";
import { Tournament } from "../../../types/tournaments";

export default function Leaderboard() {
    const dispatch = useDispatch<AppDispatch>();

    const fantasyLeagueSeasonId = useSelector((state: RootState) => state.leagues.selectedLeague?.CurrentFantasyLeagueSeasonId)

    const [selectedTournament, setSelectedTournament] = useState<Tournament | null>(null);

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
                    {selectedTournament.CurrentRoundNum}
                    <GolferTournamentDetailsTable 
                    tournamentId={selectedTournament.id}
                    holeData={selectedTournament.Holes}
                    currentRoundNum={selectedTournament.CurrentRoundNum}
                    />
                </>
            :
                <>
                    { isError && <div>Error loading tournament details.</div> }
                    {isFetching && !isSuccess && !data?.tournaments?.length && <SkeletonTable />}
                    { isSuccess && 
                    <TournamentScheduleTable 
                    handleTournamentClick={(tournament) => setSelectedTournament(tournament)}
                    checkboxes={false}
                    disabledCheckboxes
                    tournaments={data?.tournaments!}
                    />
                    }
                </>
            }
        </div>
    )
}