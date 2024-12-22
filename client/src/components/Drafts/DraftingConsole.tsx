import React, { useState, useEffect } from "react";
import TableRow from "../Utils/components/TableRow";
import Golfers from "../Golfers/components/Golfers";
import { LeagueSettings } from "../../types/leagueSettings";

type Golfer = {
  id: string;
  name: string;
  rank: number;
  points: number;
};

type DraftingConsoleProps = {
  availableGolfers: Golfer[];
  currentTeam: string;
  draftOrder: string[];
  draftPicks: Record<string, Golfer[]>;
  timeRemaining: number; // in seconds
  onDraft: (golfer: Golfer) => void;
  leagueSettings: LeagueSettings;
};

const DraftingConsole: React.FC<DraftingConsoleProps> = ({
  availableGolfers,
  currentTeam,
  draftOrder,
  draftPicks,
  timeRemaining,
  onDraft,
  leagueSettings,
}) => {
  const [timer, setTimer] = useState(timeRemaining);

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

  return (
    <div className="w-full min-h-screen bg-dark text-light flex flex-col items-center px-4 py-6">
      {/* Header */}
      <div className="w-full max-w-5xl flex justify-between items-center bg-middle p-4 rounded-md shadow-lg">
        <div className="text-lg font-bold">Drafting Console</div>
        <div className="text-md">
          <span className="font-semibold">Current Team:</span> {currentTeam}
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
                team === currentTeam ? "bg-light text-dark font-bold" : "bg-dark text-light"
              }`}
            >
              <div>Pick {index + 1}</div>
              <div>{team}</div>
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
              <Golfers />
          </div>
        </div>

        {/* Current Team */}
        <div className="flex-1 bg-middle p-4 rounded-md shadow-lg">
          <h2 className="text-lg font-semibold mb-3">Current Team Picks</h2>
          {draftPicks[currentTeam]?.length ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {draftPicks[currentTeam].map((golfer, index) => (
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
      </div>

      {/* Other Team Picks */}
      <div className="w-full max-w-5xl bg-middle mt-6 p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Other Teams' Picks</h2>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {Object.keys(draftPicks)
            .filter((team) => team !== currentTeam)
            .map((team) => (
              <div key={team} className="bg-dark p-3 rounded-md">
                <h3 className="text-md font-semibold mb-2">{team}</h3>
                <div className="flex flex-wrap gap-2">
                  {draftPicks[team].map((golfer, index) => (
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
