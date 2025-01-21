import React from "react";
import Button from "../../Utils/components/Button";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../store";
import { addTournament } from "../state/tournamentsSlice";
import { deleteTournament } from "../state/tournamentsSlice";

interface EditTournamentsButtonsProps {
    fantasyLeagueSeasonId: string;
  }
  
  const EditTournamentsButtons: React.FC<EditTournamentsButtonsProps> = ({ fantasyLeagueSeasonId }) => {
    const dispatch = useDispatch<AppDispatch>();

    const selectedTournaments = useSelector((state: RootState) => state.tournaments.selectedTournaments)
  
    const handleAddTournamentClick = () => {
      if (!selectedTournaments || selectedTournaments.length === 0) {
        alert("No tournaments selected for addition.");
        return;
      };

      dispatch(addTournament({ selectedTournaments, fantasyLeagueSeasonId }))
    };
  
    const handleDeleteTournamentClick = async () => {
      if (!selectedTournaments || selectedTournaments.length === 0) {
        alert("No tournaments selected for deletion.");
        return;
      }

      dispatch(deleteTournament({ fantasyLeagueSeasonId, selectedTournaments }))

    }

  return (
    <div className="flex items-center justify-end space-x-2 p-1">
      <Button
        type="button"
        onClick={handleAddTournamentClick}
        size="md"
        variant="secondary"
        disabled={selectedTournaments.length === 0}
      >
        Add
      </Button>
      <Button
        type="button"
        onClick={handleDeleteTournamentClick}
        size="md"
        variant="primary"
        disabled={selectedTournaments.length === 0}
      >
        Remove
      </Button>
    </div>
  );
};

export default EditTournamentsButtons;