import React from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../../store";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { ChartOptions } from "chart.js";
import TableHeaders from "../../Utils/components/TableHeaders";
import TeamData from "./TeamData";
import { Team } from "../../../types/teams";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const NewStandings = ({ changeUserSelectedTeam } : 
  { changeUserSelectedTeam: (team: Team) => void}) => {

  const selectedLeagueTeams = useSelector((state: RootState) => state.teams.leaguesTeams) || []

  // Preparing data for Chart.js
  const chartData = {
    labels: selectedLeagueTeams?.map((team) => team.TeamName) || [], // Team names as labels
    datasets: [
      {
        label: "Total Points",
        data: selectedLeagueTeams?.map((team) => team.Points) || [], // Points data
        backgroundColor: [
          "#4CAF50",
          "#FF9800",
          "#03A9F4",
          "#E91E63",
          "#FFC107",
          "#9C27B0",
        ],
        borderColor: "#FFF",
        borderWidth: 1,
      },
    ],
  };

  const chartOptions: ChartOptions<"bar"> = {
    responsive: true,
    plugins: {
      legend: {
        position: "top", // Use a valid string literal here
        labels: {
          color: "#FFF",
        },
      },
      tooltip: {
        backgroundColor: "#333",
        titleColor: "#FFF",
        bodyColor: "#FFF",
      },
    },
    scales: {
      x: {
        ticks: {
          color: "#FFF",
        },
        grid: {
          display: false,
        },
      },
      y: {
        ticks: {
          color: "#FFF",
        },
        grid: {
          color: "#555",
        },
      },
    },
  };
  
  const headers = ["Place", "Team", "Score", "Top 10s", "Missed Cuts", "Wins"]

  return (
    <div className="w-full min-h-screen bg-dark text-light flex flex-col items-center font-PTSans">

      {/* League Standings Table */}
      <div className="w-full max-w-5xl bg-middle my-4 p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Team Rankings</h2>
        <div className="w-full flex items-center justify-center">
          <button 
          className="rounded-full bg-light text-dark font-PTSans p-2 text-xs boreder-dark border-2 hover:bg-light/90"
          >
            current period
          </button>
        </div>
        <TableHeaders headers={headers} />
        {selectedLeagueTeams.map((team, index) => (
          <TeamData 
          key={team.id}
          even={index % 2 == 0} 
          team={team} 
          onClick={() => changeUserSelectedTeam(team)} 
          />
        ))}
      </div>

      {/* Standings Visualization */}
      <div className="w-full max-w-5xl bg-middle p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">Performance Overview</h2>
        <div className="w-full h-96">
          <Bar data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Notes or Additional Data */}
      <div className="w-full max-w-5xl bg-middle mt-6 p-4 rounded-md shadow-lg">
        <h2 className="text-lg font-semibold mb-3">League Insights</h2>
        <div className="text-sm text-light">
          Stay tuned for upcoming features and updates about your league!
        </div>
      </div>
    </div>
  );
};

export default NewStandings;
