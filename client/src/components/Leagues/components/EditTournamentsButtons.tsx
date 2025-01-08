import React from "react";
import Button from "../../Utils/components/Button";
import { Tournament } from "../../../types/tournaments";
import axios from "axios";
import { useSettings } from "../state/settingsContext";
import { FantasyLeagueTournamentsResponse } from "../../../types/fantasyLeagueTournamentsResponse";

interface EditTournamentsButtonsProps {
    setTournaments: React.Dispatch<SetStateAction<FantasyLeagueTournamentsResponse | Tournament[] | undefined>>;
    fantasyLeagueSeasonId: string;
  }
  
  const EditTournamentsButtons: React.FC<EditTournamentsButtonsProps> = ({ setTournaments, fantasyLeagueSeasonId }) => {
    const { selectedTournaments, setSelectedTournaments } = useSettings(); // Assume setSelectedTournaments exists
  
    const addTournament = async () => {
      if (!selectedTournaments || selectedTournaments.size === 0) {
        alert("No tournaments selected for addition.");
        return;
      }
  
      try {
        const addedTournaments = await Promise.all(
          Array.from(selectedTournaments).map(async (tournamentId) => {
            const response = await axios.post(
              `/fantasy_league_seasons/${fantasyLeagueSeasonId}/tournaments`,
              { tournamentId } // Assuming API expects this structure
            );
            return response.data;
          })
        );
  
        setTournaments((prev) => [...prev, ...addedTournaments]);
        setSelectedTournaments(new Set()); // Clear selection after successful addition
      } catch (error) {
        console.error("Error adding tournaments:", error);
        alert("Failed to add one or more tournaments. Please try again.");
      }
    };
  
    const deleteTournament = async () => {
      if (!selectedTournaments || selectedTournaments.size === 0) {
        alert("No tournaments selected for deletion.");
        return;
      }
  
      try {
        await Promise.all(
          Array.from(selectedTournaments).map((tournamentId) =>
            axios.delete(
              `/fantasy_league_seasons/${fantasyLeagueSeasonId}/tournaments/${tournamentId}`
            )
          )
        );
  
        setTournaments((prev) =>
          prev.filter((tournament) => !selectedTournaments.has(tournament.id))
        );
        setSelectedTournaments(new Set()); // Clear selection after successful deletion
      } catch (error) {
        console.error("Error deleting tournaments:", error);
        alert("Failed to delete one or more tournaments. Please try again.");
      }
    };

  return (
    <div className="flex items-center justify-end space-x-2 p-1">
      <Button
        type="button"
        onClick={addTournament}
        size="md"
        variant="secondary"
        disabled={selectedTournaments.size === 0}
      >
        Add
      </Button>
      <Button
        type="button"
        onClick={deleteTournament}
        size="md"
        variant="primary"
        disabled={selectedTournaments.size === 0}
      >
        Remove
      </Button>
    </div>
  );
};

export default EditTournamentsButtons;