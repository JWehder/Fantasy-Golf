import React, { useState } from "react";
import BackButton from "../Utils/components/BackButton";
import NextButton from "../Utils/components/NextButton";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../store";
import ErrorPage from "../Utils/components/ErrorPage";
import PlayerData from "../Golfers/components/PlayerData";
import { setSelectedGolfer } from "../Golfers/state/golferSlice";
import { LeagueSettings } from "../../types/leagueSettings";
import { DraftPick } from "../../types/draftPicks";
import TableHeaders from "../Utils/components/TableHeaders";
import { useNavigate } from "react-router-dom";

type DraftResultsProps = {
  draftPicks: DraftPick[];
  draftOrder: string[]; // draft pick ids
  leagueSettings: LeagueSettings;
  rounds: number; // Number of draft rounds
};

const DraftResults: React.FC<DraftResultsProps> = ({
  draftPicks,
  rounds,
}) => {
  const [currentRound, setCurrentRound] = useState(1);

  const navigate = useNavigate();

  const handleBackToLeagueClick = () => {
      const leagueId = "66cfb58fcb1c3460e49138c2"; // Replace this with your actual league ID
      navigate(`/leagues/${leagueId}`);
  };

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

  const getTeamName = (teamId: string) => {
    const team = leagueTeams.find((team) => team.id === teamId);
    return team ? team.TeamName : "Unknown Team";
  };

  const headers = ["Fedex Rank", "Golfer", "Avg Score", "Top 10s", "Wins", "Cuts Made", "Fedex Pts"];

  return (
    <div className="w-full flex items-center justify-center min-w-[775px]">
        <div className="w-10/12 bg-dark text-light flex flex-col items-center mb-2 rounded-lg">
            {/* Header */}
            <div className="w-full flex justify-between items-center bg-middle p-4 rounded-lg shadow-lg">
                <BackButton 
                handleBackClick={handleBackToLeagueClick} 
                size={8} 
                color="light"
                message="Back"
                />
                <div className="text-lg font-bold">Draft Results - Round {currentRound}</div>
                <div className="text-md">
                <span className="font-semibold">Teams:</span> {leagueSettings?.NumberOfTeams}
                </div>
            </div>

            {/* Round Navigation */}
            <div className="w-full flex justify-between items-center my-2">
                <BackButton handleBackClick={handlePreviousRound} disabled={currentRound === 1} size={8} color="light" />
                <NextButton handleNextClick={handleNextRound} disabled={currentRound === rounds} size={8} color="light" />
            </div>

            {/* Draft Picks Overview */}
            <div className="w-full bg-middle mt-2 p-4 rounded-lg shadow-lg">
                <h2 className="text-lg font-semibold mb-3">
                    Draft Picks Overview
                </h2>
                <TableHeaders headers={headers} />
                <div className="space-y-4">
                    {draftPicks?.length ? (
                        <div className="space-y-2">
                        {leagueSettings && draftPicks
                            .filter((draftPick) => draftPick.RoundNumber === currentRound)
                            .map((pick, index) => (
                                <div key={`${getTeamName(pick.TeamId)} - ${pick.PickNumber}`}>
                                    <h3 className="text-md font-semibold p-2 border-b-2 border-light">
                                        {getTeamName(pick.TeamId)} - {pick.PickNumber}
                                    </h3>

                                    <PlayerData
                                    player={pick.Golfer}
                                    even={index % 2 === 0}
                                    onClick={() => openGolferModal(pick.Golfer.id)}
                                    />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center text-sm text-light">No picks for this team</div>
                    )}
                </div>
            </div>

            {/* Graphs Placeholder */}
            <div className="w-full bg-middle mt-6 p-4 rounded-lg shadow-lg">
                <h2 className="text-lg font-semibold mb-3">
                    Performance Graphs
                </h2>
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
