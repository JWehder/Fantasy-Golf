import { Tournament } from "./tournaments"

export interface FantasyLeagueTournamentsResponse {
    currentProSeasonTournaments?: Array<Tournament>,
    pastFantasyLeagueTournaments?: Array<Tournament>,
    upcomingFantasyLeagueTournaments?: Array<Tournament>,
    upcomingProSeasonTournaments?: Array<Tournament>,
    allTournaments?: Array<Tournament>
}