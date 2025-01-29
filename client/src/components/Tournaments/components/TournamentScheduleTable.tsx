import React, { useMemo } from "react";
import TableRow from "../../Utils/components/TableRow";
import { Tournament } from "../../../types/tournaments";
import TableHeaders from "../../Utils/components/TableHeaders";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch } from "../../../store";
import { setSelectedTournament } from "../state/tournamentsSlice";
import { RootState } from "../../../store";

interface TournamentScheduleTableProps {
    tournaments: Tournament[] | undefined;
    checkboxes: boolean;
    disabledCheckboxes?: boolean;
    handleCheckboxChange?: (tournamentId: string) => void;
    ongoingTournaments?: boolean;
    handleTournamentClick: (tournament: Tournament) => void;
}

export default function TournamentScheduleTable({
    tournaments,
    checkboxes,
    disabledCheckboxes,
    handleCheckboxChange,
    ongoingTournaments,
    handleTournamentClick
}: TournamentScheduleTableProps) {
    const dispatch = useDispatch<AppDispatch>();

    const desiredKeysSet = new Set(["PreviousWinner", "Purse"]);

    const headers = ["Date", "Tournament Name", "Purse", "Winner"];

    const selectedTournaments = useSelector(
        (state: RootState) => state.tournaments.selectedTournaments
      );
    
      // Memoize the Set conversion to optimize performance
    const selectedTournamentsSet = useMemo(() => new Set(selectedTournaments), [
        selectedTournaments,
    ]);

    return (
        <>
            <div className="flex">
                { checkboxes ?
                <div className="w-10" />
                :
                null
                }
                
                <TableHeaders headers={headers} />
            </div>

            { tournaments?.map((tournament: Tournament, idx) => {
                let newDesiredKeysSet = {};
                // Replace "PreviousWinner" with "Winner"
                if (desiredKeysSet.has("PreviousWinner")) {
                    desiredKeysSet.delete("PreviousWinner"); // Remove the old value
                    desiredKeysSet.add("Winner"); // Add the new value
                }
                return  (
                    <div className="flex items-center" key={tournament.id}>
                    {/* Checkbox Column */}
                        { checkboxes ?
                        <div className="w-10 flex justify-center items-center">
                            <input
                                type="checkbox"
                                checked={selectedTournamentsSet?.has(tournament.id)}
                                onChange={() => {
                                    if (handleCheckboxChange) {
                                        handleCheckboxChange(tournament.id)
                                    }
                                }}
                                className="cursor-pointer"
                                disabled={disabledCheckboxes}
                            />
                        </div>
                        :
                        null
                        }

                        {/* Table Row */}
                        <TableRow
                            firstTwoDatapoints={[
                                tournament.StartDate,
                                <div className="flex flex-col group-hover/team:translate-x-2 transition duration-200">
                                    <div className="flex items-center">
                                        <span className="font-semibold text-md">{tournament.Name}</span>
                                        { ongoingTournaments ? 
                                        <div className="ml-2 h-2 w-2 bg-red-400 rounded-full animate-pulse items-center justify-center flex"></div>
                                        :
                                        ""
                                        }
                                    </div>
                                <span className="text-light text-xs">{`${tournament.City}, ${tournament.State}`}</span>
                                </div>,
                            ]}
                            data={tournament}
                            columns={desiredKeysSet}
                            brightness={idx % 2 === 0 ? "brightness-125" : ""}
                            onClick={() => handleTournamentClick(tournament)}
                            disabled={false}
                        />
                    </div>
                )
            })}
        </>
    )
}