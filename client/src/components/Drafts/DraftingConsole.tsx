import React, { useState, useEffect, useRef } from "react";
import Golfers from "../Golfers/components/Golfers";
import { LeagueSettings } from "../../types/leagueSettings";
import { useFetchAvailableTourneyGolfers } from "../../hooks/golfers";
import { setSelectedGolfer } from "../Golfers/state/golferSlice";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../store";
import { Team } from "../../types/teams";
import { DraftPick } from "../../types/draftPicks";

type Golfer = {
  id: string;
  name: string;
  rank: number;
  points: number;
};

type DraftingConsoleProps = {
  draftId: string;
  leagueId: string;
  tournamentId: string;
  draftOrder: Team[];
  draftPicks: DraftPick[];
  timeRemaining: number; // in seconds
  onDraft: (golfer: Golfer) => void;
  leagueSettings: LeagueSettings;
};

const DraftingConsole: React.FC<DraftingConsoleProps> = ({
  draftId,
  onDraft,
  leagueId,
  tournamentId,
  draftOrder,
  timeRemaining,
  draftPicks,
  leagueSettings,
}) => {

  const socketRef = useRef<WebSocket | null>(null);
  const [currentTeam, setCurrentTeam] = useState<Team>();

  const [currentRound, setCurrentRound] = useState<number>();
  const [currentPick, setCurrentPick] = useState<number>();

  const leaguesTeams = useSelector((state: RootState) => state.teams.leaguesTeams);

  // Handle draft pick
  const handleDraftPick = (golfer: Golfer) => {
    if (socketRef.current) {
      socketRef.current.send(
        JSON.stringify({
          event: "make_pick",
          team_id: currentTeam!.id,
          golfer_id: golfer.id,
          draft_id: draftId
        })
      );
    }
  };

  // Establish WebSocket connection
  useEffect(() => {
    const socket = new WebSocket(`/ws/${leagueId}`);
    socketRef.current = socket;

    // Handle incoming messages
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      // Handle different message events (player_drafted, current_pick, draft_complete)
      if (message.event === "player_drafted") {
        // Update draftPicks with the new draft data
        setTimer(message.timeRemaining)
        onDraft(message.draftPick)
        // Update your state with the new golfer information
      } else if (message.event === "current_pick") {
        setCurrentRound(message.round);
        setCurrentPick(message.pick);
        const currentTeam = leaguesTeams.find((team) => team.id === message.teamId);
        setCurrentTeam(currentTeam);
        // Update the UI to indicate the current team's pick
      } else if (message.event === "draft_complete") {
        console.log("Draft completed");
        // Handle draft completion logic
      }
    };

    // Handle connection close
    socket.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      socket.close();
    };
  }, [leagueId, handleDraftPick]);

  const [timer, setTimer] = useState(timeRemaining);

  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer((prev) => Math.max(prev - 1, 0));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Fetch available golfers
  const {
    data: golfersData,
    fetchNextPage: fetchNextGolferPage,
    hasNextPage: hasNextGolferPage,
    isFetchingNextPage: isFetchingNextGolferPage,
    isFetching: isFetchingGolfers,
    isError: isGolferError,
    error: golferError,
  } = useFetchAvailableTourneyGolfers(leagueId!, tournamentId!);

  // Map React Query data to match the expected prop structure
  const golfersPages = golfersData?.pages.map((page) => ({
    golfers: page.golfers,
    nextPage: page.nextPage,
  }));

  const handleGolferClick = (golfer: object) => {
    dispatch(setSelectedGolfer(golfer));
  };

  const onAddClick = (golferId: string) => {
    console.log(golferId);
  };

  const headers = ["Fedex Rank", "Golfer", "Avg Score", "Top 10s", "Wins", "Cuts Made", "Fedex Pts"];

  return (
    <div className="w-full min-h-screen bg-dark text-light flex flex-col items-center px-4 py-6">
      {/* Header */}
      <div className="w-full max-w-5xl flex justify-between items-center bg-middle p-4 rounded-md shadow-lg">
        <div className="text-lg font-bold">Drafting Console</div>
        <div className="text-md">
          <span className="font-semibold">Current Team:</span> {currentTeam?.TeamName}
        </div>
        <div className="text-md">
          <span className="font-semibold">Time Remaining:</span> {formatTime(timer)}
        </div>
      </div>

      {/* Draft Order */}
      <div className="w-full max-w-5xl bg-middle my-4 p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Draft Order</h2>
        <div className="flex overflow-x-auto space-x-4">
          {draftOrder.map((team, index) => (
            <div
              key={index}
              className={`flex flex-col items-center px-3 py-2 rounded-md ${
                team.TeamName === currentTeam?.TeamName ? "bg-light text-dark font-bold" : "bg-dark text-light"
              }`}
            >
              <div>Pick {index + 1}</div>
              <div>{team.TeamName}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Draft Area */}
      <div className="w-full max-w-5xl flex flex-col lg:flex-row gap-6">
        {/* Available Golfers */}
        <div className="flex-1 bg-middle p-4 rounded-md shadow-lg">
          <h2 className="text-lg font-semibold mb-3">Available Golfers</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            <Golfers
              headers={headers}
              data={golfersPages || []}
              isFetching={isFetchingGolfers}
              isFetchingNextPage={isFetchingNextGolferPage}
              hasNextPage={hasNextGolferPage}
              fetchNextPage={fetchNextGolferPage}
              onGolferClick={handleGolferClick}
              onAddClick={onAddClick}
            />
          </div>
        </div>
      </div>

      {/* Current Team */}
      <div className="flex-1 bg-middle p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Current Team Picks</h2>
        {draftPicks[currentTeam!]?.length ? (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {draftPicks[currentTeam!].map((golfer, index) => (
              <div key={index} className="flex justify-between items-center bg-dark p-2 rounded-md">
                <span>{golfer.name}</span>
                <span className="text-sm text-light">{golfer.points} pts</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-sm text-light">No picks yet</div>
        )}
      </div>

      {/* Other Team Picks */}
      <div className="w-full max-w-5xl bg-middle mt-6 p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Other Teams' Picks</h2>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {Object.keys(draftPicks!)
            .filter((team) => team !== currentTeam)
            .map((team) => (
              <div key={team} className="bg-dark p-3 rounded-md">
                <h3 className="text-md font-semibold mb-2">{team}</h3>
                <div className="flex flex-wrap gap-2">
                  {draftPicks![team].map((golfer, index) => (
                    <div
                      key={index}
                      className="bg-middle text-light px-3 py-1 rounded-md text-sm"
                    >
                      {golfer.name}
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default DraftingConsole;
