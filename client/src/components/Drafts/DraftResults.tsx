import React, { useState } from "react";
import BackButton from "../Utils/components/BackButton";
import NextButton from "../Utils/components/NextButton";
import { Golfer } from "../../types/golfers";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../store";
import ErrorPage from "../Utils/components/ErrorPage";
import PlayerData from "../Golfers/components/PlayerData";
import { setSelectedGolfer } from "../Golfers/state/golferSlice";
import { LeagueSettings } from "../../types/leagueSettings";
import { DraftPick } from "../../types/draftPicks";

type DraftResultsProps = {
  draftPicks: DraftPick[];
  draftOrder: string[]; // draft pick ids
  leagueSettings: LeagueSettings;
  rounds: number; // Number of draft rounds
};

const DraftResults: React.FC<DraftResultsProps> = ({
  draftPicks,
  draftOrder,
  rounds,
}) => {
  const [currentRound, setCurrentRound] = useState(1);

  const dispatch = useDispatch<AppDispatch>();

  const leagueSettings = useSelector((state: RootState) => state.leagues.selectedLeague!.LeagueSettings!);

  const leagueTeams = useSelector((state: RootState) => state.teams.leaguesTeams);

  const handleNextRound = () => {
    if (currentRound < rounds) setCurrentRound(currentRound + 1);
  };

  const handlePreviousRound = () => {
    if (currentRound > 1) setCurrentRound(currentRound - 1);
  };

  if (!leagueSettings) {
    return <ErrorPage message="League settings are not available." />;
  };

  const openGolferModal = (golferId: string) => {
    dispatch(setSelectedGolfer(golferId));
  };

  return (
    <div className="w-full h-screen overflow-auto flex items-center justify-center">
        <div className="w-2/3 bg-dark h-full overflow-auto text-light flex flex-col items-center px-4 py-6 mb-2 round-lg">
        {/* Header */}
        <div className="w-full max-w-5xl flex justify-between items-center bg-middle p-4 rounded-md shadow-lg">
            <div className="text-lg font-bold">Draft Results - Round {currentRound}</div>
            <div className="text-md">
            <span className="font-semibold">Teams:</span> {leagueSettings?.NumberOfTeams}
            </div>
        </div>

        {/* Round Navigation */}
        <div className="w-full max-w-5xl flex justify-between items-center my-4">
            <BackButton handleBackClick={handlePreviousRound} disabled={currentRound === 1} size={8} color="light" />
            <NextButton handleNextClick={handleNextRound} disabled={currentRound === rounds} size={8} color="light" />
        </div>

        {/* Draft Picks Overview */}
        <div className="w-full max-w-5xl bg-middle mt-4 p-4 rounded-md shadow-lg">
            <h2 className="text-lg font-semibold mb-3">Draft Picks Overview</h2>
            <div className="space-y-4">
            {draftPicks.map((draftPick) => (
                <div key={draftPick.id} className="bg-dark p-4 rounded-md shadow-md">
                <h3 className="text-md font-semibold mb-2">
                    {draftPick.team}
                </h3>
                {draftPicks?.length ? (
                    <div className="space-y-2">
                    {leagueSettings && leagueTeams
                        .filter((_golfer, index) => === currentRound)
                        .map((golfer, index) => (
                            <PlayerData
                            player={golfer}
                            even={index % 2 === 0}
                            onClick={() => openGolferModal(golfer.id)}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="text-center text-sm text-light">No picks for this team</div>
                )}
                </div>
            ))}
            </div>
        </div>

        {/* Graphs Placeholder */}
        <div className="w-full max-w-5xl bg-middle mt-6 p-4 rounded-md shadow-lg">
            <h2 className="text-lg font-semibold mb-3">Performance Graphs</h2>
            <div className="flex flex-wrap gap-4">
            {/* Placeholder for graphs */}
            <div className="flex-1 bg-dark p-4 rounded-md shadow-md">
                <h3 className="text-md font-semibold">Team Contribution</h3>
                <div className="h-40 flex justify-center items-center">
                {/* Add a graph component here */}
                <span className="text-sm text-light">Graph Placeholder</span>
                </div>
            </div>
            <div className="flex-1 bg-dark p-4 rounded-md shadow-md">
                <h3 className="text-md font-semibold">Golfer Performance</h3>
                <div className="h-40 flex justify-center items-center">
                {/* Add another graph component here */}
                <span className="text-sm text-light">Graph Placeholder</span>
                </div>
            </div>
            </div>
        </div>
        </div>
    </div>
  );
};

export default DraftResults;
