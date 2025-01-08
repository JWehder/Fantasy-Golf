import React from "react";
import TableRow from "../../Utils/components/TableRow";
import { Tournament } from "../../../types/tournaments";
import TableHeaders from "../../Utils/components/TableHeaders";
import { useSettings } from "../../Leagues/state/settingsContext";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../../../store";
import { setSelectedTournament } from "../state/tournamentsSlice";

interface TournamentScheduleTableProps {
    tournaments: Tournament[];
}

export default function TournamentScheduleTable({
    tournaments
}: TournamentScheduleTableProps) {
    const dispatch = useDispatch<AppDispatch>();

    const { settings, disabled, handleCheckboxChange, selectedTournaments } = useSettings();

    const desiredKeysSet = new Set(["PreviousWinner", "Purse"]);

    const headers = ["Date", "Tournament Name", "Purse", "Winner"];

    return (
        <>
            <div className="flex">
                { settings ?
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
                        { settings ?
                        <div className="w-10 flex justify-center items-center">
                            <input
                                type="checkbox"
                                checked={selectedTournaments?.has(tournament.id)}
                                onChange={() => handleCheckboxChange(tournament.id)}
                                className="cursor-pointer"
                                disabled={disabled}
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
                                    <span className="font-semibold text-md">{tournament.Name}</span>
                                    <span className="text-light text-xs">{`${tournament.City}, ${tournament.State}`}</span>
                                </div>,
                            ]}
                            data={tournament}
                            columns={desiredKeysSet}
                            brightness={idx % 2 === 0 ? "brightness-125" : ""}
                            onClick={() => dispatch(setSelectedTournament(tournament))}
                            disabled={false}
                        />
                    </div>
                )
            })}
        </>
    )
}